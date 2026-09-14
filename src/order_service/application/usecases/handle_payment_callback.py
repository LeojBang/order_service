"""Use case: callback от Capashino Payments (POST /orders/payment-callback).

При успешной оплате: PAID + запись order.paid в outbox (для Shipping через Kafka).
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel

from order_service.application.ports.notifications_client import NotificationsClient
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

    def __init__(self, unit_of_work: UnitOfWork, notifications_client: NotificationsClient):
        self._unit_of_work = unit_of_work
        self._notifications_client = notifications_client

    async def execute(self, payment: PaymentDTO) -> Order:
        notify_paid = False

        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id_for_update(payment.order_id)
            if not order:
                raise OrderNotFoundError

            if payment.status == "succeeded" and order.status == OrderStatus.PAID:
                notify_paid = True
            elif payment.status == "failed" and order.status == OrderStatus.CANCELLED:
                pass
            elif payment.status == "succeeded":
                order.status = OrderStatus.PAID
                order.updated_at = datetime.now(UTC)
                await uow.orders.update(order)
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
                notify_paid = True
            elif payment.status == "failed":
                order.status = OrderStatus.CANCELLED
                order.updated_at = datetime.now(UTC)
                await uow.orders.update(order)
                await uow.commit()
            else:
                return order

        if notify_paid:
            await self._notifications_client.send_notification(
                message="PAID: Ваш заказ успешно оплачен и готов к отправке",
                reference_id=str(order.id),
                idempotency_key=f"{order.id}-PAID",
            )

        return order
