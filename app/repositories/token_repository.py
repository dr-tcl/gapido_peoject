from datetime import datetime
from app.db.mongo import get_db


class TokenRepository:
    def __init__(self):
        self.collection = get_db()["refresh_tokens"]

    async def save_token(self, user_id: str, token: str, expires_at):
        doc = {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "revoked": False,
        }
        await self.collection.insert_one(doc)

    async def get_valid_token(self, token: str):
        return await self.collection.find_one({
            "token": token,
            "revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })

    async def revoke_token(self, token: str):
        await self.collection.update_one({"token": token}, {"$set": {"revoked": True}})
