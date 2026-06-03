import httpx
from app.sms.base import BaseSMSProvider
from app.core.exceptions import ServiceUnavailableException
from app.core.config import settings


class YektaSMSProvider(BaseSMSProvider):
    async def send_otp(self, phone: str, code: str) -> dict:
        url = "https://api.yektasms.example/send"
        payload = {
            "api_key": settings.YEKTASMS_API_KEY,
            "sender": settings.YEKTASMS_SENDER,
            "to": phone,
            "message": f"Your OTP code is {code}"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    raise ServiceUnavailableException(f"YektaSMS failed: {response.text}")
                return response.json()
        except httpx.TimeoutException:
            raise ServiceUnavailableException("YektaSMS timeout")
        except httpx.RequestError:
            raise ServiceUnavailableException("YektaSMS connection error")
