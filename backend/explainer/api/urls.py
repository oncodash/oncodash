from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NetworkViewSet

import logging
logger = logging.getLogger("django.oncodash.explainer")
logger.debug("Register explainer URLs")

app_name = 'explainer-api'

router = DefaultRouter()
router.register(r'networks', NetworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

