"""
UI Module — професійне оформлення CLI для Platium.

Єдиний шар виводу для CLI:
- кольори та форматування;
- заголовки та секції;
- статуси;
- таблиці;
- progress bar;
- spinner;
- результати сканування;
- сумісний legacy API для існуючих CLI-модулів.
"""

import json
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# ANSI COLORS
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# COMPATIBILITY COLOR CLASS
# ---------------------------------------------------------------------------

class Color:
    """Сумісний API кольорів для існуючих CLI-модулів."""

    RESET = COLORS["reset"]
    BOLD = COLORS["bold"]
    DIM = COLORS["dim"]

    RED = COLORS["red"]
    GREEN = COLORS["green"]
    YELLOW = COLORS["yellow"]
    BLUE = COLORS["blue"]
    MAGENTA = COLORS["magenta"]
    CYAN = COLORS["cyan"]
    WHITE = COLORS["white"]
    BLACK = COLORS["black"]

    BG_RED = COLORS["bg_red"]
    BG_GREEN = COLORS["bg_green"]
    BG_YELLOW = COLORS["bg_yellow"]
    BG_BLUE = COLORS["bg_blue"]


# ---------------------------------------------------------------------------
# LOW-LEVEL HELPERS
# ---------------------------------------------------------------------------

def colorize(text: Any, color: str) -> str:
    """
    Додає ANSI-колір до тексту, якщо stdout є інтерактивним терміналом.
    """
    text = str(text)

    if not sys.stdout.isatty():
        return text

    return f"{color}{text}{COLORS['reset']}"


def _terminal_width(default: int = 80) -> int:
    """Повертає поточну ширину терміналу."""
    if not sys.stdout.isatty():
        return default

    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return default


# ---------------------------------------------------------------------------
# MAIN UI CLASS
# ---------------------------------------------------------------------------

class UI:
    """
    Головний клас CLI-інтерфейсу Platium.
    """

    def __init__(self, theme: str = "dark", verbose: bool = False):
        self.theme = theme
        self.verbose = verbose
        self.width = _terminal_width()
        self.colors = COLORS
        self.status_colors = STATUS_COLORS

    def _colorize(self, text: str, color: str) -> str:
        """Додає ANSI-колір до тексту."""
        return colorize(text, color)

    def _truncate(self, text: str, max_len: int) -> str:
        """Обрізає текст до заданої довжини."""
        text = str(text)

        if max_len <= 0:
            return ""

        if len(text) <= max_len:
            return text

        if max_len <= 3:
            return text[:max_len]

        return text[:max_len - 3] + "..."

    def refresh_width(self) -> None:
        """Оновлює ширину терміналу."""
        self.width = _terminal_width()

    # -----------------------------------------------------------------------
    # HEADERS / SECTIONS
    # -----------------------------------------------------------------------

    def header(
        self,
        text: str,
        char: str = "=",
        color: str = "cyan"
    ) -> None:
        """Друкує великий заголовок."""
        self.refresh_width()

        border = char * self.width

        print(self._colorize(border, COLORS.get(color, color)))
        print(
            self._colorize(
                f" {text} ".center(self.width),
                COLORS.get(color, color)
            )
        )
        print(self._colorize(border, COLORS.get(color, color)))

    def section(
        self,
        text: str,
        color: str = "blue"
    ) -> None:
        """Друкує назву секції."""
        self.refresh_width()

        print(
            self._colorize(
                f"\n▶ {text}",
                COLORS.get(color, color)
            )
        )

    def subsection(
        self,
        text: str,
        color: str = "cyan"
    ) -> None:
        """Друкує назву підсекції."""
        print(
            self._colorize(
                f"  ▸ {text}",
                COLORS.get(color, color)
            )
        )

    # -----------------------------------------------------------------------
    # STATUS
    # -----------------------------------------------------------------------

    def status(
        self,
        message: str,
        status: str = "info"
    ) -> None:
        """Друкує повідомлення зі статусом."""
        color = self.status_colors.get(
            status,
            COLORS["reset"]
        )

        status_label = status.upper()

        print(
            f"{self._colorize(f'[{status_label}]', color)} "
            f"{message}"
        )

    def success(self, message: str) -> None:
        self.status(message, "success")

    def error(self, message: str) -> None:
        self.status(message, "error")

    def warning(self, message: str) -> None:
        self.status(message, "warning")

    def info(self, message: str) -> None:
        self.status(message, "info")

    # -----------------------------------------------------------------------
    # TABLE
    # -----------------------------------------------------------------------

    def table(
        self,
        headers: List[str],
        rows: List[List[Union[str, int, float, None]]]
    ) -> None:
        """
        Друкує таблицю з автоматичним вирівнюванням.
        """
        if not headers:
            self.info("No columns to display")
            return

        if not rows:
            self.info("No data to display")
            return

        str_headers = [str(header) for header in headers]

        str_rows = [
            [
                str(cell) if cell is not None else ""
                for cell in row
            ]
            for row in rows
        ]

        column_count = len(str_headers)

        normalized_rows = []

        for row in str_rows:
            normalized_rows.append(
                row[:column_count]
                + [""] * max(0, column_count - len(row))
            )

        col_widths = [
            len(header)
            for header in str_headers
        ]

        for row in normalized_rows:
            for index, cell in enumerate(row):
                col_widths[index] = max(
                    col_widths[index],
                    len(cell)
                )

        col_widths = [
            width + 2
            for width in col_widths
        ]

        total_width = (
            sum(col_widths)
            + column_count
            + 1
        )

        if total_width > self.width:
            available_width = (
                self.width
                - column_count
                - 1
            )

            if available_width > column_count * 3:
                ratio = available_width / sum(col_widths)

                col_widths = [
                    max(
                        3,
                        int(width * ratio)
                    )
                    for width in col_widths
                ]

        separator = (
            "+"
            + "+".join(
                "-" * width
                for width in col_widths
            )
            + "+"
        )

        print(separator)

        header_cells = []

        for index, header in enumerate(str_headers):
            cell_width = col_widths[index] - 1
            display_header = self._truncate(
                header,
                cell_width
            )

            header_cells.append(
                f" {display_header.ljust(cell_width)}"
            )

        print(
            "|"
            + "|".join(header_cells)
            + "|"
        )

        print(separator)

        for row in normalized_rows:
            cells = []

            for index, cell in enumerate(row):
                cell_width = col_widths[index] - 1

                display_cell = self._truncate(
                    cell,
                    cell_width
                )

                cells.append(
                    f" {display_cell.ljust(cell_width)}"
                )

            print(
                "|"
                + "|".join(cells)
                + "|"
            )

        print(separator)

    # -----------------------------------------------------------------------
    # PROGRESS BAR
    # -----------------------------------------------------------------------

    def progress(
        self,
        current: int,
        total: int,
        label: str = "",
        bar_len: int = 30
    ) -> None:
        """Друкує progress bar."""
        if total <= 0:
            return

        current = max(0, min(current, total))

        percent = current / total
        filled = int(bar_len * percent)

        bar = (
            "█" * filled
            + "░" * (bar_len - filled)
        )

        percent_str = f"{percent * 100:.1f}%"

        output = (
            f"\r{self._colorize(bar, COLORS['green'])} "
            f"{percent_str} {label}"
        )

        if len(output) < self.width:
            output = output.ljust(self.width)

        sys.stdout.write(output)
        sys.stdout.flush()

        if current >= total:
            sys.stdout.write("\n")

    # -----------------------------------------------------------------------
    # SPINNER
    # -----------------------------------------------------------------------

    def spinner(
        self,
        message: str = "Loading...",
        duration: float = 1.0
    ) -> None:
        """Показує spinner протягом заданого часу."""
        if duration <= 0:
            return

        if not sys.stdout.isatty():
            time.sleep(duration)
            return

        frames = [
            "⣾",
            "⣽",
            "⣻",
            "⢿",
            "⡿",
            "⣟",
            "⣯",
            "⣷",
        ]

        start = time.time()
        index = 0

        while time.time() - start < duration:
            frame = frames[index % len(frames)]

            sys.stdout.write(
                f"\r{self._colorize(frame, COLORS['cyan'])} "
                f"{message}"
            )

            sys.stdout.flush()

            time.sleep(0.1)
            index += 1

        clear_length = len(message) + 10

        sys.stdout.write(
            "\r"
            + " " * clear_length
            + "\r"
        )

        sys.stdout.flush()

    # -----------------------------------------------------------------------
    # SCAN RESULT
    # -----------------------------------------------------------------------

    def print_result(
        self,
        result_data: Dict[str, Any],
        scan_type: str = "scan"
    ) -> None:
        """
        Форматує результат сканування.
        """
        if result_data is None:
            self.error("No result data")
            return

        target = result_data.get(
            "target",
            "N/A"
        )

        status = result_data.get(
            "status",
            "unknown"
        )

        sources = result_data.get(
            "sources",
            {}
        )

        data = result_data.get(
            "data",
            {}
        )

        error = result_data.get(
            "error"
        )

        if hasattr(status, "value"):
            status = status.value

        status = str(status)

        self.header(
            f"{scan_type.upper()} RESULTS",
            char="─",
            color="cyan"
        )

        self.status(
            f"Target: {target}",
            "info"
        )

        self.status(
            f"Status: {status}",
            status
        )

        if error:
            self.error(
                f"Error: {error}"
            )

        if sources:
            self.section(
                "Sources",
                "blue"
            )

            for source_name, source_info in sources.items():
                if isinstance(source_info, dict):
                    source_status = source_info.get(
                        "status",
                        "unknown"
                    )
                else:
                    source_status = "unknown"

                self.status(
                    f"{source_name}: {source_status}",
                    str(source_status)
                )

        if data:
            self.section(
                "Data",
                "blue"
            )

            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        self.subsection(
                            str(key),
                            "cyan"
                        )

                        for sub_key, sub_value in value.items():
                            if isinstance(
                                sub_value,
                                (list, dict)
                            ):
                                sub_value = json.dumps(
                                    sub_value,
                                    indent=2,
                                    ensure_ascii=False
                                )

                            self.info(
                                f"  {sub_key}: {sub_value}"
                            )

                    elif isinstance(value, list):
                        self.info(
                            f"{key}: "
                            f"{json.dumps(value, ensure_ascii=False)}"
                        )

                    else:
                        self.info(
                            f"{key}: {value}"
                        )

            else:
                self.info(str(data))

    # -----------------------------------------------------------------------
    # STATUS CARD
    # -----------------------------------------------------------------------

    def status_card(
        self,
        title: str,
        status: str,
        details: Optional[str] = None
    ) -> None:
        """Друкує компактну status card."""
        color = self.status_colors.get(
            status,
            COLORS["reset"]
        )

        status_label = status.upper()

        line = (
            f"{self._colorize(title, COLORS['bold'])} "
            f"[{self._colorize(status_label, color)}]"
        )

        if details:
            line += f" {details}"

        print(line)


# ---------------------------------------------------------------------------
# GLOBAL UI INSTANCE
# ---------------------------------------------------------------------------

_ui: Optional[UI] = None


def get_ui(
    theme: str = "dark",
    verbose: bool = False
) -> UI:
    """
    Повертає глобальний екземпляр UI.
    """
    global _ui

    if _ui is None:
        _ui = UI(
            theme=theme,
            verbose=verbose
        )

    return _ui


# ---------------------------------------------------------------------------
# LEGACY / CLI COMPATIBILITY API
# ---------------------------------------------------------------------------

def display_banner() -> None:
    """
    Виводить головний банер Platium.
    """
    ui = get_ui()

    width = min(ui.width, 80)

    lines = [
        "PLATIUM",
        "OSINT & INTELLIGENCE FRAMEWORK",
    ]

    border = "═" * width

    print()
    print(colorize(border, COLORS["cyan"]))

    for line in lines:
        print(
            colorize(
                line.center(width),
                COLORS["bold"]
            )
        )

    print(colorize(border, COLORS["cyan"]))
    print()


def print_header(
    text: str,
    color: str = Color.CYAN
) -> None:
    """
    Сумісний заголовок для існуючих CLI-команд.
    """
    if color in COLORS:
        color_value = COLORS[color]
    else:
        color_value = color

    print(
        colorize(
            f"\n{text}",
            color_value
        )
    )


def print_scan_result(
    result: Any,
    scan_type: str = "scan"
) -> None:
    """
    Сумісний адаптер для виводу ScanResult або словника.
    """
    ui = get_ui()

    if hasattr(result, "to_dict"):
        result_data = result.to_dict()
    elif isinstance(result, dict):
        result_data = result
    else:
        result_data = {
            "target": getattr(
                result,
                "target",
                "N/A"
            ),
            "status": getattr(
                getattr(result, "status", None),
                "value",
                getattr(result, "status", "unknown")
            ),
            "sources": getattr(
                result,
                "sources",
                {}
            ),
            "data": getattr(
                result,
                "data",
                {}
            ),
            "error": getattr(
                result,
                "error",
                None
            ),
        }

    ui.print_result(
        result_data,
        scan_type
    )
