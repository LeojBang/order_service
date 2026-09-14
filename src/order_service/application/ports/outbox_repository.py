"""Порт Outbox — надёжная публикация событий в Kafka через БД."""

from abc import ABC, abstractmethod
from uuid import UUID

from order_service.infrastructure.persistence.models import OutboxMessage


class OutboxRepository(ABC):
    """Transactional Outbox: событие пишется в БД вместе с изменением заказа.

    Фоновый poller читает неопубликованные записи и шлёт их в Kafka.
    """

    @abstractmethod
    async def add(self, event_type: str, payload: dict) -> None:
        """Добавить событие в outbox (published_at = NULL)."""

    @abstractmethod
    async def get_unpublished(self, limit: int) -> list[OutboxMessage]:
        """Взять пачку событий, ещё не отправленных в Kafka."""

    @abstractmethod
    async def mark_published(self, message_id: UUID) -> None:
        """Пометить событие как успешно опубликованное."""
