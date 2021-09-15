from django.urls import path, include
from rest_framework.routers import DefaultRouter

from oncoviz import views


app_name = 'oncoviz'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'network', views.NetworkViewSet, 'network')

urlpatterns = [
    path('', include(router.urls)),
]