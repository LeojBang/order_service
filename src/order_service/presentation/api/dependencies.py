from functools import lru_cache

from order_service.application.usecases.create_order import CreateOrderUseCase
from order_service.application.usecases.get_order import GetOrderUseCase
from order_service.application.usecases.handle_payment_callback import HandlePaymentCallbackUseCase
from order_service.infrastructure.http.catalog_client import HttpCatalogClient
from order_service.infrastructure.http.payments_client import HttpPaymentsClient
from order_service.infrastructure.persistence.database import SessionLocal
from order_service.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from order_service.settings import settings


@lru_cache
def get_unit_of_work():
    return SQLAlchemyUnitOfWork(SessionLocal)


@lru_cache
def get_catalog_client():
    return HttpCatalogClient(settings.CAPASHINO_BASE_URL, settings.CAPASHINO_API_KEY)


@lru_cache
def get_payments_client():
    return HttpPaymentsClient(settings.CAPASHINO_BASE_URL, settings.CAPASHINO_API_KEY)


def get_create_order_use_case():
    return CreateOrderUseCase(
        catalog_client=get_catalog_client(),
        unit_of_work=get_unit_of_work(),
        payments_client=get_payments_client(),
        order_service_base_url=settings.ORDER_SERVICE_BASE_URL,
    )


def get_handle_payment_callback_use_case():
    return HandlePaymentCallbackUseCase(unit_of_work=get_unit_of_work())


def get_get_order_use_case():
    return GetOrderUseCase(
        unit_of_work=get_unit_of_work(),
    )
