from django.urls import path, include
from rest_framework.routers import DefaultRouter

from explainer import views


app_name = 'explainer'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'network', views.NetworkViewSet, 'network')

urlpatterns = [
    path('', include(router.urls)),
]
