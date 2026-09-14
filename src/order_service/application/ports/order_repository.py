from abc import ABC, abstractmethod
from uuid import UUID

from order_service.domain.order import Order


class OrderRepository(ABC):

    @abstractmethod
    async def add(self, order: Order) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> Order | None:
        pass

    @abstractmethod
    async def update(self, order: Order) -> None:
        pass
