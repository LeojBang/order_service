import uuid
from datetime import datetime, UTC

from pydantic import BaseModel

from order_service.application.ports.catalog_client import CatalogClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.exceptions import ItemNotAvailableError
from order_service.domain.order import Order, OrderStatus


class CreateOrderUseCase:
    class OrderDTO(BaseModel):
        user_id: str
        item_id: str
        quantity: int
        idempotency_key: str

    def __init__(self, catalog_client: CatalogClient, unit_of_work: UnitOfWork):
        self._catalog_client = catalog_client
        self._unit_of_work = unit_of_work

    async def execute(self, order: OrderDTO) -> Order:
        async with self._unit_of_work() as uow:
            existing = await uow.orders.get_by_idempotency_key(order.idempotency_key)
            if existing:
                return existing

        order_data = Order(
            id=uuid.uuid4(),
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=OrderStatus.NEW,
            idempotency_key=order.idempotency_key,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        item = await self._catalog_client.get_item(order.item_id)
        if item.available_qty < order.quantity or order.quantity == 0:
            raise ItemNotAvailableError
        async with self._unit_of_work() as uow:
            await uow.orders.add(order_data)
            await uow.commit()

        return order_data
