"""Pydantic-схемы HTTP API — presentation слой, не протекают в domain."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from order_service.domain.order import Order


class CreateOrderRequest(BaseModel):
    """Тело POST /orders."""

    user_id: str
    item_id: str
    quantity: int = Field(gt=0)  # минимум 1
    idempotency_key: str


class OrderResponse(BaseModel):
    """Ответ с данными заказа."""

    id: uuid.UUID
    user_id: str
    item_id: str
    quantity: int = Field(gt=0)
    status: str = "NEW"
    created_at: datetime
    updated_at: datetime


class PaymentCallbackRequest(BaseModel):
    """Тело POST /orders/payment-callback — приходит от Capashino Payments."""

    payment_id: str
    order_id: uuid.UUID
    status: str
    amount: str
    error_message: str | None = None


def order_to_response(order: Order) -> OrderResponse:
    """Конвертер domain Order → HTTP-ответ."""
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        item_id=order.item_id,
        quantity=order.quantity,
        status=order.status.value,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
