"""Порт (интерфейс) для Catalog Service — application не знает про httpx."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CatalogItem:
    """Товар из каталога Capashino."""

    id: str
    name: str
    price: str  # строка, т.к. Capashino отдаёт decimal как text
    available_qty: int


class CatalogClient(ABC):
    """Абстракция клиента каталога. Реализация — HttpCatalogClient в infrastructure."""

    @abstractmethod
    async def get_item(self, item_id: str) -> CatalogItem:
        """Получить товар по id. 404 → ItemNotAvailableError в реализации."""
