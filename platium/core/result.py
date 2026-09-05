"""
Unified Result System — єдина модель результатів для всіх сканерів
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

class ScanStatus(Enum):
    """Семантичні статуси для всіх сканерів"""
    SUCCESS = "success"          # Дані знайдено
    NOT_FOUND = "not_found"      # Дані не знайдено
    PARTIAL = "partial"          # Часткові дані
    ERROR = "error"              # Помилка виконання
    RATE_LIMITED = "rate_limited" # Перевищено ліміт запитів
    SKIPPED = "skipped"          # Пропущено (наприклад, немає ключа)
    INVALID = "invalid"          # Невалідний вхід
    TIMEOUT = "timeout"          # Таймаут
    UNKNOWN = "unknown"          # Невідомий статус

class ScanResult:
    """
    Єдина модель результату для всіх сканерів.
    Кожен сканер повинен повертати цей об'єкт.
    """
    def __init__(
        self,
        target: str,
        scanner: str,
        status: ScanStatus,
        data: Optional[Dict[str, Any]] = None,
        sources: Optional[Dict[str, Dict]] = None,
        error: Optional[str] = None,
        url: Optional[str] = None,
        confidence: float = 0.0,
        evidence: Optional[List[str]] = None,
        duration: Optional[float] = None,
        timestamp: Optional[str] = None,
    ):
        self.target = target
        self.scanner = scanner
        self.status = status
        self.data = data or {}
        self.sources = sources or {}
        self.error = error
        self.url = url
        self.confidence = confidence
        self.evidence = evidence or []
        self.duration = duration
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Перетворює результат у словник для JSON/звітів"""
        return {
            "target": self.target,
            "scanner": self.scanner,
            "status": self.status.value,
            "data": self.data,
            "sources": self.sources,
            "error": self.error,
            "url": self.url,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "duration": self.duration,
            "timestamp": self.timestamp
        }

    def to_json(self) -> str:
        """Повертає JSON-рядок результату"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def is_success(self) -> bool:
        return self.status == ScanStatus.SUCCESS

    def is_found(self) -> bool:
        return self.status in (ScanStatus.SUCCESS, ScanStatus.PARTIAL)

    def has_error(self) -> bool:
        return self.status in (ScanStatus.ERROR, ScanStatus.TIMEOUT, ScanStatus.INVALID)

    @staticmethod
    def error_result(target: str, scanner: str, error: str) -> 'ScanResult':
        """Створює результат з помилкою"""
        return ScanResult(
            target=target,
            scanner=scanner,
            status=ScanStatus.ERROR,
            error=error
        )

    @staticmethod
    def not_found(target: str, scanner: str) -> 'ScanResult':
        """Створює результат 'не знайдено'"""
        return ScanResult(
            target=target,
            scanner=scanner,
            status=ScanStatus.NOT_FOUND
        )

    @staticmethod
    def success_result(target: str, scanner: str, data: Dict, sources: Dict = None) -> 'ScanResult':
        """Створює успішний результат"""
        return ScanResult(
            target=target,
            scanner=scanner,
            status=ScanStatus.SUCCESS,
            data=data,
            sources=sources or {}
        )

    @staticmethod
    def partial_result(target: str, scanner: str, data: Dict, sources: Dict = None) -> 'ScanResult':
        """Створює частковий результат"""
        return ScanResult(
            target=target,
            scanner=scanner,
            status=ScanStatus.PARTIAL,
            data=data,
            sources=sources or {}
      )
