"""HTTP-клиент Notifications Service (Capashino)."""

import logging

import httpx

from order_service.application.ports.notifications_client import NotificationsClient

logger = logging.getLogger(__name__)


class HttpNotificationsClient(NotificationsClient):
    """POST /api/notifications с заголовком X-API-Key."""

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=10.0)

    async def send_notification(
        self, message: str, reference_id: str, idempotency_key: str
    ) -> None:
        try:
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

        except httpx.HTTPError as e:
            logger.error(
                "notification failed: ref=%s key=%s err=%s",
                reference_id,
                idempotency_key,
                e,
            )
