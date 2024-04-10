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
import random

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
        actionable_aberrations = oncokb_queryset.filter(Q(highestSensitiveLevel__in=["LEVEL_1","LEVEL_2"]) or Q(highestResistanceLevel__in=["LEVEL_R1"]))
        putative_functionally_relevant_variants = oncokb_queryset.filter(Q(highestSensitiveLevel__in=["LEVEL_3A", "LEVEL_3B", "LEVEL_4"]) or Q(highestResistanceLevel__in=["LEVEL_R2"]))
        relevant_by_oncokb = actionable_aberrations | putative_functionally_relevant_variants
        rel = relevant_by_oncokb.values('hugoSymbol').distinct()
        other_variants = oncokb_queryset.exclude(hugoSymbol__in=rel).exclude(consequence="synonymous_variant").exclude(consequence="synonymous_variant").exclude(oncogenic="Unknown")

        samples_info = {
            'name': 'Sample info',
            'row': []
        }
        samples = ascat_ests_qs.values('sample').distinct()

        samplerows = [
            {
                'sample': f'{sample_id["sample"]}',
                'purity': f'{get_purity(ascat_ests_qs.filter(sample=sample_id["sample"]))}',
                'ploidy': f'{get_ploidy(ascat_ests_qs.filter(sample=sample_id["sample"]))}',
                'tumor_site': f'{get_site_info(sample_id["sample"])}',
                'sample_time': f'{get_phase(sample_id["sample"])}',
                'sample_type': f'{get_sample_type(sample_id["sample"])}'
            }
            for sample_id in samples
        ]
        samples_info['row'] = samplerows

        data = {
            'genomic': {
                'actionable_aberrations': [actionable_aberrations.count(), 'ACTIONABLE ABERRATIONS'],
                'putative_functionally_relevant_variants': [putative_functionally_relevant_variants.count(), 'PUTATIVE FUNCTIONALLY RELEVANT VARIANTS'],
                'other_variants': [other_variants.count(), 'OTHER VARIANTS'],
                },
            'samples_info': samples_info,
            'actionable_aberrations': {},
            'putative_functionally_relevant_variants': {},
            'other_variants': {},
        }

        if actionable_aberrations.count() > 0:
            for gene in actionable_aberrations.values('hugoSymbol').distinct():

                gene_name = gene['hugoSymbol']

                gene_qs = actionable_aberrations.filter(hugoSymbol=gene_name)

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
                        'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[0])}',
                        'row': []
                    }
                    if alteration_name == "Amplification" or alteration_name == "Deletion":
                        cnas = CopyNumberAlteration.objects.all().filter(patient_id=pk).filter(gene=gene_name)
                        cnc = cnas.count()
                        alteration_rows = [
                            {
                                'sample': f'{cnas[i].sample_id}',
                                'nMajor': f'{cnas[i].nMajor}',
                                'nMinor': f'{cnas[i].nMinor}'
                            }
                            for i in range(cnc)
                        ]
                        alteration_data['row'] = alteration_rows
                    else:
                        alteration_rows = [
                            {
                                'samples': f'{grouped_alterations_qs[i].sample_id}',
                                'AD.0': f'{grouped_alterations_qs[i].ad0}',
                                'AD.1': f'{grouped_alterations_qs[i].ad1}',
                                'DP': f'{grouped_alterations_qs[i].dp}',
                                'AF': f'{grouped_alterations_qs[i].af}',
                                'nMajor': f'{grouped_alterations_qs[i].nMajor}',
                                'nMinor': f'{grouped_alterations_qs[i].nMinor}',
                                'LOHstatus': f'{grouped_alterations_qs[i].lohstatus}',
                                'expHomCI.cover': f'{grouped_alterations_qs[i].exphomci}',
                                #'estimated_homogeneity': f'{get_homogeneity_est(af)}',
                            }
                            for i in range(alts_count)
                        ]
                        alteration_data['row'] = alteration_rows

                    gene_data['alterations'].append(alteration_data)
                data['actionable_aberrations'][gene_name] = gene_data

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
                        'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[0])}',
                        'row': []
                    }
                    if alteration_name == "Amplification" or alteration_name == "Deletion":
                        cnas = CopyNumberAlteration.objects.all().filter(patient_id=pk).filter(gene=gene_name)
                        cnc = cnas.count()
                        alteration_rows = [
                            {
                                'sample': f'{cnas[i].sample_id}',
                                'nMajor': f'{cnas[i].nMajor}',
                                'nMinor': f'{cnas[i].nMinor}'
                            }
                            for i in range(cnc)
                        ]
                        alteration_data['row'] = alteration_rows
                    else:
                        alteration_rows = [
                            {
                                'samples': f'{grouped_alterations_qs[i].sample_id}',
                                'AD.0': f'{grouped_alterations_qs[i].ad0}',
                                'AD.1': f'{grouped_alterations_qs[i].ad1}',
                                'DP': f'{grouped_alterations_qs[i].dp}',
                                'AF': f'{grouped_alterations_qs[i].af}',
                                'nMajor': f'{grouped_alterations_qs[i].nMajor}',
                                'nMinor': f'{grouped_alterations_qs[i].nMinor}',
                                'LOHstatus': f'{grouped_alterations_qs[i].lohstatus}',
                                'expHomCI.cover': f'{grouped_alterations_qs[i].exphomci}',
                                # 'estimated_homogeneity': f'{get_homogeneity_est(af)}',
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
                        'reported_sensitivity': f'{get_sensitivity(grouped_alterations_qs[0])}',
                        'row': []
                    }
                    if alteration_name == "Amplification" or alteration_name == "Deletion":
                        cnas = CopyNumberAlteration.objects.all().filter(patient_id=pk).filter(gene=gene_name)
                        cnc = cnas.count()
                        alteration_rows = [
                            {
                                'sample': f'{cnas[i].sample_id}',
                                'nMajor': f'{cnas[i].nMajor}',
                                'nMinor': f'{cnas[i].nMinor}'
                            }
                            for i in range(cnc)
                        ]
                        alteration_data['row'] = alteration_rows
                    else:
                        alteration_rows = [
                            {
                                'samples': f'{grouped_alterations_qs[i].sample_id}',
                                'AD.0': f'{grouped_alterations_qs[i].ad0}',
                                'AD.1': f'{grouped_alterations_qs[i].ad1}',
                                'DP': f'{grouped_alterations_qs[i].dp}',
                                'AF': f'{grouped_alterations_qs[i].af}',
                                'nMajor': f'{grouped_alterations_qs[i].nMajor}',
                                'nMinor': f'{grouped_alterations_qs[i].nMinor}',
                                'LOHstatus': f'{grouped_alterations_qs[i].lohstatus}',
                                'expHomCI.cover': f'{grouped_alterations_qs[i].exphomci}',
                                # 'estimated_homogeneity': f'{get_homogeneity_est(af)}',
                            }
                            for i in range(alts_count)
                        ]
                        alteration_data['row'] = alteration_rows

                    gene_data['alterations'].append(alteration_data)
                data['other_variants'][gene_name] = gene_data

        #return Response(json.dumps(data, indent=4))  # use a serializer!
        return JsonResponse(data)

def get_homogeneity_est(af):
    # mutate(totalCN=nMajor + nMinor) % > %
    # mutate(expHomAF=expectedAF(totalCN, totalCN, purity)) % > %
    # mutate(expHomCI.lo = qbinom(0.025, DP, expHomAF)) % > %
    # mutate(expHomCI.hi = qbinom(0.975, DP, expHomAF)) % > %
    # mutate(expHomCI.cover = expHomCI.lo <= AD.1) % > %  # & AD.1 <= expHomCI.hi ### the comparison to upper CI boundary is irrelevant and leads to wrong interpretation
    # mutate(expHom.pbinom.lower = pbinom(AD.1, DP, expHomAF))
    return True if af >= 0.5 else False

def get_ploidy(est_objs):
    if est_objs:
        if est_objs[0].ploidy >= 0.0:
            return str('%.4f' % (float(est_objs[0].ploidy)))
        else:
            return "NA"
    else:
        return "NA"

def get_purity(est_objs):
    if est_objs:
        if est_objs[0].purity >= 0.0:
            return str('%.2f' % (100*float(est_objs[0].purity)))+"%"
        else:
            return "NA"
    else:
        return "NA"

def get_sensitivity(est_objs):
    if est_objs:
        if est_objs.highestResistanceLevel is not None and est_objs.treatments:
            return "Resistant: ",str(est_objs.treatments.replace(' ', '_').replace(';', ' '))
        if est_objs.highestSensitiveLevel is not None and est_objs.treatments:
            return "Responsive: "+str(est_objs.treatments.replace(' ', '_').replace(';', ' '))
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
    return "NA"

def get_sample_type(sample_id):
    if sample_id.find("BDNA") > 0:
        return "DNA"
    if sample_id.find("DNA") > 0:
        return "DNA"
    if sample_id.find("RNA") > 0:
        return "RNA"

def get_sample_type_info(sample_id, timeline_qs):
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
def get_site_info(sample_id):
    print(sample_id)
    ss = sample_id.split("_")
    site = str(ss[1][1:])
    if site.startswith("BDNA"):
        site = None
    if site:
        return site
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
