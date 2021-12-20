from rest_framework import viewsets

from .serializers import NetworkSerializer
from ..models import NetworkSpec


class NetworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the causal network. Provides `list`, `create`,
    `retrieve`, `update` and `destroy` actions.
    """
    queryset = NetworkSpec.objects.all()
    serializer_class = NetworkSerializer
