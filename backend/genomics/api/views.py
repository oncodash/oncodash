import logging

from rest_framework import viewsets

from genomics.api.serializers import SomaticVariantSerializer, CopyNumberAlterationSerializer, CGIMutationSerializer, CGICopyNumberAlterationSerializer, CGIFusionGeneSerializer, OncoKBAnnotationSerializer
from genomics.models import SomaticVariant, CopyNumberAlteration, CGIMutation, CGICopyNumberAlteration, CGIFusionGene, \
    CGIDrugPrescriptions, OncoKBAnnotation, AlterationType, ActionableTarget, CNAscatEstimate
from clin_overview.models import TimelineRecord
import genomics.management.commands.genomic_db_query_utils as gdbq
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse

class GenomicViewSet(viewsets.GenericViewSet):
    """
    API endpoint for the genomic data of the patients. Provides
    `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """
    permission_classes = (IsAuthenticated,)
    queryset = OncoKBAnnotation.objects.all()
    def retrieve(self, request, pk=None):

        oncokb_queryset = OncoKBAnnotation.objects.all().filter(patient_id=pk)
        ascat_ests_qs = CNAscatEstimate.objects.all().filter(patient_id=pk)
        timeline_qs = TimelineRecord.objects.all()
        # Evidence levels https://www.oncokb.org/api/v1/info
        putative_functionally_relevant_variants = oncokb_queryset.filter(Q(highestSensitiveLevel=["LEVEL_1","LEVEL_2","LEVEL_3A","LEVEL_3B"]) | Q(highestFdaLevel__in=["LEVEL_Fda1","LEVEL_Fda2","LEVEL_Fda3"]))
        variants_of_uknown_functional_significance = oncokb_queryset.filter(Q(highestPrognosticImplicationLevel__in=["LEVEL_Px1","LEVEL_Px2","LEVEL_Px3"]) | Q(highestDiagnosticImplicationLevel__in=["LEVEL_Dx1","LEVEL_Dx2","LEVEL_Dx3"]) | Q(highestSensitiveLevel=["LEVEL_4"]))
        putative_functionally_neutral_variants = oncokb_queryset.filter(highestResistanceLevel__in=["LEVEL_R1","LEVEL_R2"])
        other_alterations = oncokb_queryset.filter(Q(highestPrognosticImplicationLevel=None) | Q(highestDiagnosticImplicationLevel=None) | Q(highestFdaLevel=None)).exclude(oncogenic="Unknown")
        data = {
            'genomic': {
                'putative_functionally_relevant_variant': [putative_functionally_relevant_variants.count(), 'PUTATIVE FUNCTIONALLY RELEVANT VARIANT'],
                'variants_of_uknown_functional_significance': [variants_of_uknown_functional_significance.count(), 'VARIANTS OF UKNOWN FUNCTIONAL SIGNIFICANCE'],
                'putative_functionally_neutral_variants': [putative_functionally_neutral_variants.count(), 'PUTATIVE FUNCTIONALLY NEUTRAL VARIANTS'],
                'other_alterations': [other_alterations.count(), 'OTHER ALTERATIONS'],
                },
            'putative_functionally_relevant_variant': {},
            'variants_of_uknown_functional_significance': {},
            'putative_functionally_neutral_variants': {},
            'other_alterations': {}
        }
        if putative_functionally_relevant_variants.count() > 0:
            for gene in putative_functionally_relevant_variants.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                alterations_qs = putative_functionally_relevant_variants.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{alterations_qs[0].geneSummary}',
                    'alterations': []
                }
                alt_count = alterations_qs.count()

                alterations = [
                    {
                        'name': f'{alterations_qs[i].alteration}',
                        'description': f'{alterations_qs[i].mutationEffectDescription}',
                        'row': [
                            {
                                'samples_ids': f'{alterations_qs[i].sample_id}',
                                'samples_info': f'{get_sample_info(alterations_qs[i].sample_id, timeline_qs)}',
                                'treatment_phase': f'{get_phase(alterations_qs[i].sample_id)}',
                                'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=alterations_qs[i].sample_id))}',
                                'mutation_affects': f'{get_sample_type(alterations_qs[i].sample_id)}',
                                'reported_sensitivity': f'{alterations_qs[i].treatments}',
                            }
                        ]
                    }
                    for i in range(alt_count)
                ]
                gene_data['alterations'] = alterations
                data['putative_functionally_relevant_variant'][gene_name] = gene_data

        if variants_of_uknown_functional_significance.count() > 0:
            for gene in variants_of_uknown_functional_significance.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                alterations_qs = variants_of_uknown_functional_significance.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{alterations_qs[0].geneSummary}',
                    'alterations': []
                }
                alt_count = alterations_qs.count()

                alterations = [
                    {
                        'name': f'{alterations_qs[i].alteration}',
                        'description': f'{alterations_qs[i].mutationEffectDescription}',
                        'row': [
                            {
                                'samples_ids': f'{alterations_qs[i].sample_id}',
                                'samples_info': f'{get_sample_info(alterations_qs[i].sample_id, timeline_qs)}',
                                'treatment_phase': f'{get_phase(alterations_qs[i].sample_id)}',
                                'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=alterations_qs[i].sample_id))}',
                                'mutation_affects': f'{get_sample_type(alterations_qs[i].sample_id)}',
                                'reported_sensitivity': f'{alterations_qs[i].treatments}'.replace(' ', '_').replace(';', ' '),
                            }
                        ]
                    }
                    for i in range(alt_count)
                ]
                gene_data['alterations'] = alterations
                data['variants_of_uknown_functional_significance'][gene_name] = gene_data

        if putative_functionally_neutral_variants.count() > 0:
            for gene in putative_functionally_neutral_variants.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                alterations_qs = putative_functionally_neutral_variants.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{alterations_qs[0].geneSummary}',
                    'alterations': []
                }
                alt_count = alterations_qs.count()

                alterations = [
                    {
                        'name': f'{alterations_qs[i].alteration}',
                        'description': f'{alterations_qs[i].mutationEffectDescription}',
                        'row': [
                            {
                                'samples_ids': f'{alterations_qs[i].sample_id}',
                                'samples_info': f'{get_sample_info(alterations_qs[i].sample_id, timeline_qs)}',
                                'treatment_phase': f'{get_phase(alterations_qs[i].sample_id)}',
                                'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=alterations_qs[i].sample_id))}',
                                'mutation_affects': f'{get_sample_type(alterations_qs[i].sample_id)}',
                                'reported_sensitivity': f'{alterations_qs[i].treatments}'.replace(' ', '_').replace(';', ' '),
                            }
                        ]
                    }
                    for i in range(alt_count)
                ]
                gene_data['alterations'] = alterations
                data['putative_functionally_neutral_variants'][gene_name] = gene_data

        if other_alterations.count() > 0:
            for gene in other_alterations.values('hugoSymbol').distinct():

                sample_info = ''
                gene_name = gene['hugoSymbol']

                alterations_qs = other_alterations.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{alterations_qs[0].geneSummary}',
                    'alterations': []
                }
                alt_count = alterations_qs.count()

                alterations = [
                    {
                        'name': f'{alterations_qs[i].alteration}',
                        'description': f'{alterations_qs[i].mutationEffectDescription}',
                        'row': [
                            {
                                'samples_ids': f'{alterations_qs[i].sample_id}',
                                'samples_info': f'{get_sample_info(alterations_qs[i].sample_id, timeline_qs)}',
                                'treatment_phase': f'{get_phase(alterations_qs[i].sample_id)}',
                                'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=alterations_qs[i].sample_id))}',
                                'mutation_affects': f'{get_sample_type(alterations_qs[i].sample_id)}',
                                'reported_sensitivity': f'{alterations_qs[i].treatments}'.replace(' ', '_').replace(';', ' '),
                            }
                        ]
                    }
                    for i in range(alt_count)
                ]
                gene_data['alterations'] = alterations
                data['other_alterations'][gene_name] = gene_data

        #return Response(json.dumps(data)) # use a serializer!
        return JsonResponse(data)

def get_purity(est_objs):
    if est_objs:
        if est_objs[0].purity > 0.0:
            return str('%.2f' % (100*float(est_objs[0].purity)))+"%"
        else:
            return "NA"
    else:
        return "NA"

def get_phase(sample_id):
    p = sample_id.split("_")[1]
    if p[0] == 'p':
        return "Primary"
    if p[0] == 'i':
        return "Interval"
    if p[0] == 'r':
        return "Relapse"

def get_sample_type(sample_id):
    if sample_id.find("BDNA") > 0:
        return "DNA"
    if sample_id.find("DNA") > 0:
        return "DNA"
    if sample_id.find("RNA") > 0:
        return "RNA"

def get_sample_info(sample_id, timeline_qs):
    ss = sample_id.split("_")
    name = str(ss[0]+"_"+ss[1]).lower()
    res = timeline_qs.filter(name__icontains=name)
    if res:
        event = res[0].event
        if event == "tyks_plasma":
            return "Plasma"
        if event == "fresh_sample" or event == "fresh_sample_sequenced":
            return "Fresh tissue"
    else:
        return "NA"

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
