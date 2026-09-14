from abc import ABC, abstractmethod

from order_service.application.ports.inbox_repository import InboxRepository
from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.outbox_repository import OutboxRepository


class UnitOfWork(ABC):

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass


class UnitOfWorkImplementation(ABC):
    @property
    @abstractmethod
    def orders(self) -> OrderRepository:
        pass

    @property
    def outbox(self) -> OutboxRepository:
        pass

    @property
    def inbox(self) -> InboxRepository:
        pass

    @abstractmethod
    async def commit(self):
        pass
