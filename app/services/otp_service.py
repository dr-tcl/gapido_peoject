import json
from app.core.config import settings
from app.core.security import generate_otp, hash_otp, verify_otp_hash
from app.core.exceptions import TooManyRequestsException, BadRequestException, UnauthorizedException
from app.db.redis import get_redis
from app.broker.rabbitmq import RabbitMQBroker
from app.utils.logger import logger


class OTPService:
    def __init__(self):
        self.redis = get_redis()
        self.broker = RabbitMQBroker()

    def _ip_key(self, ip: str):
        return f"otp_ip:{ip}"

    def _otp_key(self, phone: str) -> str:
        return f"otp:{phone}"

    def _attempt_key(self, phone: str) -> str:
        return f"otp_attempt:{phone}"

    def _resend_key(self, phone: str) -> str:
        return f"otp_resend:{phone}"

    async def send_otp(self, phone: str, ip:str):
        if await self.redis.get(self._resend_key(phone)):
            raise TooManyRequestsException("Please wait before requesting another OTP")

        if await self.redis.get(self._ip_key(ip)):
            raise TooManyRequestsException("Too many OTP requests from this IP")

        code = generate_otp(settings.OTP_LENGTH)
        payload_hash = {"phone": phone, "code_hash": hash_otp(code)}
        payload = {"phone": phone, "code_hash": code}

        await self.redis.setex(self._otp_key(phone), settings.OTP_TTL_SECONDS, json.dumps(payload_hash))
        await self.redis.setex(self._attempt_key(phone), settings.OTP_TTL_SECONDS, "0")
        await self.redis.setex(self._resend_key(phone), settings.OTP_RESEND_INTERVAL_SECONDS, "1")
        await self.redis.setex(self._ip_key(ip), settings.OTP_RESEND_INTERVAL_SECONDS, "1")

        logger.info(">>>> send kavenegar", phone, code)
        await self.broker.publish_sms(payload)

        return {"message": "OTP sent successfully"}

    async def verify_otp(self, phone: str, code: str):
        raw = await self.redis.get(self._otp_key(phone))
        if not raw:
            raise BadRequestException("OTP expired or not found")

        attempts = int(await self.redis.get(self._attempt_key(phone)) or 0)
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            await self.redis.delete(self._otp_key(phone))
            raise UnauthorizedException("Maximum verification attempts exceeded")

        payload = json.loads(raw)
        if not verify_otp_hash(code, payload["code_hash"]):
            await self.redis.incr(self._attempt_key(phone))
            raise UnauthorizedException("Invalid OTP code")

        await self.redis.delete(self._otp_key(phone))
        await self.redis.delete(self._attempt_key(phone))

        return {"message": "OTP verified successfully"}
