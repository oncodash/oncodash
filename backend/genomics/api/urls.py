from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SNVViewSet, CNAViewSet, OncoKBViewSet, CGICopyNumberAlterationViewSet, CGIMutationViewSet, CGIFusionGeneViewSet

import logging
logger = logging.getLogger(__name__)
logger.debug("Register genomics view")

app_name = 'genomics'

router = DefaultRouter()
router.register(r'snvs', SNVViewSet)
router.register(r'cnas', CNAViewSet)
router.register(r'oncokbannotations', OncoKBViewSet)
router.register(r'cgicnas', CGICopyNumberAlterationViewSet)
router.register(r'cgisnvs', CGIMutationViewSet)
router.register(r'cgifus', CGIFusionGeneViewSet)


#router.register(r'translocations', TranslocationViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

