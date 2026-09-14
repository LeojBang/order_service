"""ORM-модели SQLAlchemy — маппинг таблиц PostgreSQL.

Domain-слой про эти классы не знает; репозиторий переводит ORM ↔ Order.
"""

import uuid
from datetime import datetime, UTC

from sqlalchemy import UUID, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped

from order_service.infrastructure.persistence.database import Base


class OrderORM(Base):
    """Таблица orders — хранение заказов."""

    __tablename__ = "orders"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    item_id: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, nullable=False)  # значение OrderStatus.value
    idempotency_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class OutboxMessage(Base):
    """Таблица outbox — события для отправки в Kafka.

    published_at IS NULL → poller ещё не отправил.
    """

    __tablename__ = "outbox"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[JSONB] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )


class InboxMessage(Base):
    """Таблица inbox — уже обработанные входящие события."""

    __tablename__ = "inbox"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_id: Mapped[str] = mapped_column(String, unique=True)  # уникальный ключ события
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
