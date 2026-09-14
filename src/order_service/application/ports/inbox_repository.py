"""Порт Inbox — идемпотентная обработка входящих событий из Kafka."""

from abc import ABC, abstractmethod


class InboxRepository(ABC):
    """Inbox pattern: каждое входящее событие обрабатывается ровно один раз.

    event_id уникален — повторное сообщение из Kafka игнорируется.
    """

    @abstractmethod
    async def exists(self, event_id: str) -> bool:
        """Проверить, обрабатывали ли мы это событие раньше."""

    @abstractmethod
    async def add(self, event_id: str, event_type: str) -> None:
        """Записать, что событие обработано (в той же транзакции, что и update заказа)."""
