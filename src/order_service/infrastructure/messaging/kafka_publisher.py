"""Kafka producer — отправка JSON-событий в топик."""

import json
from typing import Any

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    """Обёртка над AIOKafkaProducer для outbox poller."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
    ):
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic  # топик по умолчанию (order.events)
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        """Запустить producer (вызывается один раз при старте приложения)."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self._producer.start()

    async def stop(self):
        """Остановить producer при shutdown приложения."""
        if self._producer:
            await self._producer.stop()

    async def publish(
        self,
        message: dict[str, Any],
        key: str | None = None,
        topic: str | None = None,
    ) -> None:
        """Отправить сообщение в Kafka и дождаться подтверждения брокера."""
        if not self._producer:
            raise RuntimeError("Producer is not started. Call start() first.")

        target_topic = topic or self._topic
        await self._producer.send_and_wait(
            topic=target_topic,
            value=message,
            key=key,  # order_id — все события одного заказа в одну партицию
        )

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
