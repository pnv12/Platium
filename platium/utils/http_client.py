"""
HTTP Client з кешуванням, пулом з'єднань, таймаутами та retry
"""

import time
import hashlib
import json
import requests
from functools import lru_cache
from platium.core.config import load_config

class HTTPClient:
    def __init__(self):
        config = load_config()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.get("user_agent", "Mozilla/5.0")})
        # Пул з'єднань
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.cache = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 хвилин за замовчуванням
        self.timeout = config.get("timeout", 10)

    def get(self, url, params=None, headers=None, use_cache=True, retries=3, backoff=1):
        """Виконує GET-запит з кешуванням та retry"""
        cache_key = self._get_cache_key(url, params, headers)
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data

        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                if response.status_code in (429, 500, 502, 503, 504):
                    wait = backoff * (2 ** attempt)
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                # Кешуємо результат
                if use_cache:
                    self.cache[cache_key] = (response, time.time())
                return response
            except requests.exceptions.Timeout:
                if attempt == retries - 1:
                    raise
                time.sleep(backoff * (2 ** attempt))
            except requests.exceptions.RequestException:
                if attempt == retries - 1:
                    raise
                time.sleep(backoff * (2 ** attempt))
        return None

    def post(self, url, data=None, json=None, headers=None, retries=3, backoff=1):
        """Виконує POST-запит з retry"""
        for attempt in range(retries):
            try:
                response = self.session.post(
                    url,
                    data=data,
                    json=json,
                    headers=headers,
                    timeout=self.timeout
                )
                if response.status_code in (429, 500, 502, 503, 504):
                    wait = backoff * (2 ** attempt)
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                if attempt == retries - 1:
                    raise
                time.sleep(backoff * (2 ** attempt))
            except requests.exceptions.RequestException:
                if attempt == retries - 1:
                    raise
                time.sleep(backoff * (2 ** attempt))
        return None

    def _get_cache_key(self, url, params, headers):
        """Генерує унікальний ключ для кешу"""
        key = url
        if params:
            key += json.dumps(params, sort_keys=True)
        if headers:
            key += json.dumps(headers, sort_keys=True)
        return hashlib.md5(key.encode()).hexdigest()

    def clear_cache(self):
        """Очищує кеш"""
        self.cache.clear()

# Глобальний екземпляр
_http_client = None

def get_http_client():
    global _http_client
    if _http_client is None:
        _http_client = HTTPClient()
    return _http_client
