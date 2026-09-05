"""
Graph Scanner — побудова графу зв'язків на основі результатів інших сканерів
"""

from platium.core.result import ScanResult, ScanStatus
from platium.core.config import load_config
from platium.scanners.username.scanner import search as username_search
from platium.scanners.email.scanner import search as email_search
from platium.scanners.phone.scanner import search as phone_search
from platium.scanners.ip.scanner import search as ip_search

def search(query, config=None, verbose=False) -> ScanResult:
    """
    Будує граф зв'язків для заданої цілі на основі даних з інших сканерів.
    Використовує результати username, email, phone, ip сканерів для побудови зв'язків.
    """
    if config is None:
        config = load_config()

    # Збираємо дані з усіх сканерів
    scanners = {
        "username": username_search,
        "email": email_search,
        "phone": phone_search,
        "ip": ip_search
    }

    results = {}
    errors = []
    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND

    # Запускаємо всі сканери для отримання даних
    for name, scanner in scanners.items():
        try:
            result = scanner(query, config, verbose)
            results[name] = result
            sources[name] = result.to_dict()
            if result.is_found():
                data[name] = result.data
                if status != ScanStatus.SUCCESS:
                    status = ScanStatus.SUCCESS
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
            sources[name] = {"status": "error", "message": str(e)}

    # Будуємо граф на основі отриманих даних
    nodes = []
    edges = []

    # Додаємо ціль як головний вузол
    nodes.append({"id": query, "type": "target", "label": query})

    # Проходимо по кожному сканеру і додаємо вузли та зв'язки
    for scanner_name, result in results.items():
        if not result.is_found():
            continue

        # Отримуємо дані з результату
        result_data = result.data
        if not result_data:
            continue

        # Якщо це username scanner — додаємо знайдені платформи
        if scanner_name == "username":
            for platform, info in result_data.items():
                if info.get("status") == "found":
                    node_id = f"{platform}:{query}"
                    nodes.append({"id": node_id, "type": "platform", "label": platform})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "has_profile_on",
                        "confidence": 0.9,
                        "evidence": info.get("url", "")
                    })

        # Якщо це email scanner — додаємо утечки
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

        # Якщо це phone scanner — додаємо інформацію про оператора
        elif scanner_name == "phone":
            phone_data = result_data.get("data", {})
            if phone_data:
                country = phone_data.get("country")
                operator = phone_data.get("operator")
                if country:
                    node_id = f"country:{country}"
                    nodes.append({"id": node_id, "type": "country", "label": country})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "located_in",
                        "confidence": 0.95,
                        "evidence": f"Phone number registered in {country}"
                    })
                if operator:
                    node_id = f"operator:{operator}"
                    nodes.append({"id": node_id, "type": "operator", "label": operator})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "uses_operator",
                        "confidence": 0.95,
                        "evidence": f"Phone number uses {operator}"
                    })

        # Якщо це ip scanner — додаємо геолокацію
        elif scanner_name == "ip":
            ip_data = result_data.get("location", {})
            if ip_data:
                country = ip_data.get("country")
                city = ip_data.get("city")
                isp = ip_data.get("isp")
                if country:
                    node_id = f"country:{country}"
                    nodes.append({"id": node_id, "type": "country", "label": country})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "connected_to",
                        "confidence": 0.9,
                        "evidence": f"IP located in {country}"
                    })
                if city:
                    node_id = f"city:{city}"
                    nodes.append({"id": node_id, "type": "city", "label": city})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "located_in_city",
                        "confidence": 0.85,
                        "evidence": f"IP located in {city}"
                    })
                if isp:
                    node_id = f"isp:{isp}"
                    nodes.append({"id": node_id, "type": "isp", "label": isp})
                    edges.append({
                        "source": query,
                        "target": node_id,
                        "relation": "uses_isp",
                        "confidence": 0.85,
                        "evidence": f"IP uses {isp}"
                    })

    # Видаляємо можливі дублікати вузлів
    seen_nodes = set()
    unique_nodes = []
    for node in nodes:
        node_id = node.get("id")
        if node_id not in seen_nodes:
            seen_nodes.add(node_id)
            unique_nodes.append(node)

    # Формуємо результат
    graph_data = {
        "nodes": unique_nodes,
        "edges": edges,
        "node_count": len(unique_nodes),
        "edge_count": len(edges)
    }

    # Визначаємо статус на основі наявності даних
    if len(unique_nodes) > 1:  # є хоча б одна зв'язок
        status = ScanStatus.SUCCESS
    elif errors:
        status = ScanStatus.PARTIAL
    else:
        status = ScanStatus.NOT_FOUND

    # Створюємо результат
    result = ScanResult(
        target=query,
        scanner="graph",
        status=status,
        data=graph_data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.9 if status == ScanStatus.SUCCESS else 0.1,
        evidence=[f"Built graph with {len(unique_nodes)} nodes and {len(edges)} edges"]
    )

    return result
