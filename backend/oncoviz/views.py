from rest_framework import viewsets

from oncoviz.serializers import NetworkSerializer
from core.models import NetworkSpec


class NetworkViewSet(viewsets.ModelViewSet):
    """
    Network viewset that provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = NetworkSpec.objects.all()
    serializer_class = NetworkSerializer