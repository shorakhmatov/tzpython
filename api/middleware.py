"""
Middleware для обработки аутентификации и присваивания request.user.
"""

from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from .authentication import JWTAuthentication, SessionAuthentication
from .models import User


class AuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для аутентификации пользователя и присваивания request.user.
    Пытается аутентифицировать через JWT, затем через сессии.
    """

    def process_request(self, request):
        """
        Обработать входящий запрос и аутентифицировать пользователя.
        """
        # Инициализировать request.user как AnonymousUser
        request.user = None
        request.auth = None

        # Попытаться аутентифицировать через JWT
        jwt_auth = JWTAuthentication()
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                request.user, request.auth = auth_result
                return None
        except AuthenticationFailed:
            pass

        # Попытаться аутентифицировать через сессии
        session_auth = SessionAuthentication()
        try:
            auth_result = session_auth.authenticate(request)
            if auth_result:
                request.user, request.auth = auth_result
                return None
        except AuthenticationFailed:
            pass

        # Если аутентификация не удалась, пользователь остается None
        return None
