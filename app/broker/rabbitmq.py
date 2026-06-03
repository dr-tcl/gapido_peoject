import json
import aio_pika
from app.core.config import settings


class RabbitMQBroker:
    def __init__(self):
        self.url = settings.RABBITMQ_URL
        self.queue_name = settings.RABBITMQ_SMS_QUEUE

    async def publish_sms(self, payload: dict):
        connection = await aio_pika.connect_robust(self.url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.queue_name, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue.name,
            )
