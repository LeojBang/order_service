"""Порт для Payments Service — создание платежа после сохранения заказа."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    """Ответ Capashino после создания платежа."""

    id: str
    order_id: str
    amount: str
    status: str


class PaymentsClient(ABC):
    """Абстракция клиента платежей. Реализация — HttpPaymentsClient."""

    @abstractmethod
    async def create_payment(
        self, order_id: str, amount: str, callback_url: str, idempotency_key: str
    ) -> PaymentResult:
        """Создать платёж. Capashino потом вызовет callback_url с результатом."""
