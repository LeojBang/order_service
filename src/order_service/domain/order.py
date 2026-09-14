"""Доменный слой: сущности и бизнес-правила без зависимостей от БД, HTTP или Kafka."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """Жизненный цикл заказа в системе Capashino."""

    NEW = "NEW"  # заказ создан, платёж ещё не прошёл
    PAID = "PAID"  # оплата успешна, ждём доставку
    SHIPPED = "SHIPPED"  # заказ отправлен
    CANCELLED = "CANCELLED"  # отменён (нет товара, ошибка платежа и т.д.)


@dataclass
class Order:
    """Заказ — главная сущность сервиса.

    Это «чистый» объект домена: без SQLAlchemy, без Pydantic.
    Репозиторий переводит его в ORM-модель и обратно.
    """

    id: uuid.UUID
    user_id: str
    item_id: str
    quantity: int
    status: OrderStatus
    idempotency_key: str  # защита от повторного создания при retry
    created_at: datetime
    updated_at: datetime
