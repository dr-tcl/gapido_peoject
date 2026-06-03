from datetime import datetime
from typing import Optional
from app.db.mongo import get_db


class UserRepository:
    def __init__(self):
        self.collection = get_db()["users"]

    async def get_by_phone(self, phone: str) -> Optional[dict]:
        return await self.collection.find_one({"phone": phone})

    async def create_user(self, phone: str, role: str = "user") -> dict:
        doc = {
            "_id": phone,
            "phone": phone,
            "role": role,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self.collection.insert_one(doc)
        return doc

    async def verify_user(self, phone: str):
        await self.collection.update_one(
            {"phone": phone},
            {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
        )

    async def ensure_user(self, phone: str):
        user = await self.get_by_phone(phone)
        if user:
            return user
        return await self.create_user(phone)
