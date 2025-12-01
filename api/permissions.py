"""
Модуль проверки прав доступа.
"""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAuthenticated(BasePermission):
    """
    Проверка, что пользователь аутентифицирован.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):
    """
    Проверка, что пользователь имеет роль Admin.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.roles.filter(name='Admin').exists()


class HasAccessToElement(BasePermission):
    """
    Проверка, что пользователь имеет доступ к бизнес-объекту.
    Использует метод has_permission на User.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Получить название элемента из view
        element_name = getattr(view, 'element_name', None)
        if not element_name:
            return True

        # Определить действие на основе метода HTTP
        action_map = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        action = action_map.get(request.method, 'read')

        # Проверить право доступа
        return request.user.has_permission(element_name, action)


class CanManageUsers(BasePermission):
    """
    Проверка, что пользователь может управлять пользователями.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Только Admin может управлять пользователями
        return request.user.roles.filter(name='Admin').exists()


class CanManageRoles(BasePermission):
    """
    Проверка, что пользователь может управлять ролями.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Только Admin может управлять ролями
        return request.user.roles.filter(name='Admin').exists()


class CanViewOwnData(BasePermission):
    """
    Проверка, что пользователь может просматривать только свои данные.
    """

    def has_object_permission(self, request, view, obj):
        # Пользователь может просматривать только свои данные
        return obj.id == request.user.id
