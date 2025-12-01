# Система Аутентификации и Авторизации на Django REST Framework

Полнофункциональная система управления доступом с собственной реализацией аутентификации и авторизации.


### Шаг 1: Клонирование и подготовка

```bash
# Перейти в директорию проекта
cd tzpython1

# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
venv\Scripts\activate


# Установить зависимости
pip install -r requirements.txt
```

### Шаг 2: Конфигурация базы данных

```bash
# Создать файл .env на основе .env.example
cp .env.example .env

### Шаг 3: Миграции базы данных

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Инициализировать базу данных с тестовыми данными
python manage.py init_db
```

### Шаг 4: Запуск сервера

```bash
# Запустить development сервер
python manage.py runserver


### Пример 1: Полный цикл регистрации и логина

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Новый",
    "last_name": "Пользователь",
    "email": "new@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'

# 2. Логин
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new@example.com",
    "password": "securepass123"
  }'

# Получить token из ответа и использовать его

# 3. Получить информацию о себе
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer {token}"

# 4. Логаут
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer {token}"
```

### Пример 2: Управление ролями (Admin)

```bash
# 1. Получить список пользователей
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer {admin_token}"

# 2. Получить список ролей
curl -X GET http://localhost:8000/api/roles/ \
  -H "Authorization: Bearer {admin_token}"

# 3. Назначить роль пользователю
curl -X POST http://localhost:8000/api/users/{user_id}/assign_role/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"role_id": "{role_id}"}'

# 4. Получить правила доступа для роли
curl -X GET "http://localhost:8000/api/access-rules/by_role/?role_id={role_id}" \
  -H "Authorization: Bearer {admin_token}"
```

### Пример 3: Проверка прав доступа

```bash
# Admin может видеть все товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer {admin_token}"
# Response 200: все товары

# User может видеть только свои товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer {user_token}"
# Response 200: только товары пользователя

# Guest может видеть товары (read_permission)
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer {guest_token}"
# Response 200: товары

# Guest не может создавать товары
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer {guest_token}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Товар", "price": 1000}'
# Response 403: Доступ запрещен
```

---

## 🗄️ Структура базы данных

### Таблица: users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100),
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW
);
```

### Таблица: roles
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP AUTO_NOW_ADD
);
```

### Таблица: user_roles
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY REFERENCES users(id),
    role_id UUID FOREIGN KEY REFERENCES roles(id),
    assigned_at TIMESTAMP AUTO_NOW_ADD,
    UNIQUE(user_id, role_id)
);
```

### Таблица: business_elements
```sql
CREATE TABLE business_elements (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP AUTO_NOW_ADD
);
```

### Таблица: access_role_rules
```sql
CREATE TABLE access_role_rules (
    id UUID PRIMARY KEY,
    role_id UUID FOREIGN KEY REFERENCES roles(id),
    element_id UUID FOREIGN KEY REFERENCES business_elements(id),
    read_permission BOOLEAN DEFAULT FALSE,
    read_all_permission BOOLEAN DEFAULT FALSE,
    create_permission BOOLEAN DEFAULT FALSE,
    update_permission BOOLEAN DEFAULT FALSE,
    update_all_permission BOOLEAN DEFAULT FALSE,
    delete_permission BOOLEAN DEFAULT FALSE,
    delete_all_permission BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW,
    UNIQUE(role_id, element_id)
);
```

### Таблица: sessions
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY REFERENCES users(id),
    session_key VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    created_at TIMESTAMP AUTO_NOW_ADD,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP AUTO_NOW
);
```


## 🧪 Тестовые аккаунты

После инициализации БД доступны следующие аккаунты:

| Email | Пароль | Роль | Описание |
|-------|--------|------|---------|
| admin@example.com | admin123 | Admin | Администратор с полными правами |
| manager@example.com | manager123 | Manager | Менеджер с правами управления |
| user1@example.com | user123 | User | Обычный пользователь |
| guest@example.com | guest123 | Guest | Гость с ограниченными правами |



### Включить логирование

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Проверить JWT токен

```bash
# Декодировать JWT токен
python -c "import jwt; print(jwt.decode('{token}', 'secret', algorithms=['HS256']))"
```

