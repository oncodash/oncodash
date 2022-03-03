from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NetworkViewSet

import logging
logger = logging.getLogger(__name__)
logger.debug("Register explainer")

app_name = 'explainer'

router = DefaultRouter()
router.register(r'networks', NetworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

