import requests
import time
from platium.core.errors import NetworkError, APILimitError

def safe_request(url, headers=None, timeout=10, retries=3, backoff=1):
    headers = headers or {}
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                raise APILimitError("Rate limited")
            if resp.status_code >= 500:
                raise NetworkError(f"Server error {resp.status_code}")
            return resp
        except requests.exceptions.Timeout:
            if attempt == retries - 1:
                raise NetworkError("Timeout")
            time.sleep(backoff * (attempt + 1))
        except requests.exceptions.ConnectionError:
            if attempt == retries - 1:
                raise NetworkError("Connection error")
            time.sleep(backoff * (attempt + 1))
