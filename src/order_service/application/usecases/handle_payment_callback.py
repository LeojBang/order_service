import uuid
from datetime import datetime, UTC

from pydantic import BaseModel

from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.exceptions import OrderNotFoundError
from order_service.domain.order import Order, OrderStatus


class HandlePaymentCallbackUseCase:
    class PaymentDTO(BaseModel):
        payment_id: str
        order_id: uuid.UUID
        status: str
        amount: str
        error_message: str | None

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def execute(self, payment: PaymentDTO) -> Order:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id(payment.order_id)
            if not order:
                raise OrderNotFoundError

        if payment.status == "succeeded" and order.status == OrderStatus.PAID:
            return order
        if payment.status == "failed" and order.status == OrderStatus.CANCELLED:
            return order

        if payment.status == "succeeded":
            order.status = OrderStatus.PAID
        elif payment.status == "failed":
            order.status = OrderStatus.CANCELLED
        else:
            return order

        order.updated_at = datetime.now(UTC)
        async with self._unit_of_work() as uow:
            await uow.orders.update(order)
            await uow.commit()

        return order
