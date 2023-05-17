import io
import time
import zipfile

import pandas as pd
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from genomics.models import SomaticVariant, CopyNumberAlteration, CGIMutation, CGICopyNumberAlteration, CGIFusionGene, \
    CGIDrugPrescriptions, OncoKBAnnotation, AlterationType
from django.db.models import Field, TextChoices
from django.db.models import Lookup
from datetime import datetime

class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

Field.register_lookup(NotEqual)

def handle_boolean_field(value, field=None, default=False):
    if str(value).lower() in ["yes", "t"]:
        return True
    elif str(value).lower() in ["no", "f"]:
        return False
    else:
        return None if field is None or field.__dict__["field"].null else default

def handle_float_field(value):
    return None if pd.isna(value) else float(value.replace(",", "."))

def handle_string_field(value):
    return None if pd.isna(value) else value

def handle_int_field(value):
    return None if pd.isna(value) else value

def handle_date_field(value):

    return None if pd.isna(value) else datetime.strptime(value, "%d/%m/%Y")

def get_cna(patient_id, gene_id):
    try:
        for rec in CopyNumberAlteration.objects.filter(patient_id=patient_id, gene_id=gene_id):
            return rec

    except Exception as e:
        print(e)
        print("No CNA", gene_id, "available in the database")

def get_snv(patient_id, ref_id):
    try:
        for rec in SomaticVariant.objects.filter(patient_id=patient_id, ref_id=ref_id):
            return rec

    except Exception as e:
        print(e)
        print("No SNV", ref_id, "available in the database")

def get_actionable_snvs_by_aaChangeRefGene(patient_id):
    try:
        return SomaticVariant.objects.filter(patient_id=patient_id).exclude(aaChangeRefGene=".")

    except Exception as e:
        print(e)
        print("No actionable SNV for patient ", patient_id, "available in the database")

def get_all_actionable_snvs_by_aaChangeRefGene():
    try:
        return SomaticVariant.objects.exclude(aaChangeRefGene=".")

    except Exception as e:
        print(e)
        print("No actionable SNVs available in the database")

def get_all_exonic_snvs_of_patient(patient_id):
    try:
        return SomaticVariant.objects.filter(patient_id=patient_id, funcRefGene="exonic")

    except Exception as e:
        print(e)
        print("No exonic SNV for patient ", patient_id, "available in the database")

def get_all_exonic_snvs():
    try:
        return SomaticVariant.objects.filter(funcRefGene="exonic")

    except Exception as e:
        print(e)
        print("No exonic SNVs available in the database")


def query_cgi_job(patient_id, jobid):

    # curl --request GET --url 'https://www.cancergenomeinterpreter.org/api/v1/de04a9b5f30b1cedb53e' --header "Authorization: ilari.maarala@helsinki.fi token" -G --data 'action=download'
    request_url = "https://www.cancergenomeinterpreter.org/api/v1/"
    cgitoken = settings.CGI_TOKEN
    cgilogin = settings.CGI_LOGIN
    header = dict(Authorization=cgilogin+' '+cgitoken)

    print("Request CGI job by id")
    payload = dict(action='download')
    response = requests.get(request_url+jobid, headers=header, params=payload)

    if (response.status_code == 200):
        z = zipfile.ZipFile(io.BytesIO(response.content))
        fnames=z.namelist()
        for fn in fnames:
            # reader = z.open(f)
            # for row in reader.readlines():
            #    print(row)
            z.extract(fn)
            df = pd.read_csv(fn, sep="\t")
            print(fn)
            print(df)

            #Response filenames
            #alterations.tsv
            #drug_prescription.tsv
            #fusion_analysis.tsv
            #biomarkers.tsv

            # Mutation Query
            # chr	pos	ref	alt
            # chr3	178936091	G	A

            # Mutation response
            #Sample ID	Gene	Protein Change	Oncogenic Summary	Oncogenic Prediction	External oncogenic annotation	Mutation	Consequence	Transcript	Strand	Type
            #input02	KCNMB2-AS1	--	non-protein affecting	non-protein affecting		chr3:178936091 G>A	non_coding_transcript_exon_variant	ENST00000668466	+	SNV

            if fn == "alterations.tsv":
                for index, row in df.iterrows():
                    try:
                        rec, created = CGIMutation.objects.get_or_create(
                            patient_id      = int(patient_id),
                            sample = handle_string_field(row["Sample ID"]),
                            gene  = handle_string_field(row["Gene"]),
                            protein_change   = handle_string_field(row["Protein Change"]),
                            oncogenic_summary    = handle_string_field(row["Oncogenic Summary"]),
                            oncogenic_prediction      = handle_string_field(row["Oncogenic Prediction"]),
                            ext_oncogenic_annotation  = handle_string_field(row["External oncogenic annotation"]),
                            mutation = handle_string_field(row["Mutation"]),
                            consequence = handle_string_field(row["Consequence"]),
                            transcript = handle_string_field(row["Transcript"]),
                            strand = handle_string_field(row["Strand"]),
                            type = handle_string_field(row["Type"])
                        )
                        rec.save()
                    except Exception as e:
                        print(e)
                        pass


            # CNA Query
            # gene	cna
            # ERBB2	AMP
            # CNA response
            # sample	gene	cna	predicted_in_tumors	known_in_tumors	gene_role	cancer	internal_id	driver	driver_statement	predicted_match	known_match
            # single_sample	ERBB2	AMP	CESC;ESCA;HNSC;LUAD;PAAD;STAD;UCEC	BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED	Act	OVE	0	known	known in: BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED
            if fn == "cna_analysis.tsv":
                for index, row in df.iterrows():
                    try:
                        rec, created = CGICopyNumberAlteration.objects.get_or_create(
                            patient_id   = int(patient_id),
                            sample = handle_string_field(row["sample"]),
                            gene = handle_string_field(row["gene"]),
                            cnatype = handle_string_field(row["cna"]),
                            predicted_in_tumors = handle_string_field(row["predicted_in_tumors"]),
                            known_in_tumors = handle_string_field(row["known_in_tumors"]),
                            gene_role = handle_string_field(row["gene_role"]),
                            cancer = handle_string_field(row["cancer"]),
                            driver = handle_string_field(row["driver"]),
                            driver_statement = handle_string_field(row["driver_statement"]),
                            predicted_match = handle_string_field(row["predicted_match"]),
                            known_match = handle_string_field(row["known_match"])
                        )
                        rec.save()
                    except Exception as e:
                        print(e)
                        pass
            # Fusion/Transloc Query
            # fus
            # BCR__ABL1
            # Fusion/Transloc response
            # sample	fus	effector_gene	gene_role	known_in_tumors	internal_id	cancer	driver	driver_statement	known_match
            # single_sample	ABL1__BCR	ABL1	Act	ALL;CML;CLL;AML;TCALL	0	OVE	known	known in: ALL;CML;CLL;AML;TCALL

            if fn == "fusion_analysis.tsv":
                for index, row in df.iterrows():
                    try:
                        rec, created = CGIFusionGene.objects.get_or_create(
                            patient_id   = int(patient_id),
                            sample = handle_string_field(row["sample"]),
                            fusiongene = handle_string_field(row["fus"]),
                            effector_gene = handle_string_field(row["effector_gene"]),
                            gene_role = handle_string_field(row["gene_role"]),
                            known_in_tumors = handle_string_field(row["known_in_tumors"]),
                            cancer = handle_string_field(row["cancer"]),
                            driver = handle_string_field(row["driver"]),
                            driver_statement = handle_string_field(row["driver_statement"]),
                            known_match = handle_string_field(row["known_match"])
                        )
                        rec.save()
                    except Exception as e:
                        print(e)
                        pass

            # Sample ID	Alterations	Biomarker	Drugs	Diseases	Response	Evidence	Match	Source	BioM	Resist.	Tumor type
            # single_sample	ABL1__BCR 	ABL1 (T315I,V299L,G250E,F317L)	Bosutinib (BCR-ABL inhibitor 3rd gen)	Acute lymphoblastic leukemia, Chronic myeloid leukemia	Resistant	A	NO	cgi	only gene		ALL, CML
            if fn == "biomarkers.tsv":
                for index, row in df.iterrows():
                    try:
                        rec, created = CGIDrugPrescriptions.objects.get_or_create(
                            patient_id  = int(patient_id),
                            sample = handle_string_field(row["Sample ID"]),
                            alterations = handle_string_field(row["Alterations"]),
                            biomarker = handle_string_field(row["Biomarker"]),
                            drugs = handle_string_field(row["Drugs"]),
                            diseases = handle_string_field(row["Diseases"]),
                            response = handle_string_field(row["Response"]),
                            evidence = handle_string_field(row["Evidence"]),
                            match = handle_boolean_field(row["Match"]),
                            source = handle_string_field(row["Source"]),
                            biom = handle_string_field(row["BioM"]),
                            resistance = handle_int_field(row["Resist."]),
                            tumor_type = handle_string_field(row["Tumor type"])
                        )
                        rec.save()
                    except Exception as e:
                        print(e)
                        pass
        return 1
    else:
        print("No CGI results available for job id: "+str(jobid))
        return 0

def generate_temp_cgi_query_files(snvs: [SomaticVariant], cnas: [CopyNumberAlteration], translocs: [str]):

    header = "chr\tpos\tref\talt\n"
    with open("./tmp/snvs.ext", "w") as file1:
        file1.write(header)
        for snv in snvs:
            row = snv.chromosome+'\t'+str(snv.position)+'\t'+snv.reference_allele+'\t'+snv.sample_allele+'\n'
            file1.write(row)
        file1.close()

    header = "gene\tcna\n"
    with open("./tmp/cnas.ext", "w") as file2:
        file2.write(header)
        for cna in cnas:
            row = cna.gene+'\t'+cna.CNstatus+'\n'
            file2.write(row)
        file2.close()

    header = "fus\n"
    with open("./tmp/fus.ext", "w") as file3:
        file3.write(header)
        for transloc in translocs:
            row = transloc+'\n'
            file3.write(row)
        file3.close()


def launch_cgi_job_with_mulitple_variant_types(mutations_file, cnas_file, transloc_file, cancer_type, reference):

    request_url = "https://www.cancergenomeinterpreter.org/api/v1"
    login = settings.CGI_LOGIN
    token = settings.CGI_TOKEN
    header = dict(Authorization=login+' '+token)

    print("Request CGI")
    payload = dict(cancer_type=cancer_type, title='Title', reference=reference)
    # CGI api requires every type mutation files to be provided
    files = dict()
    if mutations_file != None:
        files['mutations'] = open(mutations_file, 'rb')
    if cnas_file != None:
        files['cnas'] = open(cnas_file, 'rb')
    if transloc_file != None:
        files['translocations'] = open(transloc_file, 'rb')

    response = requests.post(request_url, data=payload, files=files, headers=header)

    if (response.status_code == 200):

        jobid = response.text
        print(jobid)
        return jobid

    else:
        print("[ERROR] Unable to request. Response: ", print(response.text))
        exit()

def query_oncokb_cna(cna: CopyNumberAlteration, tumorType):

    token = settings.ONCOKB_TOKEN
    # curl -X GET "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?hugoSymbol=HNRNPA1P59&copyNameAlterationType=AMPLIFICATION&referenceGenome=GRCh38&tumorType=HGSOC" -H "accept: application/json" -H "Authorization: Bearer xx-xx-xx"

    hugosymbol = gene_id_convert(cna.gene_id, "HGNC")
    api_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?"
    request_url = api_url + 'copyNameAlterationType='+AlterationType[cna.CNstatus].value+'&hugoSymbol='+hugosymbol+'&tumorType='+tumorType
    header = dict(accept="application/json", Authorization='Bearer '+token)

    print("Request OncoKB API "+request_url)
    response = requests.get(request_url, headers=header)
    print(response.status_code)
    print(response.request.url)
    if (response.status_code == 200):
        rjson = response.json()
        try:
            rec, created = OncoKBAnnotation.objects.get_or_create(
                patient_id  = handle_int_field(cna.patient_id),
                hugoSymbol = handle_string_field(rjson["query"]["hugoSymbol"]),
                entrezGeneId = handle_string_field(rjson["query"]["entrezGeneId"]),
                alteration = handle_string_field(rjson["query"]["alteration"]),
                alterationType = handle_string_field(rjson["query"]["alterationType"]),
                svType = handle_string_field(rjson["query"]["svType"]),
                tumorType = handle_string_field(rjson["query"]["tumorType"]),
                consequence = handle_string_field(rjson["query"]["consequence"]),
                proteinStart = handle_int_field(rjson["query"]["proteinStart"]),
                proteinEnd = handle_int_field(rjson["query"]["proteinEnd"]),
                hgvs = handle_string_field(rjson["query"]["hgvs"]),
                geneExist = handle_boolean_field(rjson["geneExist"]),
                variantExist = handle_boolean_field(rjson["variantExist"]),
                alleleExist = handle_boolean_field(rjson["alleleExist"]),
                oncogenic = handle_string_field(rjson["oncogenic"]),
                mutationEffectDescription = handle_string_field(rjson["mutationEffect"]["description"]),
                knownEffect = handle_string_field(rjson["mutationEffect"]["knownEffect"]),
                citationPMids = handle_string_field(rjson["mutationEffect"]["citations"]["pmids"]),
                citationAbstracts = handle_string_field(rjson["mutationEffect"]["citations"]["abstracts"]),
                highestSensitiveLevel = handle_string_field(rjson["alleleExist"]),
                highestResistanceLevel = handle_string_field(rjson["highestResistanceLevel"]),
                highestDiagnosticImplicationLevel = handle_string_field(rjson["highestDiagnosticImplicationLevel"]),
                highestPrognosticImplicationLevel = handle_string_field(rjson["highestPrognosticImplicationLevel"]),
                highestFdaLevel = handle_string_field(rjson["highestFdaLevel"]),
                otherSignificantSensitiveLevels = handle_string_field(rjson["otherSignificantSensitiveLevels"]),
                otherSignificantResistanceLevels = handle_string_field(rjson["otherSignificantResistanceLevels"]),
                hotspot = handle_boolean_field(rjson["hotspot"]),
                geneSummary = handle_string_field(rjson["geneSummary"]),
                variantSummary = handle_string_field(rjson["variantSummary"]),
                tumorTypeSummary = handle_string_field(rjson["tumorTypeSummary"]),
                prognosticSummary = handle_string_field(rjson["prognosticSummary"]),
                diagnosticSummary = handle_string_field(rjson["diagnosticSummary"]),
                diagnosticImplications = handle_string_field(rjson["diagnosticImplications"]),
                prognosticImplications = handle_string_field(rjson["prognosticImplications"]),
                treatments = handle_string_field(rjson["treatments"]),
                dataVersion = handle_string_field(rjson["dataVersion"]),
                lastUpdate = handle_date_field(rjson["lastUpdate"]),
                vus = handle_boolean_field(rjson["vus"])
            )
            rec.save()
        except Exception as e:
            print(e)
            pass
    else:
        print("[ERROR] Unable to request. Response: ", print(response.text))
        exit()

def query_oncokb_somatic_mutation(snv: SomaticVariant , tumorType):
    # curl -X GET "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange?genomicLocation=7%2C140453136%2C140453136%2CA%2CT&tumorType=Melanoma&evidenceType=ONCOGENIC" -H "accept: application/json" -H "Authorization: Bearer token"
    # genomicLocation=7,140453136,140453136,A,T
    print(snv)
    altlength = len(snv.sample_allele)
    genomicLocation = snv.chromosome+','+str(snv.position)+','+(str(snv.position)+str(altlength))+','+snv.reference_allele+','+snv.sample_allele
    token = settings.ONCOKB_TOKEN
    header = dict(accept="application/json", Authorization='Bearer '+token)
    request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange?"

    print("Request OncoKB API "+request_url)
    response = requests.get(request_url+'genomicLocation='+genomicLocation+'&tumorType='+tumorType+'&evidenceType=ONCOGENIC', headers=header)

    if (response.status_code == 200):
        rjson = response.json()
        try:
            rec, created = OncoKBAnnotation.objects.get_or_create(
                patient_id  = handle_int_field(snv.patient_id),
                hugoSymbol = handle_string_field(rjson["query"]["hugoSymbol"]),
                entrezGeneId = handle_string_field(rjson["query"]["entrezGeneId"]),
                alteration = handle_string_field(rjson["query"]["alteration"]),
                alterationType = handle_string_field(rjson["query"]["alterationType"]),
                svType = handle_string_field(rjson["query"]["svType"]),
                tumorType = handle_string_field(rjson["query"]["tumorType"]),
                consequence = handle_string_field(rjson["query"]["consequence"]),
                proteinStart = handle_int_field(rjson["query"]["proteinStart"]),
                proteinEnd = handle_int_field(rjson["query"]["proteinEnd"]),
                hgvs = handle_string_field(rjson["query"]["hgvs"]),
                geneExist = handle_boolean_field(rjson["geneExist"]),
                variantExist = handle_boolean_field(rjson["variantExist"]),
                alleleExist = handle_boolean_field(rjson["alleleExist"]),
                oncogenic = handle_string_field(rjson["oncogenic"]),
                mutationEffectDescription = handle_string_field(rjson["mutationEffect"]["description"]),
                knownEffect = handle_string_field(rjson["mutationEffect"]["knownEffect"]),
                citationPMids = handle_string_field(rjson["mutationEffect"]["citations"]["pmids"]),
                citationAbstracts = handle_string_field(rjson["mutationEffect"]["citations"]["abstracts"]),
                highestSensitiveLevel = handle_string_field(rjson["alleleExist"]),
                highestResistanceLevel = handle_string_field(rjson["highestResistanceLevel"]),
                highestDiagnosticImplicationLevel = handle_string_field(rjson["highestDiagnosticImplicationLevel"]),
                highestPrognosticImplicationLevel = handle_string_field(rjson["highestPrognosticImplicationLevel"]),
                highestFdaLevel = handle_string_field(rjson["highestFdaLevel"]),
                otherSignificantSensitiveLevels = handle_string_field(rjson["otherSignificantSensitiveLevels"]),
                otherSignificantResistanceLevels = handle_string_field(rjson["otherSignificantResistanceLevels"]),
                hotspot = handle_boolean_field(rjson["hotspot"]),
                geneSummary = handle_string_field(rjson["geneSummary"]),
                variantSummary = handle_string_field(rjson["variantSummary"]),
                tumorTypeSummary = handle_string_field(rjson["tumorTypeSummary"]),
                prognosticSummary = handle_string_field(rjson["prognosticSummary"]),
                diagnosticSummary = handle_string_field(rjson["diagnosticSummary"]),
                diagnosticImplications = handle_string_field(rjson["diagnosticImplications"]),
                prognosticImplications = handle_string_field(rjson["prognosticImplications"]),
                treatments = handle_string_field(rjson["treatments"]),
                dataVersion = handle_string_field(rjson["dataVersion"]),
                lastUpdate = handle_date_field(rjson["lastUpdate"]),
                vus = handle_boolean_field(rjson["vus"])
            )
            rec.save()
        except Exception as e:
            print(e)
            pass

    else:
        print("[ERROR] Unable to request. Response: ", print(response.text))
        exit()

# TODO: method to request cancer genes from OnckoKB. Store to genomics model as target genes, create target gene filter for variants, and query from external DBs.
# def query_oncokb_cancer_gene_list():
#
#     token = settings.ONCOKB_TOKEN
#     request_url = "https://www.oncokb.org/api/v1/utils/cancerGeneList"
#     header = dict(accept="application/json", Authorization='Bearer '+token)
#
#     print("Request OncoKB API "+request_url)
#     response = requests.get(request_url)
#     print(response.status_code)
#     print(response.request.url)
#     if (response.status_code == 200):
#         rjson = response.json()
#         print(rjson)
#         return rjson
#
#     else:
#         print("[ERROR] Unable to request. Response: ", print(response.text))
#         exit()

def gene_id_convert(geneids, target):
    # geneids given as list with whitespace separator, target can be one of the target namespaces in https://biit.cs.ut.ee/gprofiler/convert
    # Few of the target namespaces: EMBL  ENSG    ENSP    ENST    ENTREZGENE    ENTREZGENE_ACC    ENTREZGENE_TRANS_NAME   GENEDB  GO  HGNC    HGNC_ACC    HGNC_TRANS_NAME
    # curl -X 'POST' -d '{"organism": "hsapiens", "target": "HGNC", "query": "ENSG00000230280"}' 'https://biit.cs.ut.ee/gprofiler/api/convert/convert/'
    request_url = "https://biit.cs.ut.ee/gprofiler/api/convert/convert/"
    print("Request gProfiler API "+request_url)
    data = '{"organism":"hsapiens", "target":"'+target+'", "query":"'+geneids+'"}'
    response = requests.post(url=request_url, data=data)
    print(response.status_code)
    print(response.request.url)
    if (response.status_code == 200):
        rjson = response.json()
        print(dict(rjson['result'][0]).get('converted'))
        return dict(rjson['result'][0]).get('converted')

    else:
        print("[ERROR] Unable to request. Response: ", print(response.text))
        exit()


def parse_isoforms(aaChangeRefGene):
    records = aaChangeRefGene.split(",") # WDR31:NM_001012361:exon4:c.184A>G:p.M62V,WDR31:NM_145241:exon4:c.181A>G:p.M61V
    isoforms = []
    for rec in records:
        fields = rec.split(":")
        if len(fields) > 1:
            gene = fields[0]
            print(fields)
            protein = fields[len(fields)-1].split(".")[1]
            isoform = gene+":"+protein
            isoforms.append(isoform)

            # else aaChangeRefGene can have UNKNOWN status, what to do with it?
    return list(dict.fromkeys(isoforms))

def generate_proteinchange_query_file(snvs: [SomaticVariant]):

    header = "protein\n"
    with open("./tmp/prot.ext", "w") as file1:
        file1.write(header)
        for snv in snvs:
            isoforms = parse_isoforms(snv.aaChangeRefGene)
            for isoform in isoforms:
                file1.write(isoform+"\n")
        file1.close()

def sql_query_db():

    try:
        for rec in SomaticVariant.objects.raw("SELECT * FROM genomics_somaticvariant"):
            print(rec)

    except Exception as e:
        print("Not in the database")

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--debug_cid', type=str, help="CID to execute the script in 'debug' mode on a specific CID")
        parser.add_argument('--snv',  action='store_true', help='')
        parser.add_argument('--patientid', type=str, help='Give patient id (in internal DB)')
        parser.add_argument('--geneid', type=str, help='Give gene id (in format eg. ENSG00000272262, NM_032264 or NBPF3)')
        parser.add_argument('--refid', type=str,  help='Give reference id (in dbSNP format eg. rs61769312)')
        parser.add_argument('--cna',  action='store_true', help='')
        parser.add_argument('--fusgenes', type=str,  help='Give a list of fusion genes eg. BCR__ABL1,PML__PARA')
        parser.add_argument('--cgijobid', type=str, help='Download results from CGI by jobid')
        parser.add_argument('--cgiquery',  action='store_true', help='Download results from CGI by jobid')
        parser.add_argument('--oncokbcna',  action='store_true',  help='Query OncoKB by gene id from given patient CNA. Input parameter: gene id')
        parser.add_argument('--oncokbsnv', action='store_true',  help='Query OncoKB by genomic location parsed patient SNV. Input parameter: ref id')
        parser.add_argument('--sqlsnvs',  action='store_true', help='')
        parser.add_argument('--exonic',  action='store_true', help='')
        parser.add_argument('--proteinchange',  action='store_true', help='')

    def handle(self, *args, **kwargs):

        if kwargs["sqlsnvs"]:
            sql_query_db()

        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbcna --geneid=ENSG00000230280 --patientid=1"
        if kwargs["oncokbcna"]:
            cna = get_cna(kwargs["patientid"], kwargs["geneid"])
            resp = query_oncokb_cna(cna, "HGSOC")
            print(resp)
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbsnv=rs61769312 --patientid=1"
        if kwargs["oncokbsnv"]:
            snv = get_snv(kwargs["patientid"], kwargs["refid"])
            resp = query_oncokb_somatic_mutation(snv, "HGSOC")
            print(resp)
        if kwargs["cgijobid"]:
            cgijobid=kwargs["cgijobid"]
            query_cgi_job(kwargs["patientid"], cgijobid)
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --cna --geneid=PTPN14 --patientid=1"
        if kwargs["cgiquery"] and kwargs["cna"]:
            ensg = gene_id_convert(kwargs["geneid"], "ENSG")
            cna = get_cna(kwargs["patientid"], ensg)
            generate_temp_cgi_query_files([],[cna],[])
            jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, "FRS", "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(120)
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --exonic --patientid=1"
        if kwargs["cgiquery"] and kwargs["exonic"] and kwargs["patientid"]: # Query all exonic mutations for given patient
            snv = get_all_exonic_snvs_of_patient(kwargs["patientid"])
            generate_temp_cgi_query_files(snv,[],[])
            jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext", None, None, "FRS", "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(120)
        if kwargs["cgiquery"] and kwargs["proteinchange"] and kwargs["patientid"]: # Query all protein affecting mutations for given patient
            snvs = get_actionable_snvs_by_aaChangeRefGene(kwargs["patientid"])
            generate_proteinchange_query_file(snvs)
            jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/prot.ext", None, None, "FRS", "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(120)
        if kwargs["cgiquery"] and kwargs["fusgenes"] and kwargs["patientid"]: # Query list of fusion genes for given patient
            fusgenes=kwargs["fusgenes"].split(',')
            generate_temp_cgi_query_files([],[],fusgenes)
            jobid = launch_cgi_job_with_mulitple_variant_types(None, None, "./tmp/fus.ext", "FRS", "hg38")
            time.sleep(90)
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(120)
