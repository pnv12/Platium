import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        "timeout": int(os.getenv("TIMEOUT", 10)),
        "user_agent": os.getenv("USER_AGENT", "Mozilla/5.0"),
        "cache_ttl": int(os.getenv("CACHE_TTL", 300)),  # 5 хвилин
        "max_workers": int(os.getenv("MAX_WORKERS", 20)),
        "shodan_key": os.getenv("SHODAN_API_KEY"),
        "virustotal_key": os.getenv("VIRUSTOTAL_API_KEY"),
        "abuseipdb_key": os.getenv("ABUSEIPDB_API_KEY"),
        "ipinfo_key": os.getenv("IPINFO_API_KEY"),
    }

def get_user_agent():
    return load_config()["user_agent"]
