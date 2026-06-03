import json
import aio_pika
import asyncio
from app.core.config import settings
from app.services.sms_service import SMSService
from app.utils.logger import logger

async def consume_sms():
    while True:
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            break
        except Exception:
            logger.info("Waiting for RabbitMQ...")
            await asyncio.sleep(5)

    channel = await connection.channel()
    queue = await channel.declare_queue(settings.RABBITMQ_SMS_QUEUE, durable=True)

    sms_service = SMSService()

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body.decode())
                    await sms_service.send_otp(payload["phone"], payload["code_hash"])
                    logger.info(f"SMS sent to {payload['phone']}")
                except Exception as exc:
                    logger.exception(f"SMS worker error: {str(exc)}")


if __name__ == "__main__":
    asyncio.run(consume_sms())
