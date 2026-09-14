"""Реализация OutboxRepository — transactional outbox pattern."""

import uuid
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.application.ports.outbox_repository import OutboxRepository
from order_service.infrastructure.persistence.models import OutboxMessage


class SQLAlchemyOutboxRepository(OutboxRepository):
    """Запись событий в таблицу outbox для последующей отправки poller'ом."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, event_type: str, payload: dict) -> None:
        message = OutboxMessage(
            id=uuid.uuid4(),
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(UTC),
            published_at=None,  # poller выставит после успешной отправки в Kafka
        )
        self._session.add(message)
        await self._session.flush()

    async def get_unpublished(self, limit: int) -> list[OutboxMessage]:
        # FIFO: сначала старые события
        statement = (
            select(OutboxMessage)
            .where(OutboxMessage.published_at.is_(None))
            .order_by(OutboxMessage.created_at)
            .limit(limit)
        )
        messages = await self._session.execute(statement)
        return list(messages.scalars().all())

    async def mark_published(self, message_id: UUID) -> None:
        message = await self._session.get(OutboxMessage, message_id)
        if message is None:
            return
        message.published_at = datetime.now(UTC)
        await self._session.flush()
