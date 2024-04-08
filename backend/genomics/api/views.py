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
        cgi_biomarkers_queryset = CGIDrugPrescriptions.objects.all().filter(patient_id=pk)
        ascat_ests_qs = CNAscatEstimate.objects.all().filter(patient_id=pk)
        timeline_qs = TimelineRecord.objects.all()
        # Evidence levels https://www.oncokb.org/api/v1/info
        actionable_relevant_targets = oncokb_queryset.filter(Q(highestSensitiveLevel__in=["LEVEL_1","LEVEL_2"]) or Q(highestResistanceLevel__in=["LEVEL_R1"]))
        putative_functionally_relevant_variants = oncokb_queryset.filter(Q(highestSensitiveLevel__in=["LEVEL_3A", "LEVEL_3B", "LEVEL_4"]) or Q(highestResistanceLevel__in=["LEVEL_R2"]))
        relevant_by_oncokb = actionable_relevant_targets | putative_functionally_relevant_variants
        rel = relevant_by_oncokb.values('hugoSymbol').distinct()
        other_variants = oncokb_queryset.exclude(hugoSymbol__in=rel).exclude(consequence="synonymous_variant").exclude(consequence="synonymous_variant").exclude(oncogenic="Unknown")
        #other_variants = oncokb_queryset.filter((Q(highestResistanceLevel=None) & Q(highestSensitiveLevel=None) & (Q(alteration="Amplification") | Q(alteration="Deletion")))
        #                                        | (Q(highestResistanceLevel=None) & Q(highestSensitiveLevel=None) & ~ (Q(alteration="Amplification") & ~ Q(alteration="Deletion")) & ~ Q(oncogenic="Unknown"))).exclude(consequence="synonymous_variant")

        data = {
            'genomic': {
                'actionable_relevant_targets': [actionable_relevant_targets.count(), 'ACTIONABLE TARGETS'],
                'putative_functionally_relevant_variants': [putative_functionally_relevant_variants.count(), 'PUTATIVE FUNCTIONALLY RELEVANT VARIANTS'],
                'other_variants': [other_variants.count(), 'OTHER VARIANTS'],
                },
            'actionable_relevant_targets': {},
            'putative_functionally_relevant_variants': {},
            'other_variants': {},
        }
        #cgi_genes = []
        #for alt in cgi_biomarkers_queryset.values('alterations').distinct():
        #    cgi_genes.append(alt.split(':')[0])

        #oncokb_missing = cgi_genes not in all_oncokb_variants.values('hugoSymbol').distinct()
        if actionable_relevant_targets.count() > 0:
            for gene in actionable_relevant_targets.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                gene_qs = actionable_relevant_targets.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{gene_qs[0].geneSummary}',
                    'alterations': []
                }
                for alteration_name in gene_qs.values('alteration').distinct():
                    alteration_name = alteration_name.get('alteration')

                    grouped_alterations_qs = gene_qs.filter(alteration=alteration_name)

                    alts_count = grouped_alterations_qs.count()
                    alteration_data = {
                        'name': f'{alteration_name}',
                        'description': f'{grouped_alterations_qs[0].mutationEffectDescription}',
                        'row': []
                    }
                    alteration_rows = [
                        {
                            'samples_ids': f'{grouped_alterations_qs[i].sample_id}',
                            'samples_info': f'{get_sample_info(grouped_alterations_qs[i].sample_id, timeline_qs)}',
                            'treatment_phase': f'{get_phase(grouped_alterations_qs[i].sample_id)}',
                            'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=grouped_alterations_qs[i].sample_id))}',
                            'mutation_affects': f'{get_sample_type(grouped_alterations_qs[i].sample_id)}',
                            'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[i])}',
                        }
                        for i in range(alts_count)
                    ]
                    alteration_data['row'] = alteration_rows

                    gene_data['alterations'].append(alteration_data)
                data['actionable_relevant_targets'][gene_name] = gene_data

        if putative_functionally_relevant_variants.count() > 0:
            for gene in putative_functionally_relevant_variants.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                gene_qs = putative_functionally_relevant_variants.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{gene_qs[0].geneSummary}',
                    'alterations': []
                }
                for alteration_name in gene_qs.values('alteration').distinct():
                    alteration_name = alteration_name.get('alteration')

                    grouped_alterations_qs = gene_qs.filter(alteration=alteration_name)
                    alts_count = grouped_alterations_qs.count()
                    alteration_data = {
                        'name': f'{alteration_name}',
                        'description': f'{grouped_alterations_qs[0].mutationEffectDescription}',
                        'row': []
                    }
                    alteration_rows = [
                        {
                            'samples_ids': f'{grouped_alterations_qs[i].sample_id}',
                            'samples_info': f'{get_sample_info(grouped_alterations_qs[i].sample_id, timeline_qs)}',
                            'treatment_phase': f'{get_phase(grouped_alterations_qs[i].sample_id)}',
                            'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=grouped_alterations_qs[i].sample_id))}',
                            'mutation_affects': f'{get_sample_type(grouped_alterations_qs[i].sample_id)}',
                            'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[i])}',
                        }
                        for i in range(alts_count)
                    ]
                    alteration_data['row'] = alteration_rows

                    gene_data['alterations'].append(alteration_data)
                data['putative_functionally_relevant_variants'][gene_name] = gene_data

        if other_variants.count() > 0:
            for gene in other_variants.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                gene_qs = other_variants.filter(hugoSymbol=gene_name)

                gene_data = {
                    'description': f'{gene_qs[0].geneSummary}',
                    'alterations': []
                }
                for alteration_name in gene_qs.values('alteration').distinct():
                    alteration_name = alteration_name.get('alteration')

                    grouped_alterations_qs = gene_qs.filter(alteration=alteration_name)
                    alts_count = grouped_alterations_qs.count()
                    alteration_data = {
                        'name': f'{alteration_name}',
                        'description': f'{grouped_alterations_qs[0].mutationEffectDescription}',
                        'row': []
                    }
                    alteration_rows = [
                        {
                            'samples_ids': f'{grouped_alterations_qs[i].sample_id}',
                            'samples_info': f'{get_sample_info(grouped_alterations_qs[i].sample_id, timeline_qs)}',
                            'treatment_phase': f'{get_phase(grouped_alterations_qs[i].sample_id)}',
                            'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=grouped_alterations_qs[i].sample_id))}',
                            'mutation_affects': f'{get_sample_type(grouped_alterations_qs[i].sample_id)}',
                            'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[i])}',
                        }
                        for i in range(alts_count)
                    ]
                    alteration_data['row'] = alteration_rows

                    gene_data['alterations'].append(alteration_data)
                data['other_variants'][gene_name] = gene_data

        # for gene in cgi_genes:
        #     gene_qs = cgi_biomarkers_queryset.filter(Q(alterations__contains=gene) and (Q(tumor_type="OV") or Q(tumor_type="OVSE")))
        #     if len(gene_qs) == 0:
        #         gene_qs = cgi_biomarkers_queryset.filter(Q(alterations__contains=gene) and Q(tumor_type="CANCER"))
        #     drugs = ""
        #     for row in gene_qs:
        #         drugs = drugs+" "+row.drugs
        #     # TODO: if CGICopyNumber.objects.all().filter(patient_id=pk)
        #     gene_data = {
        #         'description': f'{gene}', #TODO: get gene description from ? perhaps store from oncokb
        #         'alterations': []
        #     }
        #     alteration_data = {
        #         'name': f'{gene_qs[0].alterations.replace(gene,"").replace(":","")}',
        #         'description': f'{gene_qs[0].source}',
        #         'row': []
        #     }
        #
        #     samples = gene_qs.values('sample').distinct()
        #     alts_count = len(samples)
        #
        #     alteration_rows = [
        #         {
        #             'samples_ids': f'{samples[i]}',
        #             'samples_info': f'{get_sample_info(samples[i], timeline_qs)}',
        #             'treatment_phase': f'{get_phase(samples[i])}',
        #             'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=samples[i]))}',
        #             'mutation_affects': f'{get_sample_type(samples[i])}',
        #             'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[i])}',
        #         }
        #         for i in range(alts_count)
        #     ]
        #         alteration_data['row'] = alteration_rows
        #
        #         gene_data['alterations'].append(alteration_data)
        #     data['other_variants'][gene_name] = gene_data

        # if other_alterations.count() > 0:
        #     for gene in other_alterations.values('hugoSymbol').distinct():
        #
        #         sample_info = ''
        #         gene_name = gene['hugoSymbol']
        #
        #         alterations_qs = other_alterations.filter(hugoSymbol=gene_name)
        #
        #         gene_data = {
        #             'description': f'{alterations_qs[0].geneSummary}',
        #             'alterations': []
        #         }
        #         alt_count = alterations_qs.count()
        #
        #         alterations = [
        #             {
        #                 'name': f'{alterations_qs[i].alteration}',
        #                 'description': f'{alterations_qs[i].mutationEffectDescription}',
        #                 'row': [
        #                     {
        #                         'samples_ids': f'{alterations_qs[i].sample_id}',
        #                         'samples_info': f'{get_sample_info(alterations_qs[i].sample_id, timeline_qs)}',
        #                         'treatment_phase': f'{get_phase(alterations_qs[i].sample_id)}',
        #                         'tumor_purity': f'{get_purity(ascat_ests_qs.filter(sample=alterations_qs[i].sample_id))}',
        #                         'mutation_affects': f'{get_sample_type(alterations_qs[i].sample_id)}',
        #                         'reported_sensitivity': f'{alterations_qs[i].treatments}'.replace(' ', '_').replace(';', ' '),
        #                     }
        #                 ]
        #             }
        #             for i in range(alt_count)
        #         ]
        #         gene_data['alterations'] = alterations
        #         data['other_alterations'][gene_name] = gene_data

        return Response(json.dumps(data, indent=4)) # use a serializer!
        #return JsonResponse(data)

def get_purity(est_objs):
    if est_objs:
        if est_objs[0].purity > 0.0:
            return str('%.2f' % (100*float(est_objs[0].purity)))+"%"
        else:
            return "NA"
    else:
        return "NA"

def get_sensitivity(est_objs):
    if est_objs:
        if est_objs.highestResistanceLevel is not None and est_objs.treatments:
            return "R: "+str(est_objs.treatments.replace(' ', '_').replace(';', ' '))
        if est_objs.highestSensitiveLevel is not None and est_objs.treatments:
            return "S: "+str(est_objs.treatments.replace(' ', '_').replace(';', ' '))
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
