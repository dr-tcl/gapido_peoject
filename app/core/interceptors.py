import grpc
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException


def get_token_from_metadata(context):
    metadata = dict(context.invocation_metadata())
    auth_header = metadata.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid authorization metadata")
    return auth_header.split(" ")[1]


async def require_authenticated(context):
    token = get_token_from_metadata(context)
    return decode_access_token(token)


async def require_admin(context):
    user = await require_authenticated(context)
    if user.get("role") != "admin":
        raise ForbiddenException("Admin access required")
    return user
