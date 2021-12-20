from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NetworkViewSet


app_name = 'explainer'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'network', NetworkViewSet, 'network')

urlpatterns = [
    path('', include(router.urls)),
]
