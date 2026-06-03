import grpc
from grpc import aio

from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    TooManyRequestsException,
    ServiceUnavailableException,
)
from app.core.interceptors import require_authenticated, require_admin
from app.proto import auth_pb2, auth_pb2_grpc
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService
from app.utils.logger import logger


def extract_client_ip(peer: str) -> str:
    if peer.startswith("ipv4:"):
        return peer.split("ipv4:")[1].rsplit(":", 1)[0]

    if peer.startswith("ipv6:"):
        raw = peer.split("ipv6:")[1]
        if raw.startswith("["):
            return raw.split("]")[0][1:]
        return raw.rsplit(":", 1)[0]

    return peer



async def abort_with_exception(context, exc: Exception):
    if isinstance(exc, BadRequestException):
        await context.abort(
            grpc.StatusCode.INVALID_ARGUMENT,
            exc.message
        )
    elif isinstance(exc, UnauthorizedException):
        await context.abort(
            grpc.StatusCode.UNAUTHENTICATED,
            exc.message
        )
    elif isinstance(exc, ForbiddenException):
        await context.abort(
            grpc.StatusCode.PERMISSION_DENIED,
            exc.message
        )
    elif isinstance(exc, TooManyRequestsException):
        await context.abort(
            grpc.StatusCode.RESOURCE_EXHAUSTED,
            exc.message
        )
    elif isinstance(exc, ServiceUnavailableException):
        await context.abort(
            grpc.StatusCode.UNAVAILABLE,
            exc.message
        )
    else:
        await context.abort(
            grpc.StatusCode.INTERNAL,
            "Internal server error"
        )


class AuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    async def SendOTP(self, request, context):
        try:
            service = OTPService()

            peer = context.peer()
            ip = extract_client_ip(peer)

            result = await service.send_otp(request.phone, ip)
            return auth_pb2.MessageResponse(message=result["message"])
        except Exception as exc:
            logger.exception("SendOTP failed")
            await abort_with_exception(context, exc)

    async def VerifyOTP(self, request, context):

        try:
            otp_service = OTPService()
            await otp_service.verify_otp(request.phone, request.code)

            auth_service = AuthService()
            tokens = await auth_service.login_or_register(request.phone)
            return auth_pb2.AuthTokensResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"]
            )
        except BadRequestException as exc:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, exc.message)
        except Exception as exc:
            logger.exception("VerifyOTP failed")
            await abort_with_exception(context, exc)

    async def RefreshToken(self, request, context):
        try:
            auth_service = AuthService()
            tokens = await auth_service.refresh(request.refresh_token)
            return auth_pb2.AuthTokensResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"]
            )
        except Exception as exc:
            logger.exception("RefreshToken failed")
            await abort_with_exception(context, exc)

    async def PublicAccess(self, request, context):
        return auth_pb2.MessageResponse(message="Public access granted")

    async def UserAccess(self, request, context):
        try:
            user = await require_authenticated(context)
            return auth_pb2.MessageResponse(
                message=f"Authenticated access granted for user {user['phone']}"
            )
        except Exception as exc:
            logger.exception("UserAccess failed")
            await abort_with_exception(context, exc)

    async def AdminAccess(self, request, context):
        try:
            user = await require_admin(context)
            return auth_pb2.MessageResponse(
                message=f"Admin access granted for admin {user['phone']}"
            )
        except Exception as exc:
            logger.exception("AdminAccess failed")
            await abort_with_exception(context, exc)


async def serve():
    server = aio.server()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    logger.info("gRPC server started on port 50051")
    await server.start()
    await server.wait_for_termination()
