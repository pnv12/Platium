"""
Graph Scanner — побудова графу зв'язків на основі результатів інших сканерів
"""

from platium.core.config import load_config
from platium.core.errors import ScannerError

def search(query, config=None, verbose=False):
    """
    Будує граф зв'язків для заданої цілі на основі даних з інших сканерів.
    Якщо даних недостатньо — повертає порожній граф.
    """
    if config is None:
        config = load_config()

    result = {
        "target": query,
        "scan_type": "graph",
        "nodes": [],
        "edges": [],
        "status": "empty"
    }

    # Це місце для реальної логіки побудови графу.
    # Поки що ми не маємо доступу до результатів інших сканерів,
    # тому повертаємо порожній граф, але без фейкових даних.
    # У майбутньому тут буде виклик інших сканерів і побудова зв'язків.

    # Якщо немає даних — статус empty
    result["status"] = "empty"
    result["nodes"] = []
    result["edges"] = []

    # Додамо інформацію про те, що це не фейк, а просто поки що порожньо
    if verbose:
        result["info"] = "No data available for graph construction yet"

    return result
