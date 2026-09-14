from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from order_service.application.ports.inbox_repository import InboxRepository
from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.outbox_repository import OutboxRepository
from order_service.application.ports.unit_of_work import UnitOfWork, UnitOfWorkImplementation
from order_service.infrastructure.persistence.inbox_repository import SQLAlchemyInboxRepository
from order_service.infrastructure.persistence.order_repository import SQLAlchemyOrderRepository
from order_service.infrastructure.persistence.outbox_repository import SQLAlchemyOutboxRepository


class SQLAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @asynccontextmanager
    async def __call__(self, *args, **kwargs):
        async with self._session_factory() as session:
            try:
                yield _SQLAlchemyUnitOfWorkImplementation(session)
                await session.rollback()
            except Exception:
                await session.rollback()
                raise


class _SQLAlchemyUnitOfWorkImplementation(UnitOfWorkImplementation):

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def orders(self) -> OrderRepository:
        return SQLAlchemyOrderRepository(self._session)

    async def commit(self):
        await self._session.commit()

    @property
    def outbox(self) -> OutboxRepository:
        return SQLAlchemyOutboxRepository(self._session)

    @property
    def inbox(self) -> InboxRepository:
        return SQLAlchemyInboxRepository(self._session)