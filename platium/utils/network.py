import requests
import time
from platium.core.config import config
from platium.core.errors import NetworkError, APILimitError
from platium.utils.url_validation import is_safe_url

def safe_request(url, headers=None, timeout=None, retries=3, backoff=1):
    """
    Безпечний HTTP-запит з перевіркою URL на SSRF.
    """
    if not is_safe_url(url):
        raise NetworkError(f"Blocked SSRF attempt: {url}")

    headers = headers or {}
    timeout = timeout or config.timeout

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
    return None
