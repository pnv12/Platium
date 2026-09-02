"""
Social Analyzer — аналіз соцмереж
"""

import requests
import json

def search(username):
    """Аналізує профіль у соцмережах"""
    results = {}
    
    # Твіттер (публічні дані)
    try:
        response = requests.get(f"https://nitter.net/{username}", timeout=5)
        if response.status_code == 200:
            results["twitter"] = "Профіль існує"
        else:
            results["twitter"] = "Не знайдено"
    except:
        results["twitter"] = "Помилка"
    
    # Інстаграм (публічні дані)
    try:
        response = requests.get(f"https://www.instagram.com/{username}/", timeout=5)
        if response.status_code == 200:
            results["instagram"] = "Профіль існує"
        else:
            results["instagram"] = "Не знайдено"
    except:
        results["instagram"] = "Помилка"
    
    return results
