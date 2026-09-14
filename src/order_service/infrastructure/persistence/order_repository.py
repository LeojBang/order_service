"""Реализация OrderRepository на SQLAlchemy."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.application.ports.order_repository import OrderRepository
from order_service.domain.order import Order, OrderStatus
from order_service.infrastructure.persistence.models import OrderORM


class SQLAlchemyOrderRepository(OrderRepository):
    """Переводит доменный Order ↔ ORM-модель OrderORM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(order_model: OrderORM) -> Order:
        """ORM → доменная сущность."""
        return Order(
            id=order_model.id,
            user_id=order_model.user_id,
            item_id=order_model.item_id,
            quantity=order_model.quantity,
            status=OrderStatus(order_model.status),
            idempotency_key=order_model.idempotency_key,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at,
        )

    @staticmethod
    def _to_model(domain_order: Order) -> OrderORM:
        """Доменная сущность → ORM."""
        return OrderORM(
            id=domain_order.id,
            user_id=domain_order.user_id,
            item_id=domain_order.item_id,
            quantity=domain_order.quantity,
            status=domain_order.status.value,
            idempotency_key=domain_order.idempotency_key,
            created_at=domain_order.created_at,
            updated_at=domain_order.updated_at,
        )

    async def add(self, domain_order: Order) -> None:
        order_model = self._to_model(domain_order)
        try:
            self._session.add(order_model)
            await self._session.flush()  # flush, не commit — commit делает UoW
        except IntegrityError:
            await self._session.rollback()
            raise

    async def get_by_id(self, order_id: UUID) -> Order | None:
        order_model = await self._session.get(OrderORM, order_id)
        if order_model is None:
            return None
        return self._to_entity(order_model)

    async def get_by_id_for_update(self, order_id: UUID) -> Order | None:
        statement = select(OrderORM).where(OrderORM.id == order_id).with_for_update()
        result = await self._session.execute(statement)
        order_model = result.scalar_one_or_none()
        if order_model is None:
            return None
        return self._to_entity(order_model)

    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        statement = select(OrderORM).where(OrderORM.idempotency_key == idempotency_key)
        result = await self._session.execute(statement)
        order_model = result.scalar_one_or_none()
        if order_model is None:
            return None
        return self._to_entity(order_model)

    async def update(self, order: Order) -> None:
        order_model = await self._session.get(OrderORM, order.id)
        if order_model is None:
            return

        order_model.status = order.status.value
        order_model.updated_at = order.updated_at
        await self._session.flush()
