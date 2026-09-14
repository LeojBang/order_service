from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    id: str
    order_id: str
    amount: str
    status: str


class PaymentsClient(ABC):

    @abstractmethod
    async def create_payment(self, order_id: str, amount: str, callback_url: str, idempotency_key: str) -> PaymentResult:
        pass
