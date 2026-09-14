"""Порт репозитория заказов — CRUD без привязки к SQLAlchemy."""

from abc import ABC, abstractmethod
from uuid import UUID

from order_service.domain.order import Order


class OrderRepository(ABC):
    """Хранилище заказов. Use case работает только с этим интерфейсом."""

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Сохранить новый заказ."""

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Найти заказ по id или вернуть None."""

    @abstractmethod
    async def get_by_id_for_update(self, order_id: UUID) -> Order | None:
        """Найти заказ по id с блокировкой строки (SELECT FOR UPDATE)."""

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> Order | None:
        """Найти заказ по ключу идемпотентности (для POST /orders retry)."""

    @abstractmethod
    async def update(self, order: Order) -> None:
        """Обновить существующий заказ (статус, updated_at)."""
