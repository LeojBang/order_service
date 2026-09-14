"""HTTP-клиент Payments Service (Capashino)."""

import httpx

from order_service.application.ports.payments_client import PaymentResult, PaymentsClient
from order_service.domain.exceptions import PaymentCreationError


class HttpPaymentsClient(PaymentsClient):
    """Реализация PaymentsClient через httpx."""

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=10.0)

    async def create_payment(
        self, order_id: str, amount: str, callback_url: str, idempotency_key: str
    ) -> PaymentResult:
        body = {
            "order_id": order_id,
            "amount": amount,
            "callback_url": callback_url,  # Capashino вызовет его после оплаты
            "idempotency_key": idempotency_key,
        }
        try:
            response = await self._client.post(
                f"{self._base_url}/api/payments",
                headers={"X-API-Key": self._api_key},
                json=body,
            )
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError):
            raise PaymentCreationError from None

        data = response.json()
        return PaymentResult(
            id=data["id"],
            order_id=data["order_id"],
            amount=data["amount"],
            status=data["status"],
        )

    async def close(self):
        await self._client.aclose()
