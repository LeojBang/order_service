from abc import ABC, abstractmethod
from order_service.application.ports.order_repository import OrderRepository


class UnitOfWork(ABC):

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass


class UnitOfWorkImplementation(ABC):
    @property
    @abstractmethod
    def orders(self) -> OrderRepository:
        pass

    @abstractmethod
    async def commit(self):
        pass
