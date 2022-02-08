from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClinicalViewSet


app_name = "clin_overview"

router = DefaultRouter()
router.register(r"data", ClinicalViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
