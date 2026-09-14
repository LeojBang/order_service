"""Порт для Notifications Service — отправка уведомлений пользователю."""

from abc import ABC, abstractmethod


class NotificationsClient(ABC):
    """Абстракция клиента уведомлений. Реализация — HttpNotificationsClient."""

    @abstractmethod
    async def send_notification(
        self, message: str, reference_id: str, idempotency_key: str
    ) -> None:
        """Отправить уведомление.

        Args:
            message: текст (autotest ищет NEW / PAID / SHIPPED в message).
            reference_id: id заказа — по нему потом GET /api/notifications/reference.
            idempotency_key: уникальный ключ, чтобы не создавать дубли.
        """
