import io
import time
import zipfile

import pandas as pd
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from genomics.models import SomaticVariant, CopyNumberAlteration, CGIMutation, CGICopyNumberAlteration, CGIFusionGene, \
    CGIDrugPrescriptions, OncoKBAnnotation


def handle_boolean_field(value, field=None, default=False, ):
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


def launch_cgi_job(mutations_file, cnas_file, transloc_file, cancer_type, reference):

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
        print("[ERROR] Unable to request")
        exit()

def query_oncokb_cna(cna: CopyNumberAlteration, tumorType):

    token = settings.ONCOKB_TOKEN
    # curl -X GET "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?hugoSymbol=HNRNPA1P59&copyNameAlterationType=AMPLIFICATION&referenceGenome=GRCh38&tumorType=HGSOC" -H "accept: application/json" -H "Authorization: Bearer xx-xx-xx"

    hugosymbol = gene_id_convert(cna.gene_id, "HGNC").get('converted')
    request_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?copyNameAlterationType=AMPLIFICATION&"
    header = dict(accept="application/json", Authorization='Bearer '+token)

    print("Request OncoKB API "+request_url)
    response = requests.get(request_url + "hugoSymbol="+hugosymbol+'&tumorType='+tumorType, headers=header)
    print(response.status_code)
    print(response.request.url)
    if (response.status_code == 200):
        #responsejson = json.JSONDecoder.decode(response.json())
        rjson = response.json()
        print(rjson)
        return rjson

    else:
        print("[ERROR] Unable to request")
        exit()


def query_oncokb_somatic_mutation(snv: SomaticVariant , tumorType):
     # curl -X GET "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange?genomicLocation=7%2C140453136%2C140453136%2CA%2CT&tumorType=Melanoma&evidenceType=ONCOGENIC" -H "accept: application/json" -H "Authorization: Bearer token"
     # genomicLocation=7,140453136,140453136,A,T
     print(snv)
     altlength = len(snv.sample_allele)
     genomicLocation = snv.chromosome+','+snv.position+','+(str(snv.position)+str(altlength))+','+snv.reference_allele+','+snv.sample_allele
     token = settings.ONCOKB_TOKEN
     header = dict(accept="application/json", Authorization='Bearer '+token)
     request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange?"

     print("Request OncoKB API "+request_url)
     response = requests.get(request_url+'genomicLocation='+genomicLocation+'&tumorType='+tumorType+'&evidenceType=ONCOGENIC', headers=header)
     print(response.status_code)

     if (response.status_code == 200):
         try:
             rec, created = OncoKBAnnotation.objects.get_or_create(
                 patient_id                               = snv.patient_id,
                 hugoSymbol = handle_string_field(rjson["query"]["hugoSymbol"]),
                 entrezGeneId = handle_string_field(rjson["query"]["entrezGeneId"]),
                 alteration = handle_string_field(rjson["query"]["alteration"]),
                 alterationType = handle_string_field(rjson["query"]["alterationType"]),
                 svType = handle_string_field(rjson["query"]["svType"]),
                 tumorType = handle_string_field(rjson["query"]["tumorType"]),
                 consequence = handle_string_field(rjson["query"]["consequence"]),
                 proteinStart = handle_string_field(rjson["query"]["proteinStart"]),
                 proteinEnd = handle_string_field(rjson["query"]["proteinEnd"]),
                 hgvs = handle_string_field(rjson["query"]["hgvs"]),
                 geneExist = handle_string_field(rjson["geneExist"]),
                 variantExist = handle_string_field(rjson["variantExist"]),
                 alleleExist = handle_string_field(rjson["alleleExist"]),
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
                 hotspot = handle_string_field(rjson["hotspot"]),
                 geneSummary = handle_string_field(rjson["geneSummary"]),
                 variantSummary = handle_string_field(rjson["variantSummary"]),
                 tumorTypeSummary = handle_string_field(rjson["tumorTypeSummary"]),
                 prognosticSummary = handle_string_field(rjson["prognosticSummary"]),
                 diagnosticSummary = handle_string_field(rjson["diagnosticSummary"]),
                 diagnosticImplications = handle_string_field(rjson["diagnosticImplications"]),
                 prognosticImplications = handle_string_field(rjson["prognosticImplications"]),
                 treatments = handle_string_field(rjson["treatments"]),
                 dataVersion = handle_string_field(rjson["dataVersion"]),
                 lastUpdate = handle_string_field(rjson["lastUpdate"]),
                 vus = handle_string_field(rjson["vus"])
             )
             rec.save()
         except Exception as e:
             print(e)
             pass

     else:
         print("[ERROR] Unable to request")
         exit()


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
        print("[ERROR] Unable to request")
        exit()


def query_cgi_job(patient_id, jobid):

    # curl --request GET --url 'https://www.cancergenomeinterpreter.org/api/v1/de04a9b5f30b1cedb53e' --header "Authorization: ilari.maarala@helsinki.fi token" -G --data 'action=download'
    request_url = "https://www.cancergenomeinterpreter.org/api/v1/"
    cgitoken = settings.CGI_TOKEN
    header = dict(Authorization='ilari.maarala@helsinki.fi '+cgitoken)

    print("Request CGI job by id")
    payload = dict(action='download')
    response = requests.get(request_url+jobid, headers=header, params=payload)

    print(response.request.url)
    print(response.status_code)

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
            # MUTATION	START	POS_HG19	END	CHR	ALT	REF	STRAND	INFO	TYPE	SYMBOL	TRANSCRIPT	PROTEIN_CHANGE	BOOSTDM_DS	BOOSTDM_SCORE	ONCOGENIC_CLASSIFICATION	SOURCE	CONSEQUENCE	IS_CANCER_GENE	CONSENSUS_ROLE
            # chr3:178936091 G>A	178936091	178653879	178936091	3	A	G	+	input02	SNV	KCNMB2-AS1	ENST00000668466	--	non-protein affecting		non-protein affecting		non_coding_transcript_exon_variant	NO

            # TODO: deprecated, CGI response changed to alterations.tsv and column names changed
            # current format
            #Sample ID	Gene	Protein Change	Oncogenic Summary	Oncogenic Prediction	External oncogenic annotation	Mutation	Consequence	Transcript	Strand	Type
            #input02	KCNMB2-AS1	--	non-protein affecting	non-protein affecting		chr3:178936091 G>A	non_coding_transcript_exon_variant	ENST00000668466	+	SNV

            if fn == "alterations.tsv":
                for index, row in df.iterrows():
                    try:
                        rec, created = CGIMutation.objects.get_or_create(
                            patient_id      = patient_id,
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
                            patient_id                                = patient_id,
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
                            patient_id                                = patient_id,
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
            # Drug prescriptions response
            # SAMPLE	DISEASES	CTYPE	SAMPLE_ALTERATION	ALTERATION_MATCH	CTYPE_MATCH	DRUGS	BIOMARKER	RESPONSE	BIOMARKER_IDX	RESISTANCE_LIST	RESISTANCE_TYPE	EVIDENCE_LABEL	SOURCE	SOURCE_DETAILS
            # single_sample	Breast adenocarcinoma	BRCA	ERBB2:amp CNA	complete	NO	Neratinib (ERBB2 inhibitor) + Capecitabine (Chemotherapy)	ERBB2 amplification	Responsive	2			A	cgi	FDA:https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-neratinib-metastatic-her2-positive-breast-cancer;PMID:30860945

            # TODO: CGI response changed to biomarkers.tsv
            # current format
            # Sample ID	Alterations	Biomarker	Drugs	Diseases	Response	Evidence	Match	Source	BioM	Resist.	Tumor type
            # single_sample	ABL1__BCR 	ABL1 (T315I,V299L,G250E,F317L)	Bosutinib (BCR-ABL inhibitor 3rd gen)	Acute lymphoblastic leukemia, Chronic myeloid leukemia	Resistant	A	NO	cgi	only gene		ALL, CML
            if fn == "biomarkers.tsv":
                for index, row in df.iterrows():
                    try:
                        rec, created = CGIDrugPrescriptions.objects.get_or_create(
                            patient                                = patient_id,
                            sample = handle_string_field(row["Sample ID"]),
                            alterations = handle_string_field(row["Alterations"]),
                            biomarker = handle_string_field(row["Biomarker"]),
                            drugs = handle_string_field(row["Drugs"]),
                            diseases = handle_string_field(row["Diseases"]),
                            response = handle_string_field(row["Response"]),
                            evidence = handle_string_field(row["Evidence"]),
                            match = handle_string_field(row["Match"]),
                            source = handle_string_field(row["Source"]),
                            biom = handle_string_field(row["BioM"]),
                            resistance = handle_string_field(row["Resist."]),
                            tumor_type = handle_string_field(row["Tumor type"])
                        )
                        rec.save()
                    except Exception as e:
                        print(e)
                        pass

    else:
        print("[ERROR] Unable to request")
        exit()

# TODO: Get variants from the model and generate files if model is given
def generate_temp_cgi_query_files(snvs: [SomaticVariant], cnas: [CopyNumberAlteration], translocs: [str]):

        header = "chr\tpos\tref\talt\n"
        with open("./tmp/snvs.ext", "w") as file1:
            file1.write(header)
            for snv in snvs:
                row = snv.chromosome+'\t'+snv.position+'\t'+snv.reference_allele+'\t'+snv.sample_allele+'\n'
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



    def handle(self, *args, **kwargs):

        def handle_boolean_field(value, field=None, default=False, ):
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

        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbcna=ENSG00000230280 --patientid=1"
        if kwargs["oncokbcna"]:
            ensg = gene_id_convert(kwargs["geneid"], "ENSG").get('converted')
            cna = get_cna(kwargs["patientid"], ensg)
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
            jobid = launch_cgi_job(None, "./tmp/cnas.ext", None, "OVSE", "hg38")
            time.sleep(90)
            # TODO: CGI analysis can take long time depending on traffic etc, try query few times
            query_cgi_job(kwargs["patientid"], jobid.replace('"', ''))
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --snv --refid=rs61769312 --patientid=1"
        if kwargs["cgiquery"] and kwargs["snv"]:
            snv = get_snv(kwargs["patientid"], kwargs["refid"])
            generate_temp_cgi_query_files([snv],[],[])
            jobid = launch_cgi_job("./tmp/snvs.ext", None, None, "OVSE", "hg38")
            time.sleep(90)
            query_cgi_job(kwargs["patientid"], jobid.replace('"', ''))
        if kwargs["cgiquery"] and kwargs["fusgenes"]:
            fusgenes=kwargs["fusgenes"].split(',')
            generate_temp_cgi_query_files([],[],fusgenes)
            jobid = launch_cgi_job(None, None, "./tmp/fus.ext", "OVSE", "hg38")
            time.sleep(90)
            query_cgi_job(kwargs["patientid"], "", jobid.replace('"', ''))