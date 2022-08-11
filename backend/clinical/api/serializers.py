from rest_framework import serializers

from clinical.models import ClinicalData


class ClinicalDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the clinical data specification.
    """

    class Meta:
        model = ClinicalData
        fields = "__all__"
