"""Точка входа FastAPI — HTTP API + фоновые задачи Kafka.

При старте:
  - outbox poller (order.paid → Kafka)
  - shipment consumer (Kafka → SHIPPED/CANCELLED)

При остановке — корректный shutdown всех задач.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from order_service.application.usecases.handle_shipment import HandleShipmentEventUseCase
from order_service.infrastructure.messaging.kafka_consumer import run_shipment_consumer
from order_service.infrastructure.messaging.kafka_publisher import KafkaProducer
from order_service.infrastructure.messaging.outbox_poller import (
    ORDER_EVENTS_TOPIC,
    run_outbox_poller,
)
from order_service.infrastructure.persistence.database import SessionLocal
from order_service.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from order_service.presentation.api.routers import router
from order_service.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle приложения — запуск/остановка фоновых worker'ов."""
    unit_of_work = SQLAlchemyUnitOfWork(SessionLocal)
    shipment_use_case = HandleShipmentEventUseCase(unit_of_work)

    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=ORDER_EVENTS_TOPIC,
    )
    await producer.start()

    # Фон: outbox → Kafka (order.paid)
    poller_task = asyncio.create_task(
        run_outbox_poller(unit_of_work, producer)
    )
    # Фон: Kafka → обновление статуса (order.shipped)
    consumer_task = asyncio.create_task(
        run_shipment_consumer(settings.KAFKA_BOOTSTRAP_SERVERS, shipment_use_case)
    )

    yield  # приложение работает

    # Shutdown
    poller_task.cancel()
    try:
        await poller_task
    except asyncio.CancelledError:
        pass
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await producer.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api")
