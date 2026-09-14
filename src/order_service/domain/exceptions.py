class ItemNotAvailableError(Exception):
    "Товара нет в наличие или товара недостаточно"


class OrderNotFoundError(Exception):
    "Заказ не найден"

class PaymentCreationError(Exception):
    "Платеж не создался"