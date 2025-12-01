"""
Команда для инициализации базы данных с тестовыми данными.
Использование: python manage.py init_db
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import User, Role, UserRole, BusinessElement, AccessRoleRule


class Command(BaseCommand):
    help = 'Инициализировать базу данных с тестовыми данными'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Инициализация базы данных...')

        # Создать роли
        roles_data = [
            {'name': 'Admin', 'description': 'Администратор системы с полными правами'},
            {'name': 'Manager', 'description': 'Менеджер с правами управления ресурсами'},
            {'name': 'User', 'description': 'Обычный пользователь'},
            {'name': 'Guest', 'description': 'Гость с ограниченными правами'},
        ]

        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            roles[role_data['name']] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Роль "{role.name}" создана'))
            else:
                self.stdout.write(f'- Роль "{role.name}" уже существует')

        # Создать бизнес-объекты
        elements_data = [
            {'name': 'products', 'description': 'Товары'},
            {'name': 'orders', 'description': 'Заказы'},
            {'name': 'reports', 'description': 'Отчеты'},
            {'name': 'users', 'description': 'Пользователи'},
            {'name': 'settings', 'description': 'Настройки'},
        ]

        elements = {}
        for element_data in elements_data:
            element, created = BusinessElement.objects.get_or_create(
                name=element_data['name'],
                defaults={'description': element_data['description']}
            )
            elements[element_data['name']] = element
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Бизнес-объект "{element.name}" создан'))
            else:
                self.stdout.write(f'- Бизнес-объект "{element.name}" уже существует')

        # Создать правила доступа
        access_rules = [
            # Admin - полный доступ ко всему
            {'role': 'Admin', 'element': 'products', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': True},
            {'role': 'Admin', 'element': 'orders', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': True},
            {'role': 'Admin', 'element': 'reports', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': True},
            {'role': 'Admin', 'element': 'users', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': True},
            {'role': 'Admin', 'element': 'settings', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': True},

            # Manager - может читать и управлять всеми ресурсами
            {'role': 'Manager', 'element': 'products', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': False},
            {'role': 'Manager', 'element': 'orders', 'read_all': True, 'create': True, 'update_all': True, 'delete_all': False},
            {'role': 'Manager', 'element': 'reports', 'read_all': True, 'create': True, 'update_all': False, 'delete_all': False},
            {'role': 'Manager', 'element': 'users', 'read_all': True, 'create': False, 'update_all': False, 'delete_all': False},

            # User - может читать и управлять только своими ресурсами
            {'role': 'User', 'element': 'products', 'read': True, 'create': True, 'update': True, 'delete': True},
            {'role': 'User', 'element': 'orders', 'read': True, 'create': True, 'update': True, 'delete': False},
            {'role': 'User', 'element': 'reports', 'read': False, 'create': False, 'update': False, 'delete': False},

            # Guest - только чтение товаров
            {'role': 'Guest', 'element': 'products', 'read': True, 'create': False, 'update': False, 'delete': False},
        ]

        for rule_data in access_rules:
            role = roles[rule_data['role']]
            element = elements[rule_data['element']]

            rule, created = AccessRoleRule.objects.get_or_create(
                role=role,
                element=element,
                defaults={
                    'read_permission': rule_data.get('read', False),
                    'read_all_permission': rule_data.get('read_all', False),
                    'create_permission': rule_data.get('create', False),
                    'update_permission': rule_data.get('update', False),
                    'update_all_permission': rule_data.get('update_all', False),
                    'delete_permission': rule_data.get('delete', False),
                    'delete_all_permission': rule_data.get('delete_all', False),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Правило доступа "{role.name}" -> "{element.name}" создано'))

        # Создать тестовых пользователей
        users_data = [
            {
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'email': 'admin@example.com',
                'password': 'admin123',
                'roles': ['Admin']
            },
            {
                'first_name': 'Менеджер',
                'last_name': 'Магазина',
                'email': 'manager@example.com',
                'password': 'manager123',
                'roles': ['Manager']
            },
            {
                'first_name': 'Иван',
                'last_name': 'Пользователь',
                'patronymic': 'Иванович',
                'email': 'user1@example.com',
                'password': 'user123',
                'roles': ['User']
            },
            {
                'first_name': 'Петр',
                'last_name': 'Гость',
                'email': 'guest@example.com',
                'password': 'guest123',
                'roles': ['Guest']
            },
        ]

        for user_data in users_data:
            password = user_data.pop('password')
            user_roles = user_data.pop('roles')

            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Пользователь "{user.email}" создан'))
            else:
                self.stdout.write(f'- Пользователь "{user.email}" уже существует')

            # Назначить роли
            for role_name in user_roles:
                role = roles[role_name]
                user_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role=role
                )
                if created:
                    self.stdout.write(f'  ✓ Роль "{role_name}" назначена')

        self.stdout.write(self.style.SUCCESS('\n✓ Инициализация базы данных завершена!'))
        self.stdout.write('\nТестовые аккаунты:')
        self.stdout.write('  admin@example.com : admin123 (Admin)')
        self.stdout.write('  manager@example.com : manager123 (Manager)')
        self.stdout.write('  user1@example.com : user123 (User)')
        self.stdout.write('  guest@example.com : guest123 (Guest)')
