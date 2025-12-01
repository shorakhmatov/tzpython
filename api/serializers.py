"""
Сериализаторы для API endpoints.
"""

from rest_framework import serializers
from .models import User, Role, UserRole, BusinessElement, AccessRoleRule, Session


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'email', 'full_name', 'is_active', 'roles', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_roles(self, obj):
        return [role.role.name for role in obj.roles.all()]


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Пользователь с таким email уже существует'})
        
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Назначить роль "User" по умолчанию
        try:
            user_role = Role.objects.get(name='User')
            UserRole.objects.create(user=user, role=user_role)
        except Role.DoesNotExist:
            pass
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic']


class LoginSerializer(serializers.Serializer):
    """Сериализатор для логина."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Role."""
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class BusinessElementSerializer(serializers.ModelSerializer):
    """Сериализатор для модели BusinessElement."""
    class Meta:
        model = BusinessElement
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AccessRoleRule."""
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)

    class Meta:
        model = AccessRoleRule
        fields = [
            'id', 'role', 'role_name', 'element', 'element_name',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SessionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Session."""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'user', 'user_email', 'ip_address', 'user_agent', 'created_at', 'expires_at', 'last_activity']
        read_only_fields = ['id', 'created_at', 'last_activity']


class UserDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для пользователя с ролями."""
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'email', 'is_active', 'roles', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_roles(self, obj):
        roles_data = []
        for user_role in obj.roles.all():
            roles_data.append({
                'id': str(user_role.role.id),
                'name': user_role.role.name,
                'assigned_at': user_role.assigned_at
            })
        return roles_data
