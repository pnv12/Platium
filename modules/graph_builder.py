"""
Graph Builder — побудова графу зв'язків
"""

import requests
import json

def build(email):
    """Будує граф зв'язків на основі email"""
    results = {}
    try:
        # 1. Пошук за email через публічні джерела (заглушка)
        results["connections"] = ["pnv21", "neo", "saturn", "john_doe"]
        results["links"] = 3
        results["email"] = email
        results["source"] = "public databases"
    except Exception as e:
        results["error"] = str(e)
    
    return results
