from rest_framework import viewsets

from .serializers import ClinicalDataSerializer
from ..models import ClinicalData


class ClinicalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the causal networks of the patients. Provides
    `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """
    queryset = ClinicalData.objects.all()
    serializer_class = ClinicalDataSerializer