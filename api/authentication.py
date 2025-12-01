"""
Модуль аутентификации с JWT и сессиями.
"""

import jwt
import json
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User, Session


class JWTAuthentication(BaseAuthentication):
    """
    Аутентификация через JWT токены.
    Ожидает заголовок: Authorization: Bearer {token}
    """

    def authenticate(self, request):
        """
        Аутентифицировать запрос на основе JWT токена.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]  # Удалить 'Bearer '

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Токен истек')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Неверный токен')

        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')

        return (user, token)


class SessionAuthentication(BaseAuthentication):
    """
    Аутентификация через сессии (альтернатива JWT).
    Ожидает Cookie с session_id.
    """

    def authenticate(self, request):
        """
        Аутентифицировать запрос на основе сессии.
        """
        session_id = request.COOKIES.get('session_id')

        if not session_id:
            return None

        try:
            session = Session.objects.get(session_key=session_id)
        except Session.DoesNotExist:
            raise AuthenticationFailed('Сессия не найдена')

        if not session.is_valid():
            session.delete()
            raise AuthenticationFailed('Сессия истекла')

        user = session.user
        if not user.is_active:
            raise AuthenticationFailed('Пользователь неактивен')

        return (user, session_id)


def generate_jwt_token(user_id: str) -> str:
    """
    Генерировать JWT токен для пользователя.
    
    Args:
        user_id: ID пользователя
    
    Returns:
        JWT токен
    """
    payload = {
        'user_id': str(user_id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return token


def create_session(user: User, ip_address: str, user_agent: str = '') -> Session:
    """
    Создать новую сессию для пользователя.
    
    Args:
        user: объект пользователя
        ip_address: IP адрес клиента
        user_agent: User Agent браузера
    
    Returns:
        объект Session
    """
    import uuid
    session_key = str(uuid.uuid4())
    expires_at = timezone.now() + timedelta(hours=24)
    
    session = Session.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at
    )
    return session


def invalidate_session(session_id: str) -> bool:
    """
    Инвалидировать сессию (logout).
    
    Args:
        session_id: ID сессии
    
    Returns:
        True если сессия удалена, иначе False
    """
    try:
        session = Session.objects.get(session_key=session_id)
        session.delete()
        return True
    except Session.DoesNotExist:
        return False


from django.utils import timezone
