"""Точка входа FastAPI — HTTP API + Kafka consumer (shipment events).

Outbox poller вынесен в отдельный процесс: bin/run.py
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from order_service.application.usecases.handle_shipment import HandleShipmentEventUseCase
from order_service.infrastructure.messaging.kafka_consumer import run_shipment_consumer
from order_service.infrastructure.persistence.database import SessionLocal
from order_service.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from order_service.presentation.api.dependencies import get_notifications_client
from order_service.presentation.api.routers import router
from order_service.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: только shipment consumer (order.shipped → SHIPPED)."""
    unit_of_work = SQLAlchemyUnitOfWork(SessionLocal)
    shipment_use_case = HandleShipmentEventUseCase(
        unit_of_work, notifications_client=get_notifications_client()
    )

    consumer_task = asyncio.create_task(
        run_shipment_consumer(settings.KAFKA_BOOTSTRAP_SERVERS, shipment_use_case)
    )

    yield

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router, prefix="/api")
    return app


app = create_app()
