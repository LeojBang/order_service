"""Outbox poller — фоновая задача отправки событий из БД в Kafka."""

import asyncio

from order_service.infrastructure.messaging.kafka_publisher import KafkaProducer
from order_service.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

# Топик, куда Order Service публикует order.paid (Shipping его слушает)
ORDER_EVENTS_TOPIC = "student_system-order.events"


async def run_outbox_poller(
    unit_of_work: SQLAlchemyUnitOfWork,
    kafka_producer: KafkaProducer,
    *,
    interval: float = 1.0,
    batch_size: int = 10,
) -> None:
    """Каждые `interval` секунд читает outbox и шлёт неопубликованные события.

    Алгоритм:
    1. SELECT ... WHERE published_at IS NULL
    2. publish в Kafka
    3. mark_published + commit
    """
    while True:
        async with unit_of_work() as uow:
            messages = await uow.outbox.get_unpublished(limit=batch_size)
            for message in messages:
                await kafka_producer.publish(
                    message.payload,
                    key=message.payload["order_id"],
                )
                await uow.outbox.mark_published(message.id)
            if messages:
                await uow.commit()

        await asyncio.sleep(interval)
