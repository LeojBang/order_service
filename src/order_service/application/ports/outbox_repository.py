from abc import ABC, abstractmethod
from uuid import UUID

from order_service.infrastructure.persistence.models import OutboxMessage


class OutboxRepository(ABC):

    @abstractmethod
    async def add(self, event_type: str, payload: dict) -> None:
        pass

    @abstractmethod
    async def get_unpublished(self, limit: int) -> list[OutboxMessage]:
        pass

    @abstractmethod
    async def mark_published(self, message_id: UUID) -> None:
        pass
