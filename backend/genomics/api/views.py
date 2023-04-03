from rest_framework import viewsets

from .serializers import SomaticVariantSerializer, CopyNumberAlterationSerializer, CGIMutationSerializer, CGICopyNumberAlterationSerializer, CGIFusionGeneSerializer, OncoKBAnnotationSerializer
from ..models import SomaticVariant, CopyNumberAlteration, Translocation, CGIMutation, OncoKBAnnotation, CGIFusionGene, \
    CGICopyNumberAlteration
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# TODO: Async calls to external db APIs https://testdriven.io/blog/django-async-views/
class SNVViewSet(viewsets.ModelViewSet):
    serializer_class = SomaticVariantSerializer
    queryset = SomaticVariant.objects.all()

    def retrieve(self, request, patient_id=None):
        serializer_class = SomaticVariantSerializer

        # somaticset = SomaticVariant.objects.filter(patient=patient_id)
        queryset = SomaticVariant.objects.all()
        snvs = get_object_or_404(queryset, patient_id=patient_id)

        return Response(serializer_class(snvs).data)


class CNAViewSet(viewsets.ModelViewSet):
    serializer_class = CopyNumberAlterationSerializer
    queryset = CopyNumberAlteration.objects.all()

    def retrieve(self, request, patient_id=None):
        serializer_class = CopyNumberAlterationSerializer

        queryset = CopyNumberAlteration.objects.all()
        records = get_object_or_404(queryset, patient_id=patient_id)

        return Response(serializer_class(records).data)

class OncoKBViewSet(viewsets.ModelViewSet):
    serializer_class = OncoKBAnnotationSerializer
    queryset = OncoKBAnnotation.objects.all()

    def retrieve(self, request, patient_id=None):
        serializer_class = OncoKBAnnotationSerializer

        queryset = OncoKBAnnotation.objects.all()
        records = get_object_or_404(queryset, patient_id=patient_id)

        return Response(serializer_class(records).data)

class CGIMutationViewSet(viewsets.ModelViewSet):
    serializer_class = CGIMutationSerializer
    queryset = CGIMutation.objects.all()

    def retrieve(self, request, patient_id=None):
        serializer_class = CGIMutationSerializer

        queryset = CGIMutation.objects.all()
        records = get_object_or_404(queryset, patient_id=patient_id)

        return Response(serializer_class(records).data)

class CGICopyNumberAlterationViewSet(viewsets.ModelViewSet):
    serializer_class = CGICopyNumberAlterationSerializer
    queryset = CGICopyNumberAlteration.objects.all()

    def retrieve(self, request, patient_id=None):
        serializer_class = CGICopyNumberAlterationSerializer

        queryset = CGICopyNumberAlteration.objects.all()
        records = get_object_or_404(queryset, patient_id=patient_id)

        return Response(serializer_class(records).data)

class CGIFusionGeneViewSet(viewsets.ModelViewSet):
    serializer_class = CGIFusionGeneSerializer
    queryset = CGIFusionGene.objects.all()

    def retrieve(self, request, patient_id=None):
        serializer_class = CGIFusionGeneSerializer

        queryset = CGIFusionGene.objects.all()
        records = get_object_or_404(queryset, patient_id=patient_id)

        return Response(serializer_class(records).data)

# class TranslocationViewSet(viewsets.ModelViewSet):
#     serializer_class = TranslocationSerializer
#     queryset = Translocation.objects.all()
#
#     def retrieve(self, request, patient_id=None):
#         serializer_class = TranslocationSerializer
#
#         queryset = Translocation.objects.all()
#         records = get_object_or_404(queryset, patient_id=patient_id)
#
#         return Response(serializer_class(records).data)