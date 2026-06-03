from app.core.config import settings
from app.sms.providers.kavenegar import KavenegarSMSProvider
from app.sms.providers.yektasms import YektaSMSProvider
from app.core.exceptions import BadRequestException


class SMSProviderFactory:
    @staticmethod
    def create():
        provider = settings.SMS_PROVIDER.lower()
        if provider == "kavenegar":
            return KavenegarSMSProvider()
        elif provider == "yektasms":
            return YektaSMSProvider()
        raise BadRequestException(f"Unsupported SMS provider: {provider}")
