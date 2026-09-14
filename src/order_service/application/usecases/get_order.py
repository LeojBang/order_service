"""Use case: получение заказа по id (GET /orders/{id})."""

import uuid

from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.exceptions import OrderNotFoundError
from order_service.domain.order import Order


class GetOrderUseCase:
    """Простой read-only сценарий."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def execute(self, order_id: uuid.UUID) -> Order:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id(order_id)
            if order is None:
                raise OrderNotFoundError
            return order
