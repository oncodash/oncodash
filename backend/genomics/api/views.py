from rest_framework import viewsets

from genomics.api.serializers import SomaticVariantSerializer, CopyNumberAlterationSerializer, CGIMutationSerializer, CGICopyNumberAlterationSerializer, CGIFusionGeneSerializer, OncoKBAnnotationSerializer
from genomics.models import SomaticVariant, CopyNumberAlteration, Translocation, CGIMutation, OncoKBAnnotation, CGIFusionGene, \
    CGICopyNumberAlteration
from clin_overview.models import ClinicalData
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

class GenomicViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the genomic data of the patients. Provides
    `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, patient_id=None):

        oncokb_queryset = OncoKBAnnotation.objects.all().filter(patient_id=patient_id)

        putative_functionally_relevant_variants = oncokb_queryset.filter(highestPrognosticImplicationLevel__in=["LEVEL_1","LEVEL_2","LEVEL_3"])
        variants_of_uknown_functional_significance = oncokb_queryset.filter(highestPrognosticImplicationLevel__in=["LEVEL_4","LEVEL_5"])
        putative_functionally_neutral_variants = oncokb_queryset.filter(highestPrognosticImplicationLevel__in=["LEVEL_6"])
        other_alterations = oncokb_queryset.filter(highestPrognosticImplicationLevel__in=["LEVEL_7","NULL"])

        data = {
            "genomic": {
                "putative_functionally_relevant_variant": [putative_functionally_relevant_variants.count(), "PUTATIVE FUNCTIONALLY RELEVANT VARIANT"],
                "variants_of_uknown_functional_significance": [variants_of_uknown_functional_significance.count(), "VARIANTS OF UKNOWN FUNCTIONAL SIGNIFICANCE"],
                "putative_functionally_neutral_variants": [putative_functionally_neutral_variants.count(), "PUTATIVE FUNCTIONALLY NEUTRAL VARIANTS"],
                "other_alterations": [other_alterations.count(), "OTHER ALTERATIONS"],
                },
            "putative_functionally_relevant_variant": {},
            "variants_of_uknown_functional_significance": {},
            "putative_functionally_neutral_variants": {},
            "other_alterations": {}
        }

        if putative_functionally_relevant_variants.count() > 0:
            for gene in putative_functionally_relevant_variants.values('hugoSymbol').distinct():
                sample_info = "Plasma sample"
                treatment_phase = "Primary" # ClinicalData.objects.all().filter(patient_id=patient_id)[0].current_treatment_phase
                mutation_affects = "DNA"
                tumor_purity = "40"
                reported_sensitivity = "Nirabarib"
                gene_name = gene['hugoSymbol']

                alterations_qs = putative_functionally_relevant_variants.filter(hugoSymbol=gene_name)
                # New gene

                gene_data = {
                    "description": f"{alterations_qs[0].geneSummary}",
                    "alterations": []
                }
                alt_count = alterations_qs.count()

                alterations = [
                    {
                        "name": f"{alterations_qs[i].alteration}",
                        "description": f"{alterations_qs[i].mutationEffectDescription}",
                        "row": [
                            {
                                "samples_ids": f"{alterations_qs[i].sample_id}",
                                "samples_info": f"{sample_info}",
                                "treatment_phase": f"{treatment_phase}",
                                "tumor_purity": f"{tumor_purity}%",
                                "mutation_affects": f"{mutation_affects}",
                                "reported_sensitivity": f"{reported_sensitivity}",
                            }
                        ]
                    }
                    for i in range(alt_count)
                ]
                gene_data["alterations"] = alterations
                data["putative_functionally_relevant_variant"][gene_name] = gene_data

        return Response(json.dumps(data, indent=4))

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