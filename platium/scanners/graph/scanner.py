from platium.core.result import ScanResult, ScanStatus
from platium.core.config import config
from platium.scanners.username.scanner import search as username_search
from platium.scanners.email.scanner import search as email_search
from platium.scanners.phone.scanner import search as phone_search
from platium.scanners.ip.scanner import search as ip_search

def search(query, verbose=False) -> ScanResult:
    """
    Будує граф зв'язків на основі результатів інших сканерів.
    Повертає ScanResult.
    """
    scanners = {
        "username": username_search,
        "email": email_search,
        "phone": phone_search,
        "ip": ip_search
    }

    results = {}
    errors = []
    sources = {}
    data = {"nodes": [], "edges": []}
    status = ScanStatus.NOT_FOUND

    for name, scanner in scanners.items():
        try:
            result = scanner(query, verbose)
            results[name] = result
            sources[name] = result.to_dict()
            if result.is_found():
                if status != ScanStatus.SUCCESS:
                    status = ScanStatus.SUCCESS
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
            sources[name] = {"status": "error", "message": str(e)}

    # Будуємо граф з отриманих даних
    nodes = [{"id": query, "type": "target", "label": query}]
    edges = []

    for scanner_name, result in results.items():
        if not result.is_found():
            continue
        result_data = result.data
        if not result_data:
            continue

        if scanner_name == "username":
            for platform, info in result_data.items():
                if isinstance(info, dict) and info.get("status") == "found":
                    node_id = f"{platform}:{query}"
                    nodes.append({"id": node_id, "type": "platform", "label": platform})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "has_profile_on",
                        "confidence": 0.9,
                        "evidence": info.get("url", "")
                    })

        elif scanner_name == "email":
            for source_name, source_data in result_data.items():
                if isinstance(source_data, dict) and source_data.get("status") == "success":
                    node_id = f"breach:{source_name}"
                    nodes.append({"id": node_id, "type": "breach", "label": source_name})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "appears_in_breach",
                        "confidence": 0.85,
                        "evidence": f"Found in {source_name}"
                    })

        elif scanner_name == "phone":
            phone_data = result_data.get("data", {})
            if phone_data.get("country"):
                country = phone_data["country"]
                node_id = f"country:{country}"
                nodes.append({"id": node_id, "type": "country", "label": country})
                edges.append({
                    "source": query,
                    "target": node_id,
                    "relation": "located_in",
                    "confidence": 0.95,
                    "evidence": f"Phone registered in {country}"
                })
            if phone_data.get("operator"):
                operator = phone_data["operator"]
                node_id = f"operator:{operator}"
                nodes.append({"id": node_id, "type": "operator", "label": operator})
                edges.append({
                    "source": query,
                    "target": node_id,
                    "relation": "uses_operator",
                    "confidence": 0.95,
                    "evidence": f"Phone uses {operator}"
                })

        elif scanner_name == "ip":
            location = result_data.get("location", {})
            if location.get("country"):
                country = location["country"]
                node_id = f"country:{country}"
                nodes.append({"id": node_id, "type": "country", "label": country})
                edges.append({
                    "source": query,
                    "target": node_id,
                    "relation": "connected_to",
                    "confidence": 0.9,
                    "evidence": f"IP located in {country}"
                })

    # Видаляємо дублікати вузлів
    seen = set()
    unique_nodes = []
    for node in nodes:
        if node["id"] not in seen:
            seen.add(node["id"])
            unique_nodes.append(node)

    data["nodes"] = unique_nodes
    data["edges"] = edges
    data["node_count"] = len(unique_nodes)
    data["edge_count"] = len(edges)

    if len(unique_nodes) > 1:
        status = ScanStatus.SUCCESS
    elif errors:
        status = ScanStatus.PARTIAL

    return ScanResult(
        target=query,
        scanner="graph",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.9 if status == ScanStatus.SUCCESS else 0.1,
        evidence=[f"Built graph with {len(unique_nodes)} nodes and {len(edges)} edges"]
    )
