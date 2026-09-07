import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        load_dotenv() 

        self.api_id = int(os.getenv("API_ID", 0))
        self.api_hash = os.getenv("API_HASH", "")

        self.timeout = int(os.getenv("TIMEOUT", 10))
        self.user_agent = os.getenv("USER_AGENT", "Mozilla/5.0")
        self.max_workers = int(os.getenv("MAX_WORKERS", 20))
        self.cache_ttl = int(os.getenv("CACHE_TTL", 300))
        
        self.shodan_key = os.getenv("SHODAN_API_KEY")
        self.virustotal_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY")
        self.ipinfo_key = os.getenv("IPINFO_API_KEY")
        self.hibp_key = os.getenv("HIBP_API_KEY") 

        self.proxies = os.getenv("PROXIES", "").split(",") if os.getenv("PROXIES") else []

        self._critical_keys = {
            "API_ID": self.api_id,
            "API_HASH": self.api_hash,
        }
        logger.info("Configuration loaded successfully.")

    def get_api_key(self, key_name: str) -> str:
        key = getattr(self, key_name, "")
        if not key:
            logger.warning(f"API key '{key_name}' is missing or empty.")
        return key

    def has_valid_api_key(self, key_name: str) -> bool:
        return bool(getattr(self, key_name, ""))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_id and self.api_hash)

config = Config()

def load_config():
    return {
        "timeout": config.timeout,
        "user_agent": config.user_agent,
        "max_workers": config.max_workers,
        "cache_ttl": config.cache_ttl,
        "shodan_key": config.shodan_key,
        "virustotal_key": config.virustotal_key,
        "abuseipdb_key": config.abuseipdb_key,
        "ipinfo_key": config.ipinfo_key,
        "hibp_key": config.hibp_key,
    }

def get_user_agent():
    return config.user_agent
