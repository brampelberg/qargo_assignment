from datetime import datetime
import logging
from typing import Deque, Dict, List
from pydantic import UUID4
from domain.unavailability_groups import UnavailabilityGroups
from domain.unavailability_sync_plan import UnavailabilitySyncPlan
from models.unavailability import Unavailability
from qargo_api_client import master_qargo_api_client, target_qargo_api_client

logger = logging.getLogger(__name__)

class SynchronisationService:

    _start_time: datetime

    def __init__(self, start_time: datetime):
        self._start_time = start_time

    def synchronize_unavailabilities(self):
        logger.info("Loading resources...")
        resource_ids = self._load_resource_ids()
        logger.info(f"Loaded {len(resource_ids)} resources.")
        
        logger.info("Loading unavailabilities for resources...")
        unavailability_groups_by_resource_id = self._load_unavailabilities_for_resources(resource_ids)
        logger.info("Finished loading unavailabilities.")
        
        for resource_id, unavailability_groups in unavailability_groups_by_resource_id.items():
            logger.info(f"Determining sync plan for resource {resource_id}...")
            sync_plan = self._determine_unavailability_sync_plan(unavailability_groups=unavailability_groups)

            logger.info(f"Executing sync plan actions for resource {resource_id}...")
            self._execute_unavailability_sync_plan_for_resource(resource_id, sync_plan)
            logger.info(f"Finished executing sync plan actions for resource {resource_id}.")
        logger.info("Synchronisation complete!")

    def _load_resource_ids(self) -> List[UUID4]:
        try:
            resources = target_qargo_api_client.get_resources()
            return [resource.id for resource in resources]
        except Exception as e:
            logging.exception(f"Failed to load resources: {e}")
            raise e

    def _load_unavailabilities_for_resources(self, resource_ids: List[UUID4]) -> Dict[UUID4, UnavailabilityGroups]:
        try:
            return {
            resource_id: (
                lambda target_unavailabilities, master_unavailabilities: UnavailabilityGroups(
                    target_unavailabilities_with_external_id= {
                        u.external_id: u for u in target_unavailabilities if u.external_id
                    },
                    target_unavailabilities_without_external_id={
                        str(u.id): u for u in target_unavailabilities if not u.external_id
                    },
                    master_unavailabilities={
                        str(u.id): u for u in master_unavailabilities
                    },
                )
            )(
                target_qargo_api_client.get_unavailabilities(resource_id, self._start_time),
                master_qargo_api_client.get_unavailabilities(resource_id, self._start_time),
            )
            for resource_id in resource_ids
        }
        except Exception as e:
            logging.exception("Failed to unavailabilities for resources. {e}")
            raise e
    
    def _determine_unavailability_sync_plan(self, unavailability_groups: UnavailabilityGroups) -> UnavailabilitySyncPlan:
        master_unavailabilities = unavailability_groups.master_unavailabilities
        target_unavailabilities_by_external_id = unavailability_groups.target_unavailabilities_with_external_id

        unavailabilities_to_create: Deque[Unavailability] = Deque()
        unavailabilities_to_update: Deque[Unavailability] = Deque()
        logger.debug(f"Adding {len(unavailability_groups.target_unavailabilities_without_external_id)} target unavailabilities for deletion initially.")
        unavailabilities_to_delete: Deque[Unavailability] = Deque(unavailability_groups.target_unavailabilities_without_external_id.values())

        handled_target_ids: set[str] = set()

        # Go through master unavailabilities
        logger.debug(f"Processing {len(master_unavailabilities)} master unavailabilities...")
        for master_unavailability_id, master_unavailability in master_unavailabilities.items():
            # Try to find a corresponding target unavailability based on external_id
            target_unavailability = target_unavailabilities_by_external_id.get(master_unavailability_id)
            if not target_unavailability:
                logger.debug(f"Plan: Add CREATE for master_unavailability_id: {master_unavailability_id}")
                # If there is no target unavailability found, it means it needs to be created
                unavailabilities_to_create.append(master_unavailability.model_copy(update={"external_id": str(master_unavailability.id)}))
            # If one is found but not equal, it needs to be updated and then added to the handled unavailabilities
            elif not master_unavailability.equals(target_unavailability):
                logger.debug(f"Plan: Add UPDATE for master_unavailability_id: {master_unavailability_id} (Target ID: {target_unavailability.id})")
                unavailabilities_to_update.append(master_unavailability.model_copy(update={"id": target_unavailability.id}))
                handled_target_ids.add(master_unavailability_id)
            # If one is found and equal, it just needs to be added to the handled unavailabilities
            else:
                logger.debug(f"Plan: No change needed for master_unavailability_id: {master_unavailability_id} (Target ID: {target_unavailability.id})")
                handled_target_ids.add(master_unavailability_id)

        # Any left over target unavailabilities could not be matched with a master unavailability, which means they need to be deleted
        logger.debug(f"Checking {len(target_unavailabilities_by_external_id)} target items with external_id for deletion...")
        for target_external_id, target_unavailability in target_unavailabilities_by_external_id.items():
            if target_external_id not in handled_target_ids:
                logger.debug(f"Plan: Add DELETE for external_id: {target_external_id} (Target ID: {target_unavailability.id})")
                unavailabilities_to_delete.append(target_unavailability)

        logger.debug("="*80)
        logger.debug("Sync plan:")
        logger.debug("="*80)
        logger.debug(f"Availabilities to create: {unavailabilities_to_create}")
        logger.debug("="*80)
        logger.debug(f"Availabilities to update: {unavailabilities_to_update}")
        logger.debug("="*80)
        logger.debug(f"Availabilities to delete: {unavailabilities_to_delete}")
        logger.debug("="*80)

        return UnavailabilitySyncPlan(
                to_create=unavailabilities_to_create,
                to_update=unavailabilities_to_update,
                to_delete=unavailabilities_to_delete,
            )
    
    def _execute_unavailability_sync_plan_for_resource(self, resource_id: UUID4, unavailability_sync_plan: UnavailabilitySyncPlan):
        self._create_unavailabilities_for_resource(resource_id, unavailability_sync_plan.to_create)
        self._update_unavailabilities_for_resource(resource_id, unavailability_sync_plan.to_update)
        self._delete_unavailabilities_for_resource(resource_id, unavailability_sync_plan.to_delete)

    def _create_unavailabilities_for_resource(self, resource_id: UUID4, unavailabilities: Deque[Unavailability]):
        failure_count: int = 0
        for unavailability in unavailabilities:
            if not target_qargo_api_client.create_unavailability(resource_id=resource_id, unavailability=unavailability):
                logger.warning(f"Failed to create unavailability {unavailability} for resource {resource_id}")
                failure_count += 1
        if failure_count > 0:
            logger.warning(f"Failed to create {failure_count} unavailabilities.")

    def _update_unavailabilities_for_resource(self, resource_id: UUID4, unavailabilities: Deque[Unavailability]):
        failure_count: int = 0
        for unavailability in unavailabilities:
            if not target_qargo_api_client.update_unavailability(resource_id=resource_id, unavailability=unavailability):
                logger.warning(f"Failed to update unavailability {unavailability} for resource {resource_id}")
                failure_count += 1
        if failure_count > 0:
            logger.warning(f"Failed to update {failure_count} unavailabilities.")

    def _delete_unavailabilities_for_resource(self, resource_id: UUID4, unavailabilities: Deque[Unavailability]):
        failure_count: int = 0
        for unavailability in unavailabilities:
            if not target_qargo_api_client.delete_unavailability(resource_id=resource_id, id=unavailability.id):
                logger.warning(f"Failed to delete unavailability {unavailability} for resource {resource_id}")
                failure_count += 1
        if failure_count > 0:
            logger.warning(f"Failed to delete {failure_count} unavailabilities.")
