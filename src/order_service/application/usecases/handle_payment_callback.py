"""Use case: callback от Capashino Payments (POST /orders/payment-callback).

При успешной оплате: PAID + запись order.paid в outbox (для Shipping через Kafka).
"""

import uuid
from datetime import datetime, UTC

from pydantic import BaseModel

from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.exceptions import OrderNotFoundError
from order_service.domain.order import Order, OrderStatus


class HandlePaymentCallbackUseCase:
    """Capashino вызывает наш URL после обработки платежа."""

    class PaymentDTO(BaseModel):
        """Тело callback от Payments Service."""

        payment_id: str
        order_id: uuid.UUID
        status: str  # "succeeded" или "failed"
        amount: str
        error_message: str | None

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def execute(self, payment: PaymentDTO) -> Order:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id(payment.order_id)
            if not order:
                raise OrderNotFoundError

        # Идемпотентность: повторный callback с тем же результатом — ничего не делаем
        if payment.status == "succeeded" and order.status == OrderStatus.PAID:
            return order
        if payment.status == "failed" and order.status == OrderStatus.CANCELLED:
            return order

        if payment.status == "succeeded":
            order.status = OrderStatus.PAID
            order.updated_at = datetime.now(UTC)
            async with self._unit_of_work() as uow:
                await uow.orders.update(order)
                # Outbox в той же транзакции — Shipping получит order.paid через Kafka
                await uow.outbox.add(
                    event_type="order.paid",
                    payload={
                        "event_type": "order.paid",
                        "order_id": str(order.id),
                        "item_id": order.item_id,
                        "quantity": order.quantity,
                        "idempotency_key": order.idempotency_key,
                    },
                )
                await uow.commit()
        elif payment.status == "failed":
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now(UTC)
            async with self._unit_of_work() as uow:
                await uow.orders.update(order)
                await uow.commit()
        else:
            return order

        return order
