"""
API views для системы аутентификации и авторизации.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from datetime import timedelta

from .models import User, Role, UserRole, BusinessElement, AccessRoleRule, Session
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer, LoginSerializer,
    RoleSerializer, BusinessElementSerializer, AccessRoleRuleSerializer,
    SessionSerializer, UserDetailSerializer
)
from .permissions import IsAdmin, CanManageUsers, CanManageRoles
from .authentication import generate_jwt_token, create_session, invalidate_session


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet для аутентификации (регистрация, логин, логаут).
    """

    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """
        Регистрация нового пользователя.
        POST /api/auth/register/
        """
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        """
        Логин пользователя.
        POST /api/auth/login/
        Возвращает JWT токен и создает сессию.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Пользователь неактивен'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.check_password(serializer.validated_data['password']):
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Генерировать JWT токен
        token = generate_jwt_token(user.id)

        # Создать сессию
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        session = create_session(user, ip_address, user_agent)

        response = Response({
            'message': 'Успешный вход',
            'token': token,
            'session_id': session.session_key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

        # Установить cookie с session_id
        response.set_cookie(
            'session_id',
            session.session_key,
            max_age=86400,  # 24 часа
            httponly=True,
            secure=False  # Измените на True в production с HTTPS
        )

        return response

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Логаут пользователя.
        POST /api/auth/logout/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Инвалидировать сессию
        session_id = request.COOKIES.get('session_id')
        if session_id:
            invalidate_session(session_id)

        response = Response(
            {'message': 'Успешный выход'},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('session_id')
        return response

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Получить информацию о текущем пользователе.
        GET /api/auth/me/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(UserDetailSerializer(request.user).data, status=status.HTTP_200_OK)

    def _get_client_ip(self, request):
        """Получить IP адрес клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        """Получить список всех пользователей (только для Admin)."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Получить информацию о пользователе."""
        user = self.get_object()
        return Response(UserDetailSerializer(user).data)

    def update(self, request, *args, **kwargs):
        """Обновить информацию о пользователе."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def assign_role(self, request, pk=None):
        """
        Назначить роль пользователю.
        POST /api/users/{id}/assign_role/
        Body: {"role_id": "uuid"}
        """
        user = self.get_object()
        role_id = request.data.get('role_id')

        if not role_id:
            return Response(
                {'error': 'role_id не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Роль не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        user_role, created = UserRole.objects.get_or_create(user=user, role=role)

        if created:
            return Response(
                {'message': f'Роль {role.name} назначена пользователю'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': f'Пользователь уже имеет роль {role.name}'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def remove_role(self, request, pk=None):
        """
        Удалить роль у пользователя.
        POST /api/users/{id}/remove_role/
        Body: {"role_id": "uuid"}
        """
        user = self.get_object()
        role_id = request.data.get('role_id')

        if not role_id:
            return Response(
                {'error': 'role_id не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_role = UserRole.objects.get(user=user, role_id=role_id)
            user_role.delete()
            return Response(
                {'message': 'Роль удалена'},
                status=status.HTTP_200_OK
            )
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Пользователь не имеет этой роли'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def deactivate(self, request, pk=None):
        """
        Деактивировать пользователя (мягкое удаление).
        POST /api/users/{id}/deactivate/
        """
        user = self.get_object()
        user.is_active = False
        user.save()

        # Инвалидировать все сессии пользователя
        user.sessions.all().delete()

        return Response(
            {'message': 'Пользователь деактивирован'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        """
        Удалить свой аккаунт (мягкое удаление).
        POST /api/users/delete_account/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = request.user
        user.is_active = False
        user.save()

        # Инвалидировать все сессии
        user.sessions.all().delete()

        response = Response(
            {'message': 'Ваш аккаунт удален'},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('session_id')
        return response


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления ролями (только для Admin).
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [CanManageRoles]


class BusinessElementViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления бизнес-объектами (только для Admin).
    """
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [CanManageRoles]


class AccessRoleRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления правилами доступа (только для Admin).
    """
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [CanManageRoles]

    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """
        Получить все правила доступа для роли.
        GET /api/access-rules/by_role/?role_id=uuid
        """
        role_id = request.query_params.get('role_id')
        if not role_id:
            return Response(
                {'error': 'role_id не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rules = AccessRoleRule.objects.filter(role_id=role_id)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_element(self, request):
        """
        Получить все правила доступа для бизнес-объекта.
        GET /api/access-rules/by_element/?element_id=uuid
        """
        element_id = request.query_params.get('element_id')
        if not element_id:
            return Response(
                {'error': 'element_id не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rules = AccessRoleRule.objects.filter(element_id=element_id)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)


class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сессиями (только для Admin).
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [CanManageRoles]

    @action(detail=True, methods=['post'])
    def invalidate(self, request, pk=None):
        """
        Инвалидировать сессию.
        POST /api/sessions/{id}/invalidate/
        """
        session = self.get_object()
        session.delete()
        return Response(
            {'message': 'Сессия инвалидирована'},
            status=status.HTTP_200_OK
        )
