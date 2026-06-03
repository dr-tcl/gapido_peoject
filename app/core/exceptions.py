import grpc


class AppException(Exception):
    def __init__(self, message: str, grpc_status=None, error_code: str = "APP_ERROR"):
        self.message = message
        self.grpc_status = grpc_status
        self.error_code = error_code
        super().__init__(message)


class UnauthorizedException(AppException):
    pass


class ForbiddenException(AppException):
    pass


class BadRequestException(AppException):
    pass


class TooManyRequestsException(AppException):
    pass


class ServiceUnavailableException(AppException):
    pass

