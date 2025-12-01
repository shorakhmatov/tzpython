"""
Модели для системы аутентификации и авторизации.

Структура:
- User: пользователи системы
- Role: роли (Admin, Manager, User, Guest)
- UserRole: связь пользователя с ролями (M2M)
- BusinessElement: бизнес-объекты (Products, Orders, Reports и т.д.)
- AccessRoleRule: правила доступа ролей к бизнес-объектам
- Session: сессии пользователей
"""

from django.db import models
from django.utils import timezone
import bcrypt
import uuid


class User(models.Model):
    """
    Модель пользователя с собственной реализацией хеширования пароля.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    email = models.EmailField(unique=True, verbose_name='Email')
    password_hash = models.CharField(max_length=255, verbose_name='Хеш пароля')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def set_password(self, password: str):
        """Хеширование и сохранение пароля с использованием bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Проверка пароля против хеша."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def get_full_name(self) -> str:
        """Получить полное имя пользователя."""
        parts = [self.first_name, self.last_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts)

    def has_permission(self, element_name: str, action: str, target_user_id=None) -> bool:
        """
        Проверить, имеет ли пользователь право на действие с объектом.
        
        Args:
            element_name: название бизнес-объекта (e.g., 'products', 'orders')
            action: действие (read, create, update, delete)
            target_user_id: ID пользователя-владельца объекта (для проверки own-прав)
        
        Returns:
            True если пользователь имеет право, иначе False
        """
        if not self.is_active:
            return False

        # Получить все роли пользователя
        user_roles = self.roles.all()

        # Получить бизнес-объект
        try:
            element = BusinessElement.objects.get(name=element_name)
        except BusinessElement.DoesNotExist:
            return False

        # Проверить правила доступа для каждой роли
        for role in user_roles:
            try:
                rule = AccessRoleRule.objects.get(role=role, element=element)
                
                # Проверить действие
                if action == 'read':
                    if rule.read_permission or rule.read_all_permission:
                        return True
                elif action == 'create':
                    if rule.create_permission:
                        return True
                elif action == 'update':
                    if rule.update_all_permission:
                        return True
                    if rule.update_permission and target_user_id == self.id:
                        return True
                elif action == 'delete':
                    if rule.delete_all_permission:
                        return True
                    if rule.delete_permission and target_user_id == self.id:
                        return True
            except AccessRoleRule.DoesNotExist:
                continue

        return False


class Role(models.Model):
    """
    Модель роли в системе.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Связь пользователя с ролями (M2M с дополнительными полями).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles', verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users', verbose_name='Роль')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Назначена')

    class Meta:
        db_table = 'user_roles'
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user} - {self.role}"


class BusinessElement(models.Model):
    """
    Модель бизнес-объекта приложения.
    Примеры: products, orders, reports, users, settings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        db_table = 'business_elements'
        verbose_name = 'Бизнес-объект'
        verbose_name_plural = 'Бизнес-объекты'

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """
    Правила доступа ролей к бизнес-объектам.
    
    Поля прав:
    - read_permission: может ли роль читать объекты
    - read_all_permission: может ли читать все объекты (иначе только свои)
    - create_permission: может ли создавать объекты
    - update_permission: может ли обновлять свои объекты
    - update_all_permission: может ли обновлять все объекты
    - delete_permission: может ли удалять свои объекты
    - delete_all_permission: может ли удалять все объекты
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='access_rules', verbose_name='Роль')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='access_rules', verbose_name='Бизнес-объект')
    
    read_permission = models.BooleanField(default=False, verbose_name='Чтение (свои)')
    read_all_permission = models.BooleanField(default=False, verbose_name='Чтение (все)')
    create_permission = models.BooleanField(default=False, verbose_name='Создание')
    update_permission = models.BooleanField(default=False, verbose_name='Обновление (свои)')
    update_all_permission = models.BooleanField(default=False, verbose_name='Обновление (все)')
    delete_permission = models.BooleanField(default=False, verbose_name='Удаление (свои)')
    delete_all_permission = models.BooleanField(default=False, verbose_name='Удаление (все)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        db_table = 'access_role_rules'
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'
        unique_together = ('role', 'element')

    def __str__(self):
        return f"{self.role} -> {self.element}"


class Session(models.Model):
    """
    Модель сессии пользователя для отслеживания активных сессий.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name='Пользователь')
    session_key = models.CharField(max_length=255, unique=True, verbose_name='Ключ сессии')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    expires_at = models.DateTimeField(verbose_name='Истекает')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')

    class Meta:
        db_table = 'sessions'
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'
        ordering = ['-last_activity']

    def __str__(self):
        return f"Session {self.user} ({self.created_at})"

    def is_valid(self) -> bool:
        """Проверить, активна ли сессия."""
        return self.expires_at > timezone.now()
