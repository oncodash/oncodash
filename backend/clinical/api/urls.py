from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClinicalViewSet

import logging
logger = logging.getLogger("django.oncodash.clinical")
logger.debug("Register clinical API URLs")

app_name = "clinical-api"

router = DefaultRouter()
router.register(r"data", ClinicalViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
