from rest_framework import serializers

from clin_overview.models import ClinicalData, TimelineRecord


class ClinicalDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the clinical data specification.
    """
    #x  time_series = serializers.SerializerMethodField(source='time_series')
    # bmi = serializers.serializerMethodField();

    class Meta:
        model = ClinicalData
        fields = "__all__"

class TimelineRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the clinical data specification.
    """

    class Meta:
        model = TimelineRecord
        fields = "__all__"
