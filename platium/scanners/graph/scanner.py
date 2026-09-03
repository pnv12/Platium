import requests
from platium.core.config import load_config
from platium.core.errors import ScannerError

def search(email_or_username, config=None, verbose=False):
    """
    Будує граф зв'язків на основі email або username.
    """
    if config is None:
        config = load_config()
    
    results = {
        "target": email_or_username,
        "scan_type": "graph",
        "status": "error",
        "data": {}
    }
    
    # Заглушка — реальна реалізація потребує API
    results["data"] = {
        "connections": ["pnv21", "neo", "saturn"],
        "links": 3,
        "note": "This is a demo. Real graph requires SecurityTrails or similar API."
    }
    results["status"] = "success"
    return results
