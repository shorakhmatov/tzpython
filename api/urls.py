from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, UserViewSet, RoleViewSet,
    BusinessElementViewSet, AccessRoleRuleViewSet, SessionViewSet
)
from .business_views import ProductViewSet, OrderViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'business-elements', BusinessElementViewSet, basename='business-elements')
router.register(r'access-rules', AccessRoleRuleViewSet, basename='access-rules')
router.register(r'sessions', SessionViewSet, basename='sessions')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
