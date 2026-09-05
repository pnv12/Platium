from platium.utils.http_client import get_http_client

def safe_request(url, headers=None, timeout=10, retries=3, backoff=1):
    """
    Безпечний HTTP-запит з використанням нового HTTPClient.
    """
    client = get_http_client()
    try:
        return client.get(url, headers=headers, retries=retries, backoff=backoff)
    except Exception:
        return None
