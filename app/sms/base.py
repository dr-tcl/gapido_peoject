from abc import ABC, abstractmethod


class BaseSMSProvider(ABC):
    @abstractmethod
    async def send_otp(self, phone: str, code: str) -> dict:
        pass
