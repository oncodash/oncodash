from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClinicalViewSet, TimelineViewSet


app_name = "clin_overview"

router = DefaultRouter()
router.register(r"data", ClinicalViewSet)
router.register(r"timeline", TimelineViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
