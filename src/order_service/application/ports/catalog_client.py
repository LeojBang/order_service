from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CatalogItem:
    id: str
    name: str
    price: str
    available_qty: int


class CatalogClient(ABC):

    @abstractmethod
    async def get_item(self, item_id: str) -> CatalogItem:
        pass
