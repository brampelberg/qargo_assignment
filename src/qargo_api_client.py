from datetime import datetime, timezone, timedelta
from http import HTTPMethod
from typing import Any, Dict, List, Optional
import logging
from pydantic import UUID4, ValidationError
import requests
from dtos.resource_list_dto import ResourceListDto
from dtos.unavailability_dto import UnavailabilityDto
from dtos.unavailability_list_dto import UnavailabilityListDto
from dtos.unavailability_post_dto import UnavailabilityPostDto
from dtos.unavailability_put_dto import UnavailabilityPutDto
from models.resource import Resource
from models.unavailability import Unavailability
from utils.excpetions import RateLimitException
from utils.utils import get_env_var, with_exponential_backoff

logger = logging.getLogger(__name__)

class QargoAPIClient:
    _api_client_id: str
    _api_client_secret: str
    _api_url: str
    _session: requests.Session
    _access_token: Optional[str] = None
    _access_token_expiry_time: Optional[datetime] = None
    
    def __init__(self, api_client_id: str, api_client_secret: str, api_url: str):
        if not api_client_id or not api_client_secret:
            raise ValueError("API client id and secret are required.")
        self._api_client_id = api_client_id
        self._api_client_secret = api_client_secret
        self._api_url = api_url
        self._session = requests.Session()

    @with_exponential_backoff()
    def _call_api(self, method: HTTPMethod, 
                  uri: str, 
                  params: Optional[Dict[str,str | None]] = None, 
                  body: Dict[str, Any] = {}, 
                  headers: Dict[str,str] = {}) -> requests.Response:
        access_token = self._get_valid_access_token()

        response = self._session.request(method=method.value, url=self._api_url+uri, params=params, data=body, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            **headers
        },)

        if response.status_code == 429:
                raise RateLimitException(f"Rate limit exceeded: {response.reason}")
        response.raise_for_status()

        return response

    @with_exponential_backoff(max_retries= 3, base_delay= 4.0)
    def _fetch_access_token(self):
        url = f"{self._api_url}/auth/token"
        logger.info(f"Request access token from {url}")
        try:
            response = self._session.post(url= url,
                            auth= (self._api_client_id, self._api_client_secret),
                            headers={"Accept": "application/json"})
            
            if response.status_code == 429:
                raise RateLimitException(f"Rate limit exceeded: {response.reason}")
            response.raise_for_status()

            data = response.json()

            if 'access_token' not in data or 'expires_in' not in data:
                    logger.error("access_token or expires_in not found in token response.")
                    raise ValueError("Invalid token response received.")

            self._access_token = data["access_token"]
            self._access_token_expiry_time = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])

        except ValueError as e:
            logger.exception(f"Error parsing response {e}")
            raise e

    def _get_valid_access_token(self):
        if (self._access_token == None 
            or self._access_token_expiry_time == None 
            or self._access_token_expiry_time <= datetime.now(timezone.utc)):
            self._fetch_access_token()
        if (self._access_token == None):
            raise ConnectionError("Unable to fetch access token.")
        return self._access_token

    def get_resources(self):
        all_resources: List[Resource] = []
        next_cursor: Optional[str] = None
        page_number = 1

        while True:
            try:
                response = self._call_api(method=HTTPMethod.GET, uri= "/resources/resource", params= {"cursor": next_cursor})

                json = response.json()
                resource_list_dto = ResourceListDto.model_validate(json)

                all_resources.extend([Resource.from_resource_dto(dto) for dto in resource_list_dto.items])

                if resource_list_dto.next_cursor:
                    next_cursor = resource_list_dto.next_cursor
                    page_number += 1
                else:
                    break
                
            except requests.exceptions.RequestException as e:
                logger.exception(f"Error requesting resources: {e}")
                raise e
            except ValidationError as e:
                logger.exception(f"Error parsing ResourceListDto: {e}")
                raise e
            except Exception as e:
                logger.exception(f"Unexpected exception: {e}")
                raise e
        logger.info(f"Successfully retrieved a total of {len(all_resources)} resources across {page_number} page(s).")
        return all_resources
    
    def get_unavailabilities(self, resource_id: UUID4, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Unavailability]:
        all_unavailabilities: List[Unavailability] = []
        next_cursor: Optional[str] = None
        page_number = 1

        while True:
            try:
                response = self._call_api(method=HTTPMethod.GET, 
                                          uri= f"/resources/resource/{str(resource_id)}/unavailability", 
                                          params= {"cursor": next_cursor, 
                                                   **({"start_time": start_time.isoformat()} if start_time else {}),
                                                   **({"end_time": end_time.isoformat()} if end_time else {})})

                json = response.json()
                unavailability_list_dto = UnavailabilityListDto.model_validate(json)

                all_unavailabilities.extend([Unavailability.from_unavailability_dto(dto) for dto in unavailability_list_dto.items])

                if unavailability_list_dto.next_cursor:
                    next_cursor = unavailability_list_dto.next_cursor
                    page_number += 1
                else:
                    break
                
            except requests.exceptions.RequestException as e:
                logger.exception(f"Error requesting unavailabilities: {e}")
                raise e
            except ValidationError as e:
                logger.exception(f"Error parsing UnavailabilityListDto: {e}")
                raise e
            except Exception as e:
                logger.exception(f"Unexpected exception: {e}")
                raise e
        logger.info(f"Successfully retrieved a total of {len(all_unavailabilities)} unavailabilities across {page_number} page(s).")
        return all_unavailabilities
    
    def create_unavailability(self, resource_id: UUID4, unavailability: Unavailability) -> bool:
        try:
            unavailability_post_dto = UnavailabilityPostDto.from_unavailability(unavailability=unavailability)
            logger.debug(unavailability_post_dto.model_dump_json())
            response = self._call_api(method=HTTPMethod.POST, 
                                      uri= f"/resources/resource/{str(resource_id)}/unavailability",
                                      body=unavailability_post_dto.model_dump_json())

            json = response.json()
            UnavailabilityDto.model_validate(json)
            return True
        
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error posting unavailability: {e}")
        except ValidationError as e:
            logger.exception(f"Error parsing UnavailabilityDto: {e}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected exception: {e}")
        return False
    
    def update_unavailability(self, resource_id: UUID4, unavailability: Unavailability) -> bool:
        try:
            unavailability_put_dto = UnavailabilityPutDto.from_unavailability(unavailability=unavailability)
            response = self._call_api(method=HTTPMethod.PUT, 
                                      uri= f"/resources/resource/{str(resource_id)}/unavailability/{str(unavailability.id)}",
                                      body=unavailability_put_dto.model_dump())
            json = response.json()
            UnavailabilityDto.model_validate(json)
            return True
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error updating unavailability: {e}")
        except ValidationError as e:
            logger.exception(f"Error parsing UnavailabilityDto: {e}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected exception: {e}")
        return False
    
    def delete_unavailability(self, id: UUID4, resource_id: UUID4) -> bool:
        try:
            self._call_api(method=HTTPMethod.DELETE, 
                                      uri= f"/resources/resource/{str(resource_id)}/unavailability/{str(id)}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error deleting unavailability: {e}")
        except Exception as e:
            logger.exception(f"Unexpected exception: {e}")
        return False
    

target_qargo_api_client = QargoAPIClient(
    api_client_id=get_env_var("API_CLIENT_ID"),
    api_client_secret=get_env_var("API_CLIENT_SECRET"),
    api_url=get_env_var("API_URL")
)

master_qargo_api_client = QargoAPIClient(
    api_client_id=get_env_var("MASTER_API_CLIENT_ID"),
    api_client_secret=get_env_var("MASTER_API_CLIENT_SECRET"),
    api_url=get_env_var("API_URL")
)

    