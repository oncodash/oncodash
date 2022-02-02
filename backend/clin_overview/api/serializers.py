from rest_framework import serializers

from clin_overview.models import ClinicalData


class ClinicalDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the oncodash causal network specification
    """
    class Meta:
        model = ClinicalData
        fields = [] # fill me