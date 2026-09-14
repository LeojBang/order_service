import uuid
from datetime import datetime, UTC

from pydantic import BaseModel

from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.order import OrderStatus


class HandleShipmentEventUseCase:
    class ShipmentEventDTO(BaseModel):
        event_type: str
        order_id: uuid.UUID
        shipment_id: str

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def execute(self, shipment_event: ShipmentEventDTO):
        event_id = f"{shipment_event.event_type}:{shipment_event.order_id}:{shipment_event.shipment_id}"
        async with self._unit_of_work() as uow:
            if await uow.inbox.exists(event_id):
                return

            order = await uow.orders.get_by_id(shipment_event.order_id)
            if not order:
                return

            if shipment_event.event_type == "order.shipped":
                order.status = OrderStatus.SHIPPED
            elif shipment_event.event_type == "order.cancelled":
                order.status = OrderStatus.CANCELLED
            else:
                return

            order.updated_at = datetime.now(UTC)
            await uow.orders.update(order)
            await uow.inbox.add(event_id, shipment_event.event_type)
            await uow.commit()
