from rest_framework import serializers

from core.models import NetworkSpec


class NetworkSerializer(serializers.ModelSerializer):
    """
    Serializer for the oncodash causal network specification
    """
    class Meta:
        model = NetworkSpec
        fields = ['id', 'spec']
