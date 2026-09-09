"""
UI Module — професійне оформлення CLI для Platium.
Підтримує теми, таблиці, прогрес-бари, спінери та кольоровий вивід.
"""

import os
import sys
import time
import shutil
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Константи кольорів (ANSI)
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "black": "\033[30m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
}

# Статуси з кольорами
STATUS_COLORS = {
    "success": COLORS["green"],
    "found": COLORS["green"],
    "error": COLORS["red"],
    "failed": COLORS["red"],
    "warning": COLORS["yellow"],
    "info": COLORS["blue"],
    "partial": COLORS["yellow"],
    "not_found": COLORS["dim"],
    "rate_limited": COLORS["yellow"],
    "skipped": COLORS["dim"],
    "invalid": COLORS["red"],
    "timeout": COLORS["red"],
    "unknown": COLORS["dim"],
}

class UI:
    """
    Головний клас для роботи з інтерфейсом.
    Автоматично визначає ширину терміналу та підтримує теми.
    """
    def __init__(self, theme: str = "dark", verbose: bool = False):
        self.theme = theme
        self.verbose = verbose
        self.width = shutil.get_terminal_size().columns if sys.stdout.isatty() else 80
        self.colors = COLORS
        self.status_colors = STATUS_COLORS

    def _colorize(self, text: str, color: str) -> str:
        """Додає ANSI-кольори до тексту, якщо термінал підтримує."""
        if not sys.stdout.isatty():
            return text
        return f"{color}{text}{COLORS['reset']}"

    def _truncate(self, text: str, max_len: int) -> str:
        """Обрізає текст до вказаної довжини."""
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + "..."

    # ---- ДРУК ЗАГОЛОВКІВ ТА СЕКЦІЙ ----
    def header(self, text: str, char: str = "=", color: str = "cyan") -> None:
        """Друкує заголовок з рамкою."""
        border = char * self.width
        print(self._colorize(border, color))
        print(self._colorize(f" {text} ".center(self.width), color))
        print(self._colorize(border, color))

    def section(self, text: str, color: str = "blue") -> None:
        """Друкує назву секції."""
        print(self._colorize(f"\n▶ {text}", color))

    def subsection(self, text: str, color: str = "cyan") -> None:
        """Друкує підсекцію."""
        print(self._colorize(f"  ▸ {text}", color))

    # ---- ДРУК СТАТУСІВ ----
    def status(self, message: str, status: str = "info") -> None:
        """Друкує повідомлення зі статусом."""
        color = self.status_colors.get(status, COLORS["reset"])
        status_label = status.upper()
        print(f"{self._colorize(f'[{status_label}]', color)} {message}")

    def success(self, message: str) -> None:
        self.status(message, "success")

    def error(self, message: str) -> None:
        self.status(message, "error")

    def warning(self, message: str) -> None:
        self.status(message, "warning")

    def info(self, message: str) -> None:
        self.status(message, "info")

    # ---- ДРУК ТАБЛИЦЬ ----
    def table(self, headers: List[str], rows: List[List[Union[str, int, float, None]]]) -> None:
        """
        Друкує таблицю з вирівнюванням.
        Перший рядок — заголовки, наступні — дані.
        """
        if not rows:
            self.info("No data to display")
            return

        # Перетворюємо всі значення на рядки
        str_rows = [[str(cell) if cell is not None else "" for cell in row] for row in rows]
        str_headers = [str(h) for h in headers]

        # Обчислюємо ширину колонок
        col_widths = [len(h) for h in str_headers]
        for row in str_rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell))

        # Додаємо відступи (1 пробіл з кожного боку)
        col_widths = [w + 2 for w in col_widths]

        # Перевіряємо, чи вміщується таблиця в термінал
        total_width = sum(col_widths) + len(col_widths) + 1
        if total_width > self.width:
            # Зменшуємо ширину колонок пропорційно
            ratio = (self.width - len(col_widths) - 1) / sum(col_widths)
            for i in range(len(col_widths)):
                col_widths[i] = max(3, int(col_widths[i] * ratio))

        # Формуємо рядок розділювача
        sep = "+" + "+".join("-" * w for w in col_widths) + "+"

        # Друкуємо заголовки
        print(sep)
        header_cells = []
        for i, h in enumerate(str_headers):
            header_cells.append(f" {h.ljust(col_widths[i]-1)}")
        print("|" + "|".join(header_cells) + "|")
        print(sep)

        # Друкуємо дані
        for row in str_rows:
            cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    display_cell = self._truncate(cell, col_widths[i]-1)
                    cells.append(f" {display_cell.ljust(col_widths[i]-1)}")
                else:
                    break
            print("|" + "|".join(cells) + "|")
        print(sep)

    # ---- ПРОГРЕС-БАР ----
    def progress(self, current: int, total: int, label: str = "", bar_len: int = 30) -> None:
        """
        Друкує прогрес-бар.
        """
        if total == 0:
            return
        percent = current / total
        filled = int(bar_len * percent)
        bar = "█" * filled + "░" * (bar_len - filled)
        percent_str = f"{percent*100:.1f}%"
        output = f"\r{self._colorize(bar, 'green')} {percent_str} {label}".ljust(self.width)
        sys.stdout.write(output)
        sys.stdout.flush()
        if current == total:
            sys.stdout.write("\n")

    # ---- СПІНЕР (ЗАВАНТАЖЕННЯ) ----
    def spinner(self, message: str = "Loading...", duration: float = 1.0) -> None:
        """
        Показує спінер протягом вказаної кількості секунд.
        """
        if not sys.stdout.isatty():
            time.sleep(duration)
            return

        frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        start = time.time()
        i = 0
        while time.time() - start < duration:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r{self._colorize(frame, 'cyan')} {message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")

    # ---- ВИВІД РЕЗУЛЬТАТІВ СКАНЕРА ----
    def print_result(self, result_data: Dict[str, Any], scan_type: str = "scan") -> None:
        """
        Друкує результати сканера у гарному форматі.
        Очікує словник з ключами: target, status, sources, data, error тощо.
        """
        target = result_data.get("target", "N/A")
        status = result_data.get("status", "unknown")
        sources = result_data.get("sources", {})
        data = result_data.get("data", {})
        error = result_data.get("error")

        self.header(f" {scan_type.upper()} RESULTS ", char="─", color="cyan")
        self.status(f"Target: {target}", "info")
        self.status(f"Status: {status}", status)

        if error:
            self.error(f"Error: {error}")

        if sources:
            self.section("Sources", "blue")
            for source_name, source_info in sources.items():
                source_status = source_info.get("status", "unknown")
                self.status(f"{source_name}: {source_status}", source_status)

        if data:
            self.section("Data", "blue")
            for key, value in data.items():
                if isinstance(value, dict):
                    self.subsection(key, "cyan")
                    for k, v in value.items():
                        if isinstance(v, (list, dict)):
                            v = json.dumps(v, indent=2, ensure_ascii=False)
                        self.info(f"  {k}: {v}")
                else:
                    self.info(f"{key}: {value}")

    # ---- МІНІ-КАРТА СТАТУСУ ----
    def status_card(self, title: str, status: str, details: Optional[str] = None) -> None:
        """
        Друкує міні-картку статусу.
        """
        color = self.status_colors.get(status, COLORS["reset"])
        status_label = status.upper()
        line = f"{self._colorize(title, 'bold')} [{self._colorize(status_label, color)}]"
        if details:
            line += f" {details}"
        print(line)

# Глобальний екземпляр для зручності
_ui = None

def get_ui(theme: str = "dark", verbose: bool = False) -> UI:
    """Повертає глобальний екземпляр UI."""
    global _ui
    if _ui is None:
        _ui = UI(theme=theme, verbose=verbose)
    return _ui
