from app.core.circuit_breaker import CircuitBreaker
from app.sms.factory import SMSProviderFactory


class SMSService:
    def __init__(self):
        self.provider = SMSProviderFactory.create()
        self.circuit_breaker = CircuitBreaker()

    async def send_otp(self, phone: str, code: str):
        return await self.circuit_breaker.call(self.provider.send_otp, phone, code)
