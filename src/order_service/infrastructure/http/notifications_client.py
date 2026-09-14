import httpx

from order_service.application.ports.notifications_client import NotificationsClient


class HttpNotificationsClient(NotificationsClient):

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=10.0)

    async def send_notification(self, message, reference_id, idempotency_key):
        response = await self._client.post(
            f"{self._base_url}/api/notifications",
            headers={"X-API-Key": self._api_key},
            json={
                "message": message,
                "reference_id": reference_id,
                "idempotency_key": idempotency_key,
            },
        )
        response.raise_for_status()