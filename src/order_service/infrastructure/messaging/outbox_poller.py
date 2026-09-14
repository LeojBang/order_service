import asyncio

from order_service.infrastructure.messaging.kafka_publisher import KafkaProducer
from order_service.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

ORDER_EVENTS_TOPIC = "student_system-order.events"


async def run_outbox_poller(
    unit_of_work: SQLAlchemyUnitOfWork,
    kafka_producer: KafkaProducer,
    *,
    interval: float = 1.0,
    batch_size: int = 10,
) -> None:
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