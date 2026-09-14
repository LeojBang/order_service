"""Use case: обработка событий доставки из Kafka (order.shipped / order.cancelled)."""

import uuid
from datetime import datetime, UTC

from pydantic import BaseModel

from order_service.application.ports.notifications_client import NotificationsClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.order import OrderStatus


class HandleShipmentEventUseCase:
    """Shipping Service публикует события → мы обновляем статус заказа."""

    class ShipmentEventDTO(BaseModel):
        """Событие из топика student_system-shipment.events."""

        event_type: str
        order_id: uuid.UUID
        shipment_id: str

    def __init__(self, unit_of_work: UnitOfWork, notifications_client: NotificationsClient):
        self._unit_of_work = unit_of_work
        self._notifications_client = notifications_client

    async def execute(self, shipment_event: ShipmentEventDTO):
        # Уникальный ключ события для inbox (защита от дублей Kafka)
        event_id = (
            f"{shipment_event.event_type}:"
            f"{shipment_event.order_id}:"
            f"{shipment_event.shipment_id}"
        )
        async with self._unit_of_work() as uow:
            if await uow.inbox.exists(event_id):
                return  # уже обработали

            order = await uow.orders.get_by_id(shipment_event.order_id)
            if not order:
                return  # заказ не наш — игнорируем

            if shipment_event.event_type == "order.shipped":
                order.status = OrderStatus.SHIPPED
            elif shipment_event.event_type == "order.cancelled":
                order.status = OrderStatus.CANCELLED
            else:
                return  # неизвестный тип — пропускаем

            order.updated_at = datetime.now(UTC)
            await uow.orders.update(order)
            await uow.inbox.add(event_id, shipment_event.event_type)
            await uow.commit()

        if shipment_event.event_type == "order.shipped":
            await self._notifications_client.send_notification(
                message="SHIPPED: Ваш заказ отправлен в доставку",
                reference_id=str(shipment_event.order_id),
                idempotency_key=f"{shipment_event.order_id}-SHIPPED",
            )
