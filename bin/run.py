"""Outbox worker — отдельный процесс: читает outbox и публикует события в Kafka.

Запуск:
    uv run python bin/run.py

В k8s запускается вместе с uvicorn в одном pod (см. Dockerfile CMD).
"""

import asyncio

from order_service.infrastructure.messaging.kafka_publisher import KafkaProducer
from order_service.infrastructure.messaging.outbox_poller import (
    ORDER_EVENTS_TOPIC,
    run_outbox_poller,
)
from order_service.infrastructure.persistence.database import SessionLocal
from order_service.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from order_service.settings import settings


async def main() -> None:
    unit_of_work = SQLAlchemyUnitOfWork(SessionLocal)
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=ORDER_EVENTS_TOPIC,
    )
    await producer.start()
    try:
        await run_outbox_poller(unit_of_work, producer)
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
