import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    id: uuid.UUID
    user_id: str
    item_id: str
    quantity: int
    status: OrderStatus
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
