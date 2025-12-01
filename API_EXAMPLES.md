
### Регистрация нового пользователя

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Иван",
    "last_name": "Иванов",
    "patronymic": "Иванович",
    "email": "ivan@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

**Ответ:**
```json
{
    "message": "Пользователь успешно зарегистрирован",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "first_name": "Иван",
        "last_name": "Иванов",
        "patronymic": "Иванович",
        "email": "ivan@example.com",
        "full_name": "Иван Иванов Иванович",
        "is_active": true,
        "roles": ["User"],
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

### Логин

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**Ответ:**
```json
{
    "message": "Успешный вход",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiaWF0IjoxNzA0MTA2NDAwLCJleHAiOjE3MDQxOTI4MDB9.signature",
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "user": { ... }
}
```

**Сохраните токен для дальнейшего использования:**
```bash
export TOKEN="eyJ0eXAiOiJKV..."
```

### Получить информацию о текущем пользователе

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Администратор",
    "last_name": "Системы",
    "email": "admin@example.com",
    "is_active": true,
    "roles": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Admin",
            "assigned_at": "2024-01-01T12:00:00Z"
        }
    ],
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

### Логаут

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
{
    "message": "Успешный выход"
}
```

---

## 👥 Управление пользователями

### Получить список всех пользователей (только Admin)

```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "first_name": "Администратор",
        "last_name": "Системы",
        "patronymic": "",
        "email": "admin@example.com",
        "full_name": "Администратор Системы",
        "is_active": true,
        "roles": ["Admin"],
        "created_at": "2024-01-01T12:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "first_name": "Иван",
        "last_name": "Пользователь",
        "patronymic": "Иванович",
        "email": "user1@example.com",
        "full_name": "Иван Пользователь Иванович",
        "is_active": true,
        "roles": ["User"],
        "created_at": "2024-01-01T13:00:00Z"
    }
]
```

### Получить информацию о конкретном пользователе

```bash
curl -X GET http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440001/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "first_name": "Иван",
    "last_name": "Пользователь",
    "patronymic": "Иванович",
    "email": "user1@example.com",
    "is_active": true,
    "roles": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "name": "User",
            "assigned_at": "2024-01-01T13:00:00Z"
        }
    ],
    "created_at": "2024-01-01T13:00:00Z",
    "updated_at": "2024-01-01T13:00:00Z"
}
```

### Обновить профиль пользователя

```bash
curl -X PATCH http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440001/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Петр",
    "last_name": "Петров",
    "patronymic": "Петрович"
  }'
```

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "first_name": "Петр",
    "last_name": "Петров",
    "patronymic": "Петрович",
    "email": "user1@example.com",
    "full_name": "Петр Петров Петрович",
    "is_active": true,
    "roles": ["User"],
    "created_at": "2024-01-01T13:00:00Z"
}
```

### Назначить роль пользователю

```bash
# Сначала получите ID роли
curl -X GET http://localhost:8000/api/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Затем назначьте роль
curl -X POST http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440001/assign_role/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "550e8400-e29b-41d4-a716-446655440002"
  }'
```

**Ответ:**
```json
{
    "message": "Роль Admin назначена пользователю"
}
```

### Удалить роль у пользователя

```bash
curl -X POST http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440001/remove_role/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "550e8400-e29b-41d4-a716-446655440002"
  }'
```

**Ответ:**
```json
{
    "message": "Роль удалена"
}
```

### Деактивировать пользователя

```bash
curl -X POST http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440001/deactivate/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
{
    "message": "Пользователь деактивирован"
}
```

### Удалить свой аккаунт

```bash
curl -X POST http://localhost:8000/api/users/delete_account/ \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
{
    "message": "Ваш аккаунт удален"
}
```

---

## 🎭 Управление ролями

### Получить список ролей

```bash
curl -X GET http://localhost:8000/api/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Admin",
        "description": "Администратор системы с полными правами",
        "created_at": "2024-01-01T12:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Manager",
        "description": "Менеджер с правами управления ресурсами",
        "created_at": "2024-01-01T12:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "name": "User",
        "description": "Обычный пользователь",
        "created_at": "2024-01-01T12:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440005",
        "name": "Guest",
        "description": "Гость с ограниченными правами",
        "created_at": "2024-01-01T12:00:00Z"
    }
]
```

### Создать новую роль

```bash
curl -X POST http://localhost:8000/api/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Moderator",
    "description": "Модератор контента"
  }'
```

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440006",
    "name": "Moderator",
    "description": "Модератор контента",
    "created_at": "2024-01-01T14:00:00Z"
}
```

---

## 🔑 Управление правилами доступа

### Получить все правила доступа

```bash
curl -X GET http://localhost:8000/api/access-rules/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "role": "550e8400-e29b-41d4-a716-446655440002",
        "role_name": "Admin",
        "element": "550e8400-e29b-41d4-a716-446655440020",
        "element_name": "products",
        "read_permission": true,
        "read_all_permission": true,
        "create_permission": true,
        "update_permission": true,
        "update_all_permission": true,
        "delete_permission": true,
        "delete_all_permission": true,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
]
```

### Получить правила для конкретной роли

```bash
curl -X GET "http://localhost:8000/api/access-rules/by_role/?role_id=550e8400-e29b-41d4-a716-446655440002" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "role": "550e8400-e29b-41d4-a716-446655440002",
        "role_name": "Admin",
        "element": "550e8400-e29b-41d4-a716-446655440020",
        "element_name": "products",
        ...
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440011",
        "role": "550e8400-e29b-41d4-a716-446655440002",
        "role_name": "Admin",
        "element": "550e8400-e29b-41d4-a716-446655440021",
        "element_name": "orders",
        ...
    }
]
```

### Получить правила для конкретного бизнес-объекта

```bash
curl -X GET "http://localhost:8000/api/access-rules/by_element/?element_id=550e8400-e29b-41d4-a716-446655440020" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Ответ:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "role": "550e8400-e29b-41d4-a716-446655440002",
        "role_name": "Admin",
        "element": "550e8400-e29b-41d4-a716-446655440020",
        "element_name": "products",
        ...
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "role": "550e8400-e29b-41d4-a716-446655440003",
        "role_name": "Manager",
        "element": "550e8400-e29b-41d4-a716-446655440020",
        "element_name": "products",
        ...
    }
]
```

### Создать новое правило доступа

```bash
curl -X POST http://localhost:8000/api/access-rules/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "550e8400-e29b-41d4-a716-446655440006",
    "element": "550e8400-e29b-41d4-a716-446655440020",
    "read_permission": true,
    "read_all_permission": false,
    "create_permission": true,
    "update_permission": true,
    "update_all_permission": false,
    "delete_permission": false,
    "delete_all_permission": false
  }'
```

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "role": "550e8400-e29b-41d4-a716-446655440006",
    "role_name": "Moderator",
    "element": "550e8400-e29b-41d4-a716-446655440020",
    "element_name": "products",
    "read_permission": true,
    "read_all_permission": false,
    "create_permission": true,
    "update_permission": true,
    "update_all_permission": false,
    "delete_permission": false,
    "delete_all_permission": false,
    "created_at": "2024-01-01T14:00:00Z",
    "updated_at": "2024-01-01T14:00:00Z"
}
```

### Обновить правило доступа

```bash
curl -X PATCH http://localhost:8000/api/access-rules/550e8400-e29b-41d4-a716-446655440030/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delete_permission": true,
    "delete_all_permission": false
  }'
```

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "role": "550e8400-e29b-41d4-a716-446655440006",
    "role_name": "Moderator",
    "element": "550e8400-e29b-41d4-a716-446655440020",
    "element_name": "products",
    "read_permission": true,
    "read_all_permission": false,
    "create_permission": true,
    "update_permission": true,
    "update_all_permission": false,
    "delete_permission": true,
    "delete_all_permission": false,
    "created_at": "2024-01-01T14:00:00Z",
    "updated_at": "2024-01-01T14:00:00Z"
}
```


### Получить список товаров

```bash
# Admin видит все товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# User видит только свои товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Guest видит товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $GUEST_TOKEN"
```

**Ответ:**
```json
[
    {
        "id": 1,
        "name": "Ноутбук",
        "price": 50000,
        "owner_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    {
        "id": 2,
        "name": "Мышка",
        "price": 500,
        "owner_id": "550e8400-e29b-41d4-a716-446655440001"
    }
]
```

### Получить конкретный товар

```bash
curl -X GET http://localhost:8000/api/products/1/ \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
{
    "id": 1,
    "name": "Ноутбук",
    "price": 50000,
    "owner_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Создать товар

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новый товар",
    "price": 1000
  }'
```

**Ответ:**
```json
{
    "id": 4,
    "name": "Новый товар",
    "price": 1000,
    "owner_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### Обновить товар

```bash
curl -X PUT http://localhost:8000/api/products/4/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Обновленный товар",
    "price": 1500
  }'
```

**Ответ:**
```json
{
    "id": 4,
    "name": "Обновленный товар",
    "price": 1500,
    "owner_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### Удалить товар

```bash
curl -X DELETE http://localhost:8000/api/products/4/ \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Ответ:** 204 No Content

### Получить список заказов

```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
[
    {
        "id": 1,
        "product_id": 1,
        "quantity": 2,
        "total": 100000,
        "owner_id": "550e8400-e29b-41d4-a716-446655440000"
    }
]
```

### Получить список отчетов (только Manager и Admin)

```bash
# Admin может видеть отчеты
curl -X GET http://localhost:8000/api/reports/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# User не может видеть отчеты
curl -X GET http://localhost:8000/api/reports/ \
  -H "Authorization: Bearer $USER_TOKEN"
# Response 403: Доступ запрещен
```

**Ответ:**
```json
[
    {
        "id": 1,
        "title": "Отчет по продажам",
        "date": "2024-01-01",
        "owner_id": "550e8400-e29b-41d4-a716-446655440000"
    }
]
```


### Тестовые сценарии/ Сценарий 1: Проверка ролей

```bash
# 1. Залогиниться как Admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.token')

# 2. Залогиниться как User
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"user123"}' | jq -r '.token')

# 3. Admin видит все товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.[] | {id, name, owner_id}'

# 4. User видит только свои товары
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $USER_TOKEN" | jq '.[] | {id, name, owner_id}'
```

### Сценарий 2: Проверка прав на создание

```bash
# 1. Залогиниться как Guest
GUEST_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"guest@example.com","password":"guest123"}' | jq -r '.token')

# 2. Попытаться создать товар (должно быть запрещено)
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Товар","price":1000}'
# Response 403: Доступ запрещен
```

---

## 💡 Полезные советы

### Сохранение токенов в переменные

```bash
# Сохранить токен Admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.token')

# Проверить токен
echo $ADMIN_TOKEN

# Использовать токен
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Форматирование JSON ответов

```bash
# Красивый вывод JSON
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'

# Выбрать конкретные поля
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.[] | {email, roles}'

# Фильтрация
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.[] | select(.is_active == true)'
```

### Сохранение ответов в файл

```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" > users.json

