from rest_framework import serializers

from genomics.models import SomaticVariant
from genomics.models import Translocation
from genomics.models import CopyNumberAlteration
from genomics.models import CGIMutation
from genomics.models import CGIFusionGene
from genomics.models import CGICopyNumberAlteration
from genomics.models import OncoKBAnnotation
from genomics.models import ActionableTarget
from genomics.models import CNAscatEstimate
class SomaticVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = SomaticVariant
        fields = "__all__"

class ActionableTargetSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = ActionableTarget
        fields = "__all__"

class TranslocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = Translocation
        fields = "__all__"

class CopyNumberAlterationSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = CopyNumberAlteration
        fields = "__all__"

class CGIMutationSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = CGIMutation
        fields = "__all__"

class CGICopyNumberAlterationSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = CGICopyNumberAlteration
        fields = "__all__"

class CGIFusionGeneSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = CGIFusionGene
        fields = "__all__"

class OncoKBAnnotationSerializer(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = OncoKBAnnotation
        fields = "__all__"

class CNAscatEstimate(serializers.ModelSerializer):
    """
    Serializer for the genomic data specification.
    """

    class Meta:
        model = CNAscatEstimate
        fields = "__all__"
