"""
Display — функції для красивого та професійного виводу в CLI
"""

import sys
import time
from enum import Enum

class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

def colorize(text: str, color: Color) -> str:
    """Додає колір до тексту"""
    return f"{color.value}{text}{Color.RESET.value}"

def status_label(status: str) -> str:
    """Повертає кольоровий статус"""
    status_map = {
        "success": colorize("✓", Color.GREEN),
        "found": colorize("✓", Color.GREEN),
        "not_found": colorize("✗", Color.RED),
        "error": colorize("✗", Color.RED),
        "partial": colorize("~", Color.YELLOW),
        "rate_limited": colorize("⌛", Color.YELLOW),
        "skipped": colorize("⏭", Color.CYAN),
        "invalid": colorize("✗", Color.RED),
        "timeout": colorize("⌛", Color.RED),
        "unknown": colorize("?", Color.DIM)
    }
    return status_map.get(status, status)

def print_header(text: str, color: Color = Color.CYAN):
    """Друк заголовка"""
    print(colorize("=" * 60, color))
    print(colorize(f" {text}", color))
    print(colorize("=" * 60, color))

def print_result_table(results: dict, title: str = "Results"):
    """Друк результатів у вигляді таблиці"""
    print_header(title)
    for source, data in results.items():
        status = data.get("status", "unknown")
        status_str = status_label(status)
        url = data.get("url", "N/A")
        msg = data.get("message", data.get("error", ""))
        print(f"  {source:20} {status_str} {url}")
        if msg and msg != "N/A":
            print(f"    {colorize(msg, Color.DIM)}")
    print()

def print_scan_result(result):
    """Друк результату сканування з кольором"""
    status = result.status.value
    status_str = status_label(status)
    print(f"\n[+] Results for {result.scanner}:")
    print(f"  Status: {status_str} {colorize(status, Color.BOLD)}")
    if result.confidence:
        print(f"  Confidence: {result.confidence}")
    if result.evidence:
        print(f"  Evidence: {', '.join(result.evidence)}")
    if result.error:
        print(f"  Error: {colorize(result.error, Color.RED)}")
    print()

def progress_bar(current, total, label="Processing", length=30):
    """Прогрес-бар"""
    percent = current / total
    filled = int(length * percent)
    bar = "█" * filled + "░" * (length - filled)
    sys.stdout.write(f"\r  [{bar}] {percent*100:.0f}% - {label}")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")
