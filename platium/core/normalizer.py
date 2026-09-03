from datetime import datetime

def normalize_results(raw, scan_type, target):
    results = []
    for source, data in raw.items():
        results.append({
            "target": target,
            "scan_type": scan_type,
            "source": source,
            "status": "found" if data.get("found") else "not_found",
            "confidence": 0.9 if data.get("found") else 0.0,
            "data": data.get("data", {}),
            "url": data.get("url"),
            "timestamp": datetime.now().isoformat(),
            "error": data.get("error")
        })
    return results
