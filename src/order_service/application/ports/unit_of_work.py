"""Unit of Work — одна транзакция на несколько репозиториев."""

from abc import ABC, abstractmethod

from order_service.application.ports.inbox_repository import InboxRepository
from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.outbox_repository import OutboxRepository


class UnitOfWork(ABC):
    """Фабрика транзакций. Использование: async with uow() as impl: ..."""

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass


class UnitOfWorkImplementation(ABC):
    """Объект внутри транзакции — даёт доступ к репозиториям и commit()."""

    @property
    @abstractmethod
    def orders(self) -> OrderRepository:
        pass

    @property
    @abstractmethod
    def outbox(self) -> OutboxRepository:
        pass

    @property
    @abstractmethod
    def inbox(self) -> InboxRepository:
        pass

    @abstractmethod
    async def commit(self):
        """Зафиксировать все изменения в текущей транзакции."""
