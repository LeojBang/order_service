import uuid
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.application.ports.inbox_repository import InboxRepository
from order_service.infrastructure.persistence.models import InboxMessage


class SQLAlchemyInboxRepository(InboxRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, event_id: str, event_type: str) -> None:
        message = InboxMessage(
            id=uuid.uuid4(),
            event_id=event_id,
            event_type=event_type,
            processed_at=datetime.now(UTC),
        )
        self._session.add(message)
        await self._session.flush()

    async def exists(self, event_id: str) -> bool:
        statement = select(InboxMessage).where(InboxMessage.event_id == event_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
