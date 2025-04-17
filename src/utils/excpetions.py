from requests import HTTPError

class RateLimitException(HTTPError):
    pass
