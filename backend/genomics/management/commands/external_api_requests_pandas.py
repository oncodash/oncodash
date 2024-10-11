import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings

from datetime import datetime
import json

from genomics.models import cna_annotation, snv_annotation

from genomics.models import AlterationType
import urllib3
import httpx

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
    return None if pd.isna(value) else str(value)

def handle_list_field(value):
    return None if len(value)==0 else value

def handle_int_field(value):
    return None if pd.isna(value) else value

def handle_decimal_field(value):
    return None if pd.isna(value) or str(value) == "." else value

def handle_date_field(value):

    return None if pd.isna(value) else datetime.strptime(value, "%m/%d/%Y")

def handle_copynumber_field(nMinor, nMajor):
    if pd.isna(nMinor) and pd.isna(nMajor):
        return None
    else:
        if nMinor and nMinor:
            return int(nMinor) + int(nMajor)
        if pd.isna(nMinor):
            return int(nMajor)
        if pd.isna(nMajor):
            return int(nMinor)

def handle_readcount_field0(readCounts, sids, sid):
    rcs = readCounts.split(";")
    if pd.isna(readCounts):
        return None
    return float(str(rcs[sids.index(sid)]).split(",")[0])

def handle_readcount_field1(readCounts, sids, sid):
    rcs = readCounts.split(";")
    if pd.isna(readCounts):
        return None
    return float(str(rcs[sids.index(sid)]).split(",")[1])

def handle_treatments_field(jsondata):
    if jsondata:
        drugs = ""
        for rec in jsondata:
            darr = drugs.split(";")
            if rec["drugs"][0]["drugName"] not in darr:
                drugs += rec["drugs"][0]["drugName"]+";"
        return drugs[0:len(drugs)-1]
    else:
        return None

def query_oncokb_cnas(cna_annotations: []):

    """
    This function queries the OncoKB API to get annotations for a given copy number alteration (CNA)
    and tumor type. It then saves the annotations to the database.

    Args:
    cna (CopyNumberAlteration): A copy number alteration object.
    tumorType (str): The tumor type for which the annotations are to be retrieved.

    Returns:
    None

    Raises:
    None
    """

    token = settings.ONCOKB_TOKEN

    api_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations"
    #request_url = api_url + 'copyNameAlterationType='+AlterationType[cna.CNstatus].value+'&hugoSymbol='+hugosymbol+'&tumorType='+tumorType
    header = {'accept':'application/json', 'Content-Type': 'application/json', 'Authorization':'Bearer '+token}

    print("Request OncoKB API "+api_url)

    # TODO: No need to query same alteration for every patient and sample, get unique by cnas[i].hugoSymbol cnas[i].alteration
    cnas = cna_annotations.values('hugoSymbol', 'alteration', 'referenceGenome', 'tumorType').distinct()

    data = [
        {
            "copyNameAlterationType": f"{str.upper(cna.get('alteration'))}",
            "referenceGenome": f"{cna.get('referenceGenome')}",
            "gene": {
                "hugoSymbol": f"{str.upper(cna.get('hugoSymbol'))}"
            },
            "tumorType": f"{cna.get('tumorType')}"
        }
        for cna in cnas
    ]

    #header = str(header).replace("'",'"')
    data = str(data).replace("'",'"')
    print("Querying " +str(cnas.count())+ " CNAs....")
    # Sending a POST request and getting back response as HTTPResponse object.
    response = urllib3.PoolManager().request("POST", api_url, body=data, headers={'accept':'application/json','Content-Type':'application/json','Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    #response = httpx.post(api_url, json=data, headers={'Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    #response = http.request("GET",request_url, headers=header)
    #print(response.data.decode('utf-8'))

    if (response.status == 200):

        respjson = json.loads(response.data.decode('utf-8'))
        #print(data)
        print("Response has " + str(len(respjson)) + " records.")
        for rjson in respjson:
            hugosymbol = handle_string_field(rjson["query"]["hugoSymbol"])
            alteration = str.upper(handle_string_field(rjson["query"]["alteration"]))
            #idsplit = str(cryptocode.decrypt(rjson["query"]["id"], settings.CRYPTOCODE)).split(":")
            #cna_id = idsplit[2]
            objs = cna_annotations.filter(hugoSymbol=hugosymbol).filter(alteration=alteration)
            objs.update(
                #patient_id  = idsplit[0],
                #sample_id = idsplit[1],
                hugoSymbol = handle_string_field(rjson["query"]["hugoSymbol"]),
                entrezGeneId = handle_string_field(rjson["query"]["entrezGeneId"]),
                alteration = handle_string_field(rjson["query"]["alteration"]),
                tumorType = handle_string_field(rjson["query"]["tumorType"]),
                consequence = handle_string_field(rjson["query"]["consequence"]),
                proteinStart = handle_int_field(rjson["query"]["proteinStart"]),
                proteinEnd = handle_int_field(rjson["query"]["proteinEnd"]),
                oncogenic = handle_string_field(rjson["oncogenic"]),
                mutationEffectDescription = handle_string_field(rjson["mutationEffect"]["description"]),
                gene_role = handle_string_field(rjson["mutationEffect"]["knownEffect"]),
                citationPMids = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"])),
                oncokb_level = handle_string_field(rjson["highestSensitiveLevel"]) if handle_string_field(rjson["highestSensitiveLevel"]) else handle_string_field(rjson["highestResistanceLevel"]),
                geneSummary = handle_string_field(rjson["geneSummary"]),
                variantSummary = handle_string_field(rjson["variantSummary"]),
                tumorTypeSummary = handle_string_field(rjson["tumorTypeSummary"]),
                treatments = handle_treatments_field(rjson["treatments"]),

                # exphomci = models.BooleanField(default=False, blank=False, null=True)
                # readcount=handle_readcount_field(snv.readCounts, sids, sid)
            )
            print("Updated " + str(objs.count()) + " CNAs")
    else:
        print("Unable to request. Response: ", response.data)

    return response.status

def query_oncokb_cnas_to_csv(cna_annotations: []):

    """
    This function queries the OncoKB API to get annotations for a given copy number alteration (CNA)
    and tumor type. It then saves the annotations to the database.

    Args:
    cna (CopyNumberAlteration): A copy number alteration object.
    tumorType (str): The tumor type for which the annotations are to be retrieved.

    Returns:
    None

    Raises:
    None
    """

    token = settings.ONCOKB_TOKEN

    api_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations"
    #request_url = api_url + 'copyNameAlterationType='+AlterationType[cna.CNstatus].value+'&hugoSymbol='+hugosymbol+'&tumorType='+tumorType
    header = {'accept':'application/json', 'Content-Type': 'application/json', 'Authorization':'Bearer '+token}

    print("Request OncoKB API "+api_url)

    # TODO: No need to query same alteration for every patient and sample, get unique by cnas[i].hugoSymbol cnas[i].alteration

    cnas = cna_annotations.values('hugoSymbol', 'alteration', 'referenceGenome', 'tumorType').distinct()

    data = [
        {
            "copyNameAlterationType": f"{str.upper(cna.get('alteration'))}",
            "referenceGenome": f"{cna.get('referenceGenome')}",
            "gene": {
                "hugoSymbol": f"{str.upper(cna.get('hugoSymbol'))}"
            },
            "tumorType": f"{cna.get('tumorType')}"
        }
        for cna in cnas
    ]

    #header = str(header).replace("'",'"')
    data = str(data).replace("'",'"')
    print("Querying " +str(cnas.count())+ " CNAs....")
    cnadf = pd.DataFrame.from_records(cna_annotations.values(), index="id")
    print(cnadf)
    # Sending a POST request and getting back response as HTTPResponse object.
    response = urllib3.PoolManager().request("POST", api_url, body=data, headers={'accept':'application/json','Content-Type':'application/json','Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    #response = httpx.post(api_url, json=data, headers={'Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    #response = http.request("GET",request_url, headers=header)
    #print(response.data)
    #print(response.data.decode('utf-8'))

    if (response.status == 200):

        respjson = json.loads(response.data.decode('utf-8'))

        for rjson in respjson:
            hugosymbol = handle_string_field(rjson["query"]["hugoSymbol"])
            alteration = str.upper(handle_string_field(rjson["query"]["alteration"]))
            #idsplit = str(cryptocode.decrypt(rjson["query"]["id"], settings.CRYPTOCODE)).split(":")
            #cna_id = idsplit[2]
            updatedf = cnadf.loc[(cnadf['hugoSymbol']==hugosymbol) & (cnadf['alteration']==alteration)]

            updatedf['hugoSymbol'] = handle_string_field(rjson["query"]["hugoSymbol"])
            updatedf['entrezGeneId'] = handle_string_field(rjson["query"]["entrezGeneId"])
            updatedf['tumorType'] = handle_string_field(rjson["query"]["tumorType"])
            updatedf['consequence'] = handle_string_field(rjson["query"]["consequence"])
            updatedf['proteinStart'] = handle_int_field(rjson["query"]["proteinStart"])
            updatedf['proteinEnd'] = handle_int_field(rjson["query"]["proteinEnd"])
            updatedf['oncogenic'] = handle_string_field(rjson["oncogenic"])
            updatedf['mutationEffectDescription'] = handle_string_field(rjson["mutationEffect"]["description"])
            updatedf['gene_role'] = handle_string_field(rjson["mutationEffect"]["knownEffect"])
            updatedf['citationPMids'] = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"]))
            updatedf['oncokb_level'] = handle_string_field(rjson["highestSensitiveLevel"]) if handle_string_field(rjson["highestSensitiveLevel"]) else handle_string_field(rjson["highestResistanceLevel"])
            updatedf['prognosticSummary'] = handle_string_field(rjson["prognosticSummary"])
            updatedf['diagnosticSummary'] = handle_string_field(rjson["diagnosticSummary"])
            updatedf['diagnosticImplications'] = handle_string_field(rjson["diagnosticImplications"])
            updatedf['prognosticImplications'] = handle_string_field(rjson["prognosticImplications"])
            updatedf['geneSummary'] = handle_string_field(rjson["geneSummary"])
            updatedf['variantSummary'] = handle_string_field(rjson["variantSummary"])
            updatedf['tumorTypeSummary'] = handle_string_field(rjson["tumorTypeSummary"])
            updatedf['treatments'] = handle_treatments_field(rjson["treatments"])

                # exphomci = models.BooleanField(default=False, blank=False, null=True)
                # readcount=handle_readcount_field(snv.readCounts, sids, sid)
            
            #print("Updated "+str(updatedf.count())+" CNAs")
        cnadf.to_csv("cna_annotated_oncokb.csv", sep="\t")
    else:
        print("Unable to request. Response: ", response.data)

    return response.status


def query_oncokb_somatic_mutations(snv_annotations: pd.DataFrame):
    """
    This function queries the OncoKB API to get information about a somatic mutation.

    Args:
    snv (SomaticVariant): A SomaticVariant object representing the somatic mutation.
    tumorType (str): The type of tumor for which the mutation information is being queried.

    Returns:
    None

    Raises:
    None
    """
    token = settings.ONCOKB_TOKEN
    header = {"accept":"application/json", 'Content-Type': 'application/json', "Authorization":'Bearer '+token}
    request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange"
    #request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byHGVSg"

    snvs = snv_annotations.groupby(['chromosome', 'position', 'reference_allele', 'sample_allele', 'tumorType', 'referenceGenome'])
    uniques = []
    for keys, group in snvs:
        uniques.append(dict({'chromosome':keys[0], 'position':keys[1], 'reference_allele':keys[2], 'sample_allele':keys[3], 'tumorType':keys[4], 'referenceGenome':keys[5]}))
    data = [
        {
            "id": f"{row['chromosome']+','+str(row['position'])+','+(str(int(row['position'])+len(row['sample_allele'])))+','+row['reference_allele']+','+row['sample_allele']}",
            "genomicLocation": f"{row['chromosome']+','+str(row['position'])+','+(str(int(row['position'])+len(row['sample_allele'])))+','+row['reference_allele']+','+row['sample_allele']}",
            "tumorType": f"{row['tumorType']}",
            "referenceGenome": f"{row['referenceGenome']}"
        }
        for row in uniques
    ]

    #print(data)
    # Sending a GET request and getting back response as HTTPResponse object.
    print("Request OncoKB API "+request_url)
    print("Querying " + str(len(uniques)) + " CNAs....")

    #response = urllib3.PoolManager().request("POST", request_url, body=data, headers={'accept':'application/json','Content-Type':'application/json','Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    response = httpx.post(request_url, json=data, headers={'Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'}, timeout=None)
    # response = http.request("GET",request_url, headers=header)
    print(response.status_code)

    #TODO: check why EGFR chr7,55181426,55181427,A,C  is not found but is found from web api (and also from CGI)
    if (response.status_code == 200):

        respjson = json.loads(response.text)
        for rjson in respjson:
            #print(rjson)
            #print("OBJ", rjson)
            idsplit = str(rjson["query"]["id"]).split(",")
            #sids = idsplit[1].split(";")
            #pid = idsplit[0]

            chromosome = str(idsplit[0])
            position = int(idsplit[1])
            reference_allele = str(idsplit[3])
            sample_allele = str(idsplit[4])
            # idsplit = str(cryptocode.decrypt(rjson["query"]["id"], settings.CRYPTOCODE)).split(":")
            # cna_id = idsplit[2]
            updatedf = snv_annotations.loc[(snv_annotations['chromosome']==chromosome) & (snv_annotations['position']==position) & (snv_annotations['reference_allele']==reference_allele) & (snv_annotations['sample_allele']==sample_allele)]
            #patient_id=pid,
            #sample_id=sid,
            #if len(rjson["treatments"]) > 0:
            #    print(json.dumps(rjson["treatments"],indent=4))
            if handle_string_field(rjson["highestSensitiveLevel"]):
                print(json.dumps(rjson["mutationEffect"],indent=4))
                print(json.dumps(rjson["treatments"], indent=4))

            #print(json.dumps(rjson,indent=4))

            for indxs, row in updatedf.iterrows():

                snv_annotations.at[indxs,'hugoSymbol'] = handle_string_field(rjson["query"]["hugoSymbol"])
                snv_annotations.at[indxs,'entrezGeneId'] = handle_string_field(rjson["query"]["entrezGeneId"])
                snv_annotations.at[indxs,'tumorType'] = handle_string_field(rjson["query"]["tumorType"])
                snv_annotations.at[indxs,'consequence'] = handle_string_field(rjson["query"]["consequence"])
                snv_annotations.at[indxs,'proteinStart'] = handle_int_field(rjson["query"]["proteinStart"])
                snv_annotations.at[indxs,'proteinEnd'] = handle_int_field(rjson["query"]["proteinEnd"])
                snv_annotations.at[indxs,'oncogenic'] = handle_string_field(rjson["oncogenic"])
                snv_annotations.at[indxs,'mutationEffectDescription'] = handle_string_field(rjson["mutationEffect"]["description"])
                snv_annotations.at[indxs,'gene_role'] = handle_string_field(rjson["mutationEffect"]["knownEffect"])
                snv_annotations.at[indxs,'citationPMids'] = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"]))
                snv_annotations.at[indxs,'oncokb_level'] = handle_string_field(rjson["highestSensitiveLevel"]) if handle_string_field(rjson["highestSensitiveLevel"]) else handle_string_field(rjson["highestResistanceLevel"])
                snv_annotations.at[indxs,'geneSummary'] = handle_string_field(rjson["geneSummary"])
                snv_annotations.at[indxs,'variantSummary'] = handle_string_field(rjson["variantSummary"])
                snv_annotations.at[indxs,'tumorTypeSummary'] = handle_string_field(rjson["tumorTypeSummary"])
                snv_annotations.at[indxs,'prognosticSummary'] = handle_string_field(rjson["prognosticSummary"])
                snv_annotations.at[indxs,'diagnosticSummary'] = handle_string_field(rjson["diagnosticSummary"])
                #snv_annotations.at[indxs,'diagnosticImplications'] = handle_string_field(rjson["diagnosticImplications"])
                #snv_annotations.at[indxs,'prognosticImplications'] = handle_string_field(rjson["prognosticImplications"])
                snv_annotations.at[indxs,'treatments'] = handle_treatments_field(rjson["treatments"])
                #nMinor=models.IntegerField(null=True)
                #nMajor = models.IntegerField(null=True)
                #ad0 = handle_readcount_field0(snv.readCounts, sids, sid),
                #ad1 = handle_readcount_field1(snv.readCounts, sids, sid),
                #af = models.IntegerField(null=True)
                #dp = models.IntegerField(null=True)
                #lohstatus = models.CharField(max_length=16, default=None, blank=True, null=True)
                #exphomci = models.BooleanField(default=False, blank=False, null=True)
                #copynumber = handle_copynumber_field(cna.nMinor, cna.nMajor)
        print(snv_annotations)
        snv_annotations.drop(columns=snv_annotations.columns[0], axis=1, inplace=True)
        snv_annotations.to_csv("snv_annotated_oncokb.csv", index=False, mode='a', sep="\t")
        #print("Updated " + str(len(snvdf)) + " CNAs")
    else:
        print("[ERROR] Unable to request. Response: ", print(response.data))
        exit()

def gene_id_convert(geneids, target):
    # geneids given as list with whitespace separator, target can be one of the target namespaces in https://biit.cs.ut.ee/gprofiler/convert
    request_url = "https://biit.cs.ut.ee/gprofiler/api/convert/convert/"
    print("Request gProfiler API "+request_url)
    data = '{"organism":"hsapiens", "target":"'+target+'", "query":"'+geneids+'"}'
    #{"organism":"hsapiens", "target":target, "query":geneids}
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode('utf-8')
    response = urllib3.PoolManager().request("POST", url=request_url, body=body, headers=headers)
    print("response.status", response.status)
    print(data)
    print(response.json)
    if (response.status == 200):
        rjson = json.loads(response.data.decode('utf-8'))
        print(dict(rjson['result'][0]).get('converted'))
        return dict(rjson['result'][0]).get('converted')

    else:
        print("[ERROR] Unable to request. Response: ", print(response.data))
        exit()

def parse_isoforms(aaChangeRefGene):
    records = aaChangeRefGene.split(",")
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



def generate_cgi_cna_file_from_list(genelist):
    header = "gene\tcna\n"
    with open("./tmp/cnas.ext", "w") as file2:
        file2.write(header)
        genes = genelist
        for gene in genes:
            row = gene + '\tAMP\n'
            print(row)
            file2.write(row)
        file2.close()

def cnadf_to_django_model(cnadf):
    cnaobjects = []
    for index, row in cnadf.iterrows():
        cnaobjects.append(cna_annotation(
            patient_id=handle_string_field(row["patient_id"]),  # sample name includes cohort code which is mapped to patient id
            sample_id=handle_string_field(row["sample_id"]),
            referenceGenome=row["referenceGenome"],
            hugoSymbol=handle_string_field(row["hugoSymbol"]),
            entrezGeneId=handle_string_field(row["entrezGeneId"]),
            alteration=handle_string_field(row["alteration"]),
            tumorType=handle_string_field(row["tumorType"]),
            nMajor=handle_int_field(row["nMajor"]),
            nMinor=handle_int_field(row["nMinor"]),
            lohstatus=handle_string_field(row["lohstatus"]),
            ploidy=handle_decimal_field(row["ploidy"])
        ))
    try:
        objs = cna_annotation.objects.bulk_create(cnaobjects)
        print("Imported " + str(len(objs)) + " records.")
    except Exception as e:
        print("Exception: ", e)


def snvs_to_django_model(snvs):
    snvobjs = []
    for index, row in snvs.iterrows():
        snvobjs.append(snv_annotation(
            patient_id=handle_string_field(row["patient_id"]),
            # sample name includes cohort code which is mapped to patient id
            sample_id=handle_string_field(row["sample_id"]),
            referenceGenome=row["referenceGenome"],
            ref_id=handle_string_field(row["ref_id"]),
            chromosome=handle_string_field(row["chromosome"]),
            position=handle_int_field(row["position"]),
            reference_allele=handle_string_field(row["reference_allele"]),
            sample_allele=handle_string_field(row["sample_allele"]),
            hugoSymbol=handle_string_field(row["hugoSymbol"]),
            # entrezGeneId = "",
            # alteration: string;
            tumorType=handle_string_field(row["tumorType"]),
            consequence=handle_string_field(row["consequence"]),
            # proteinStart: string;
            # proteinEnd: string;
            # oncogenic: string;
            # mutationEffectDescription: string;
            # gene_role: string;
            # citationPMids: string;
            # geneSummary: string;
            # variantSummary: string;
            # tumorTypeSummary: string;
            # diagnosticSummary: string;
            # diagnosticImplications: string;
            # prognosticImplications: string;
            # treatments: string;
            nMinor=handle_int_field(row["nMinor"]),
            nMajor=handle_int_field(row["nMajor"]),
            # oncokb_level: string;
            # cgi_level: string;
            # rank: number;
            ad0=handle_decimal_field(row["ad0"]),
            ad1=handle_decimal_field(row["ad1"]),
            af=handle_decimal_field(row["af"]),
            readcount=handle_decimal_field(row["readcount"]),
            depth=handle_decimal_field(row["depth"]),
            lohstatus=handle_string_field(row["lohstatus"]),
            hom_lo=handle_decimal_field(row["hom_lo"]),
            hom_hi=handle_decimal_field(row["hom_hi"]),
            hom_pbinom_lo=handle_decimal_field(row["hom_pbinom_lo"]),
            homogenous=handle_string_field(row["homogenous"]),
            funcMane=handle_string_field(row["funcMane"]),
            funcRefgene=handle_string_field(row["funcRefgene"]),
            exonicFuncMane=handle_string_field(row["exonicFuncMane"]),
            cadd_score=handle_decimal_field(row["cadd_score"]),
            ada_score=handle_decimal_field(row["ada_score"]),
            rf_score=handle_decimal_field(row["rf_score"]),
            amis_score=handle_decimal_field(["amis_score"]),
            cosmic_id=handle_string_field(row["cosmic_id"]),
            clinvar_id=handle_string_field(row["clinvar_id"]),
            clinvar_sig=handle_string_field(row["clinvar_sig"]),
            clinvar_status=handle_string_field(row["clinvar_status"]),
            clinvar_assoc=handle_string_field(row["clinvar_assoc"]),
            pathogenecity=handle_string_field(row["pathogenecity"]),
            classification=handle_string_field(row["classification"])
            # sift_cat: string;
            # sift_val: number;  # Will be dded to WGS output in near future https://sift.bii.a-star.edu.sg/
            # polyphen_cat: string;
            # polyphen_val: number;  # Will be dded to WGS output in near future http://genetics.bwh.harvard.edu/pph2/

        ))

    try:
        objs = snv_annotation.objects.bulk_create(snvobjs)
        print("Imported " + str(len(objs)) + " records.")
    except Exception as e:
        print(e)






class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--snv',  action='store_true', help='')
        parser.add_argument('--patientid', type=str, help='Give patient id (in internal DB)')
        parser.add_argument('--cohortcode', type=str, help='Give cohort code of patient')
        parser.add_argument('--geneid', type=str, help='Give gene id (in format eg. ENSG00000272262, NM_032264 or NBPF3)')
        parser.add_argument('--gene', type=str, help='Give gene name (in format eg. BRCA1)')
        parser.add_argument('--refid', type=str,  help='Give reference id (in dbSNP format eg. rs61769312)')
        parser.add_argument('--cna',  action='store_true', help='')
        parser.add_argument('--cancer', type=str, default='HGSOC', help='HGSOC, OV, CANCER')
        parser.add_argument('--cnatype', type=str, help='AMP,DEL')
        parser.add_argument('--targetall', action='store_true', help='Query all targetable variants from OncoKB actionable target list')
        parser.add_argument('--fusgenes', type=str,  help='Give a list of fusion genes eg. BCR__ABL1,PML__PARA')
        parser.add_argument('--cgijobid', type=str, help='Download results from CGI by jobid')
        parser.add_argument('--cgiquery',  action='store_true', help='Download results from CGI by jobid')
        parser.add_argument('--oncokbcna',  action='store_true',  help='Query OncoKB by gene id from given patient CNA. Input parameter: gene id')
        parser.add_argument('--oncokbsnv', action='store_true',  help='Query OncoKB by genomic location parsed patient SNV. Input parameter: ref id')
        parser.add_argument('--sqlsnvs',  action='store_true', help='')
        parser.add_argument('--exonic',  action='store_true', help='')
        parser.add_argument('--actionable', action='store_true', help='Query by significant copy number threshold. Default is minimum of 8 copies for AMP or minimum ploidy 2, and 0 for DEL. For somatic mutations OncoKB actionable target list is used as reference.')
        parser.add_argument('--proteinchange',  action='store_true', help='')
        parser.add_argument('--genelist', type=str, help='')
        parser.add_argument('--logrthr', type=float, default=1.5, help='logr threshold for filtering by ploidy')
        parser.add_argument('--cnthr', type=int, default=9, help='Copy number threshold')
        parser.add_argument('--single', action='store_true', help='')
        parser.add_argument('--all', action='store_true', help='')
        parser.add_argument('--direct', action='store_true', help='')
        parser.add_argument('--retrieve', action='store_true', help='')
        parser.add_argument('--import_to_django', action='store_true', help='')
        parser.add_argument('--copy_number_alterations', type=str, help='')
        parser.add_argument('--somatic_variants', type=str, help='')


    def handle(self, *args, **kwargs):

    # OncoKB queries
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbcna --geneid=ENSG00000230280 --patientid=1"
        if kwargs["import_to_django"]:
            if kwargs["copy_number_alterations"]:
                cna_data = pd.read_csv(kwargs.get("copy_number_alterations", ""), sep="\t")
                cnadf_to_django_model(cna_data)
            if kwargs["somatic_variants"]:
                snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t")
                snvs_to_django_model(snvs)



        # if kwargs["oncokbsnv"] and kwargs["proteinchange"] and kwargs["cohortcode"]: # Query all exonic mutations for given patient
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snvs = get_actionable_snvs_by_aaChangeRefGene(pid)
        #     query_oncokb_somatic_mutations(snvs, kwargs["cancer"])
        # if kwargs["oncokbsnv"] and kwargs["exonic"] and kwargs["cohortcode"]: # Query all exonic mutations for given patient
        #     targets = ActionableTarget.objects.all()
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snvs = get_all_exonic_snvs_of_patient(pid, targets)
        #     query_oncokb_somatic_mutations(snvs, kwargs["cancer"])
        #     #chunks = [snvs[x:x+10] for x in range(0, len(snvs), 10)]
        #     #for c in chunks:
        #     #    query_oncokb_somatic_mutations(c, kwargs["cancer"])
        #     #    time.sleep(1)
        # if kwargs["oncokbcna"] and kwargs["targetall"] and kwargs["cohortcode"]:
        #     targets = ActionableTarget.objects.all()
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     cnas = get_cnas_by_gene_list(pid, targets)
        #     query_oncokb_cnas(cnas, kwargs["cancer"])
        #
        # if kwargs["oncokbcna"] and kwargs["actionable"] and kwargs["cohortcode"]:
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     targets = ActionableTarget.objects.all()
        #     cnas = get_cnas_by_cn_and_ploidy(pid, kwargs["cnthr"], targets)
        #     query_oncokb_cnas(cnas, kwargs["cancer"])
        #
        # if kwargs["oncokbsnv"] and kwargs["actionable"] and kwargs["cohortcode"] and not kwargs["single"]:
        #     targets = ActionableTarget.objects.all()
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snvs = get_snvs_by_gene_list(pid, targets)
        #     #chunks = [snvs[x:x + 30] for x in range(0, len(snvs), 30)]
        #     #for c in chunks:
        #     query_oncokb_somatic_mutations(snvs, kwargs["cancer"])
        #
        # if kwargs["oncokbsnv"] and kwargs["actionable"] and kwargs["cohortcode"] and kwargs["single"]:
        #     targets = ActionableTarget.objects.all()
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snvs = get_snvs_by_gene_list(pid, targets)
        #     for snv in snvs:
        #         query_oncokb_somatic_mutation(snv, kwargs["cancer"])
        #         #time.sleep(1)


        if kwargs["oncokbcna"] and kwargs["all"]:
            #for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
            #    cnas = cna_annotation.objects.filter(patient_id=pid.get('patient_id'))
            #   if cnas:
            query_oncokb_cnas_to_csv(cna_annotation.objects.all())

        if kwargs["oncokbsnv"] and kwargs["somatic_variants"] and kwargs["all"]:
            #for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
            #    cnas = cna_annotation.objects.filter(patient_id=pid.get('patient_id'))
            #   if cnas:
            snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t")

            snvs['hugoSymbol'] = ""
            snvs['entrezGeneId'] = ""
            snvs['tumorType'] = ""
            snvs['consequence'] = ""
            snvs['proteinStart'] = ""
            snvs['proteinEnd'] = ""
            snvs['oncogenic'] = ""
            snvs['mutationEffectDescription'] = ""
            snvs['gene_role'] = ""
            snvs['citationPMids'] = ""
            snvs['oncokb_level'] = ""
            snvs['geneSummary'] = ""
            snvs['variantSummary'] = ""
            snvs['tumorTypeSummary'] = ""
            snvs['prognosticSummary'] = ""
            snvs['diagnosticSummary'] = ""
            snvs['diagnosticImplications'] = ""
            snvs['prognosticImplications'] = ""
            snvs['treatments'] = ""

            chunks = [snvs[x:x + 4999] for x in range(0, len(snvs), 5000)]
            for c in chunks:
                query_oncokb_somatic_mutations(c)


    # CGI queries

        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --exonic --patientid=1"
        # if kwargs["cgiquery"] and kwargs["exonic"] and kwargs["snv"] and kwargs["cohortcode"]: # Query all exonic mutations for given patient
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snv = get_all_exonic_snvs_of_patient(pid)
        #     generate_temp_cgi_query_files(snv,[],[])
        #     jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext", None, None, kwargs["cancer"], "hg38")
        #     if jobid != 0:
        #         while query_cgi_job(pid, jobid.replace('"', '')) == 0:
        #             print("Waiting 120 seconds for the next try...")
        #             time.sleep(30)
        #  #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --proteinchange --patientid=1"
        # if kwargs["cgiquery"] and kwargs["proteinchange"] and kwargs["snv"] and kwargs["cohortcode"]: # Query all protein affecting mutations for all patients
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snvs = get_actionable_snvs_by_aaChangeRefGene(kwargs["patientid"])
        #     generate_proteinchange_query_file(snvs)
        #     jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/prot.ext", None, None, kwargs["cancer"], "hg38")
        #     while query_cgi_job(pid, jobid.replace('"', '')) == 0:
        #         print("Waiting 120 seconds for the next try...")
        #         time.sleep(120)

        # May be impossible to query every patient at once from cgi, could be done if distinct genes of every patient mapped to same query file
        # if kwargs["cgiquery"] and kwargs["cna"] and kwargs["targetall"] and kwargs["cohortcode"]:
        #     targets = ActionableTarget.objects.all()
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     cnas = get_cnas_by_gene_list(pid, targets)
        #     if cnas:
        #         generate_temp_cgi_query_files([], cnas, [])
        #         jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
        #         time.sleep(10)
        #         while query_cgi_job(pid, jobid.replace('"', '')) == 0:
        #             print("Waiting 30 seconds for the next try...")
        #             time.sleep(30)
        #
        # if kwargs["cgiquery"] and kwargs["cna"] and kwargs["actionable"] and kwargs["cohortcode"]:
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     targets = ActionableTarget.objects.all()
        #     cnas = get_cnas_by_cn_and_ploidy(pid, kwargs["cnthr"], targets)
        #     if cnas:
        #         genfiles = generate_temp_cgi_query_files([], cnas, [])
        #         if genfiles:
        #             jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
        #             time.sleep(10)
        #             if jobid != 0:
        #                 while query_cgi_job(pid, jobid.replace('"', '')) == 0:
        #                     print("Waiting 30 seconds for the next try...")
        #                     time.sleep(30)
        #         else:
        #             print("No cgi variant files generated!")
        #     else:
        #         print("No CNAs!")
        # if kwargs["cgiquery"] and kwargs["snv"] and kwargs["actionable"] and kwargs["cohortcode"]:
        #     targets = ActionableTarget.objects.all()
        #     pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
        #     snvs = get_snvs_by_gene_list(pid, targets)
        #     if snvs:
        #         generate_temp_cgi_query_files(snvs, [], [])
        #         jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext", None, None, kwargs["cancer"], "hg38")
        #         time.sleep(10)
        #         while query_cgi_job(pid, jobid.replace('"', '')) == 0:
        #                 print("Waiting 30 seconds for the next try...")
        #                 time.sleep(30)
