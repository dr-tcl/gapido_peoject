from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.core.exceptions import UnauthorizedException


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.token_repo = TokenRepository()

    async def login_or_register(self, phone: str):
        user = await self.user_repo.ensure_user(phone)
        await self.user_repo.verify_user(phone)

        access_token = create_access_token({
            "sub": user["_id"],
            "phone": user["phone"],
            "role": user["role"],
        })

        refresh_token, expires_at = create_refresh_token({
            "sub": user["_id"],
            "phone": user["phone"],
            "role": user["role"],
        })

        await self.token_repo.save_token(user["_id"], refresh_token, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh(self, refresh_token: str):
        payload = decode_refresh_token(refresh_token)
        token_doc = await self.token_repo.get_valid_token(refresh_token)
        if not token_doc:
            raise UnauthorizedException("Refresh token is invalid or revoked")

        access_token = create_access_token({
            "sub": payload["sub"],
            "phone": payload["phone"],
            "role": payload["role"],
        })

        new_refresh_token, expires_at = create_refresh_token({
            "sub": payload["sub"],
            "phone": payload["phone"],
            "role": payload["role"],
        })

        await self.token_repo.revoke_token(refresh_token)
        await self.token_repo.save_token(payload["sub"], new_refresh_token, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        }
