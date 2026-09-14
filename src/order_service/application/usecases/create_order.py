"""Use case: создание заказа (шаг 1 + 2).

Поток: идемпотентность → проверка каталога → сохранение NEW → создание платежа.
"""

import uuid
from datetime import datetime, UTC
from decimal import Decimal

from pydantic import BaseModel

from order_service.application.ports.catalog_client import CatalogClient
from order_service.application.ports.payments_client import PaymentsClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.exceptions import ItemNotAvailableError, PaymentCreationError
from order_service.domain.order import Order, OrderStatus


class CreateOrderUseCase:
    """Сценарий POST /orders."""

    class OrderDTO(BaseModel):
        """Входные данные use case (из HTTP-схемы presentation)."""

        user_id: str
        item_id: str
        quantity: int
        idempotency_key: str

    def __init__(
        self,
        catalog_client: CatalogClient,
        payments_client: PaymentsClient,
        order_service_base_url: str,
        unit_of_work: UnitOfWork,
    ):
        self._catalog_client = catalog_client
        self._unit_of_work = unit_of_work
        self._payments_client = payments_client
        self._order_service_base_url = order_service_base_url

    async def execute(self, order: OrderDTO) -> Order:
        # 1. Идемпотентность: повторный запрос с тем же ключом → тот же заказ
        async with self._unit_of_work() as uow:
            existing = await uow.orders.get_by_idempotency_key(order.idempotency_key)
            if existing:
                return existing

        # 2. Собираем доменный объект заказа
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

        # 3. Проверяем наличие товара в Catalog Service
        item = await self._catalog_client.get_item(order.item_id)
        if item.available_qty < order.quantity or order.quantity == 0:
            raise ItemNotAvailableError

        # 4. Сохраняем заказ в БД со статусом NEW
        async with self._unit_of_work() as uow:
            await uow.orders.add(order_data)
            await uow.commit()

        # 5. Создаём платёж в Capashino (вне транзакции — внешний HTTP)
        amount = str(Decimal(item.price) * order.quantity)
        callback_url = f"{self._order_service_base_url}/api/orders/payment-callback"
        try:
            await self._payments_client.create_payment(
                order_id=str(order_data.id),
                amount=amount,
                callback_url=callback_url,
                idempotency_key=order_data.idempotency_key,
            )
        except PaymentCreationError:
            # Платёж не создался — отменяем заказ
            order_data.status = OrderStatus.CANCELLED
            order_data.updated_at = datetime.now(UTC)
            async with self._unit_of_work() as uow:
                await uow.orders.update(order_data)
                await uow.commit()
            raise

        return order_data
