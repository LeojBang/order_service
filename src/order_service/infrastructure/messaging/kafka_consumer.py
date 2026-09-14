"""Kafka consumer — чтение событий доставки из Shipping Service."""

import json

from aiokafka import AIOKafkaConsumer

from order_service.application.usecases.handle_shipment import HandleShipmentEventUseCase

# Топик, куда Shipping публикует order.shipped / order.cancelled
SHIPMENT_EVENTS_TOPIC = "student_system-shipment.events"


async def run_shipment_consumer(
    bootstrap_servers: str,
    use_case: HandleShipmentEventUseCase,
) -> None:
    """Бесконечный цикл: читаем Kafka → вызываем use case.

    Запускается как asyncio.create_task в lifespan FastAPI.
    """
    consumer = AIOKafkaConsumer(
        SHIPMENT_EVENTS_TOPIC,
        bootstrap_servers=bootstrap_servers,
        group_id="order-service",  # consumer group — балансировка между репликами
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for message in consumer:
            dto = HandleShipmentEventUseCase.ShipmentEventDTO.model_validate(message.value)
            await use_case.execute(dto)
    finally:
        await consumer.stop()
