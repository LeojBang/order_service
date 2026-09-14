"""Доменные исключения — бизнес-ошибки, которые use case пробрасывает наверх."""


class ItemNotAvailableError(Exception):
    """Товара нет в наличии или запрошенного количества недостаточно."""


class OrderNotFoundError(Exception):
    """Заказ с указанным id не найден в базе."""


class PaymentCreationError(Exception):
    """Capashino Payments не смог создать платёж (сеть, 4xx/5xx)."""
