
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer, CharField, IntegerField, ListSerializer
from .permissions import HasAccessToElement


# Mock-данные для демонстрации
MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук', 'price': 50000, 'owner_id': '1'},
    {'id': 2, 'name': 'Мышка', 'price': 500, 'owner_id': '2'},
    {'id': 3, 'name': 'Клавиатура', 'price': 2000, 'owner_id': '1'},
]

MOCK_ORDERS = [
    {'id': 1, 'product_id': 1, 'quantity': 2, 'total': 100000, 'owner_id': '1'},
    {'id': 2, 'product_id': 2, 'quantity': 5, 'total': 2500, 'owner_id': '2'},
]

MOCK_REPORTS = [
    {'id': 1, 'title': 'Отчет по продажам', 'date': '2024-01-01', 'owner_id': '1'},
    {'id': 2, 'title': 'Отчет по заказам', 'date': '2024-01-02', 'owner_id': '2'},
]


class ProductSerializer(Serializer):
    """Сериализатор для Product."""
    id = IntegerField()
    name = CharField(max_length=200)
    price = IntegerField()
    owner_id = CharField()


class OrderSerializer(Serializer):
    """Сериализатор для Order."""
    id = IntegerField()
    product_id = IntegerField()
    quantity = IntegerField()
    total = IntegerField()
    owner_id = CharField()


class ReportSerializer(Serializer):
    """Сериализатор для Report."""
    id = IntegerField()
    title = CharField(max_length=200)
    date = CharField()
    owner_id = CharField()


class ProductViewSet(viewsets.ViewSet):
    """
    Mock ViewSet для товаров.
    Демонстрирует применение системы авторизации.
    """
    element_name = 'products'

    def list(self, request):
        """
        Получить список товаров.
        GET /api/products/
        
        Правила доступа:
        - Admin: может видеть все товары
        - Manager: может видеть все товары
        - User: может видеть только свои товары
        - Guest: не может видеть товары
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Проверить право на чтение
        if not request.user.has_permission('products', 'read'):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Если пользователь может читать все товары
        if request.user.has_permission('products', 'read') and \
           request.user.roles.filter(name__in=['Admin', 'Manager']).exists():
            products = MOCK_PRODUCTS
        else:
            # Иначе показать только свои товары
            user_id = str(request.user.id)
            products = [p for p in MOCK_PRODUCTS if p['owner_id'] == user_id]

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Получить информацию о товаре.
        GET /api/products/{id}/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.has_permission('products', 'read'):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            product = next(p for p in MOCK_PRODUCTS if p['id'] == int(pk))
        except StopIteration:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверить, может ли пользователь видеть этот товар
        user_id = str(request.user.id)
        if product['owner_id'] != user_id and \
           not request.user.roles.filter(name__in=['Admin', 'Manager']).exists():
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def create(self, request):
        """
        Создать новый товар.
        POST /api/products/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.has_permission('products', 'create'):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data
            product['owner_id'] = str(request.user.id)
            product['id'] = max([p['id'] for p in MOCK_PRODUCTS]) + 1
            MOCK_PRODUCTS.append(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Обновить товар.
        PUT /api/products/{id}/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            product = next(p for p in MOCK_PRODUCTS if p['id'] == int(pk))
        except StopIteration:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверить право на обновление
        user_id = str(request.user.id)
        if product['owner_id'] == user_id:
            if not request.user.has_permission('products', 'update', user_id):
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            if not request.user.has_permission('products', 'update'):
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product.update(serializer.validated_data)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Удалить товар.
        DELETE /api/products/{id}/
        """
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            product = next(p for p in MOCK_PRODUCTS if p['id'] == int(pk))
        except StopIteration:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверить право на удаление
        user_id = str(request.user.id)
        if product['owner_id'] == user_id:
            if not request.user.has_permission('products', 'delete', user_id):
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            if not request.user.has_permission('products', 'delete'):
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )

        MOCK_PRODUCTS.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ViewSet):
    """
    Mock ViewSet для заказов.
    """
    element_name = 'orders'

    def list(self, request):
        """Получить список заказов."""
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.has_permission('orders', 'read'):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = str(request.user.id)
        if request.user.roles.filter(name__in=['Admin', 'Manager']).exists():
            orders = MOCK_ORDERS
        else:
            orders = [o for o in MOCK_ORDERS if o['owner_id'] == user_id]

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Получить информацию о заказе."""
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.has_permission('orders', 'read'):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            order = next(o for o in MOCK_ORDERS if o['id'] == int(pk))
        except StopIteration:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user_id = str(request.user.id)
        if order['owner_id'] != user_id and \
           not request.user.roles.filter(name__in=['Admin', 'Manager']).exists():
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class ReportViewSet(viewsets.ViewSet):
    """
    Mock ViewSet для отчетов.
    """
    element_name = 'reports'

    def list(self, request):
        """Получить список отчетов."""
        if not request.user:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.has_permission('reports', 'read'):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Только Admin и Manager могут видеть отчеты
        if not request.user.roles.filter(name__in=['Admin', 'Manager']).exists():
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReportSerializer(MOCK_REPORTS, many=True)
        return Response(serializer.data)
