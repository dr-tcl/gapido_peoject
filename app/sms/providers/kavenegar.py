import httpx
from app.sms.base import BaseSMSProvider
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException
from app.utils.logger import logger


class KavenegarSMSProvider(BaseSMSProvider):
    async def send_otp(self, phone: str, code: str) -> dict:
        logger.info(">>>> send kavenegar" , phone, code)
        return None
        url = f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/verify/lookup.json"
        payload = {
            "receptor": phone,
            "token": code,
            "template": settings.KAVENEGAR_TEMPLATE
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, data=payload)
                if response.status_code != 200:
                    raise ServiceUnavailableException(f"Kavenegar failed: {response.text}")
                return response.json()
        except httpx.TimeoutException:
            raise ServiceUnavailableException("Kavenegar timeout")
        except httpx.RequestError:
            raise ServiceUnavailableException("Kavenegar connection error")
