import json

from aiokafka import AIOKafkaConsumer

from order_service.application.usecases.handle_shipment import HandleShipmentEventUseCase

SHIPMENT_EVENTS_TOPIC = "student_system-shipment.events"


async def run_shipment_consumer(
    bootstrap_servers: str,
    use_case: HandleShipmentEventUseCase,
) -> None:
    consumer = AIOKafkaConsumer(
        SHIPMENT_EVENTS_TOPIC,
        bootstrap_servers=bootstrap_servers,
        group_id="order-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for message in consumer:
            dto = HandleShipmentEventUseCase.ShipmentEventDTO.model_validate(message.value)
            await use_case.execute(dto)
    finally:
        await consumer.stop()