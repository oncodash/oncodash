import zipfile
import pandas as pd
import argparse

from datetime import datetime
import json

import httpx
from enum import Enum
import io
import time
import urllib3

CGI_LOGIN = ""
CGI_TOKEN = ""
ONCOKB_TOKEN = ""

class cna_alt_to_cgi(Enum):
    AMPLIFICATION = "AMP"
    DELETION = "DEL"
    def __str__(self):
        return str(self.value)

class cgi2oncokb_level(Enum):
    A = "LEVEL_1"
    B = "LEVEL_2"
    C = "LEVEL_3A"
    D = "LEVEL_3B"
    E = "LEVEL_4"
    R1 = "LEVEL_R1"
    R2 = "LEVEL_R2"
    def __str__(self):
        return str(self.value)

def map_cgi_evidence(biomarker):
    evidence = biomarker['Evidence']
    response = biomarker['Response']
    if pd.isna(evidence):
        return None
    if response == "Responsive":
        return cgi2oncokb_level[evidence].value
    if response == "Resistant":
        if cgi2oncokb_level[evidence] in ["LEVEL_1", "LEVEL_2"]:
            return cgi2oncokb_level["R1"].value
        if cgi2oncokb_level[evidence] in ["LEVEL_3A", "LEVEL_3B", "LEVEL_4"]:
            return cgi2oncokb_level["R2"].value
    return None

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
    return "" if pd.isna(value) else str(value)

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

def handle_treatments_oncokb(jsondata, alt_type, alteration):
    treatments = []
    for row in jsondata:
        drugs = ""
        print(row)
        if row["drugs"]:
            print(row["drugs"])
            for drug in row["drugs"]:
                print(drug)
                drugs += drug["drugName"]+";"
        pmids = ";".join(row['pmids'])
        approvedIndications = ";".join(row['approvedIndications'])
        tumortype = row['levelAssociatedCancerType']['mainType']['name']
        level = row['level']
        description = row['description']
        treatments.append(pd.Series({
            'alteration_type': alt_type,
            'alteration': alteration,
            'approvedIndications': approvedIndications,
            'description': description,
            'treatment': drugs,
            'level_of_evidence': level,
            'citations': pmids,
            'tumorType': tumortype
        }))
    return treatments

def handle_treatments_cgi(row, alt_type, alteration):

    drugs = row['Drugs']
    pmids = row['Source']
    approvedIndications = row['Biomarker']
    tumortype = row['Tumor type']
    level = map_cgi_evidence(row)
    description = ""
    return pd.Series({
        'alteration_type': alt_type,
        'alteration': alteration,
        'approvedIndications': approvedIndications,
        'description': description,
        'treatment': drugs,
        'level_of_evidence': level,
        'cgi_level': handle_string_field(row['Evidence'])+"("+handle_string_field(row['Response'])+")",
        'citations': pmids,
        'tumorType': tumortype
    })

def handle_drugs_field(jsondata):
    if jsondata:
        drugs = ""
        for rec in jsondata:
            darr = drugs.split(";")
            if rec["drugs"][0]["drugName"] not in darr:
                drugs += rec["drugs"][0]["drugName"]+";"
        return drugs[0:len(drugs)-1]
    else:
        return None


def query_oncokb_cnas_to_csv(cna_annotations: pd.DataFrame):

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

    token = ONCOKB_TOKEN

    api_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations"
    #request_url = api_url + 'copyNameAlterationType='+AlterationType[cna.CNstatus].value+'&hugoSymbol='+hugosymbol+'&tumorType='+tumorType
    header = {'accept':'application/json', 'Content-Type': 'application/json', 'Authorization':'Bearer '+token}

    print("Request OncoKB API "+api_url)

    # TODO: No need to query same alteration for every patient and sample, get unique by cnas[i].hugoSymbol cnas[i].alteration

    cnas = cna_annotations.groupby(
        ['hugoSymbol', 'alteration', 'referenceGenome', 'tumorType'])
    uniques = []
    for keys, group in cnas:
        uniques.append(dict(
            {'hugoSymbol': keys[0], 'alteration': keys[1], 'referenceGenome': keys[2], 'tumorType': keys[3]}))

    data = [
        {
            "copyNameAlterationType": f"{str.upper(cna['alteration'])}",
            "referenceGenome": f"{cna['referenceGenome']}",
            "gene": {
                "hugoSymbol": f"{str.upper(cna['hugoSymbol'])}",
            },
            "tumorType": f"{cna['tumorType']}",
        }
        for cna in uniques
    ]

    #header = str(header).replace("'",'"')
    #data = str(data).replace("'",'"')
    print("Querying " +str(len(uniques))+ " CNAs....")

    # Sending a POST request and getting back response as HTTPResponse object.
    #response = urllib3.PoolManager().request("POST", api_url, body=data, headers={'accept':'application/json','Content-Type':'application/json','Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    response = httpx.post(api_url, json=data, headers={'Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'}, timeout=None)
    #response = http.request("GET",request_url, headers=header)
    #print(response.data)
    #print(response.data.decode('utf-8'))

    #treatmentsdf = pd.DataFrame.from_dict({'alteration_type':[],'alteration':[],'approvedIndications':[],'description':[],'treatment':[],'level_of_evidence':[],'citations':[],'tumorType':[]})
    if (response.status_code == 200):
        treatments = []
        respjson = json.loads(response.text)

        for rjson in respjson:
            hugosymbol = handle_string_field(rjson["query"]["hugoSymbol"])
            #idsplit = str(cryptocode.decrypt(rjson["query"]["id"], settings.CRYPTOCODE)).split(":")
            #cna_id = idsplit[2]
            alteration = str.upper(handle_string_field(rjson["query"]["alteration"]))

            updatedf = cna_annotations.loc[(cna_annotations['hugoSymbol']==hugosymbol) & (cna_annotations['alteration']==alteration)]
            for indxs, row in updatedf.iterrows():
                cna_annotations.at[indxs,'hugoSymbol'] = handle_string_field(rjson["query"]["hugoSymbol"])
                cna_annotations.at[indxs,'tumorType'] = handle_string_field(rjson["query"]["tumorType"])
                cna_annotations.at[indxs,'consequence'] = handle_string_field(rjson["query"]["consequence"])
                #updatedf['proteinStart'] = handle_int_field(rjson["query"]["proteinStart"])
                #updatedf['proteinEnd'] = handle_int_field(rjson["query"]["proteinEnd"])
                cna_annotations.at[indxs,'oncogenic'] = handle_string_field(rjson["oncogenic"])
                cna_annotations.at[indxs,'mutationEffectDescription'] = handle_string_field(rjson["mutationEffect"]["description"])
                cna_annotations.at[indxs,'gene_role'] = handle_string_field(rjson["mutationEffect"]["knownEffect"])
                cna_annotations.at[indxs,'citationPMids'] = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"]))
                cna_annotations.at[indxs,'level_of_evidence'] = handle_string_field(rjson["highestSensitiveLevel"]) if handle_string_field(rjson["highestSensitiveLevel"]) else handle_string_field(rjson["highestResistanceLevel"])
                # Hematologic malignancies only
                #updatedf['prognosticSummary'] = handle_string_field(rjson["prognosticSummary"])
                #updatedf['diagnosticSummary'] = handle_string_field(rjson["diagnosticSummary"])
                #updatedf['diagnosticImplications'] = handle_string_field(rjson["diagnosticImplications"])
                #updatedf['prognosticImplications'] = handle_string_field(rjson["prognosticImplications"])
                cna_annotations.at[indxs,'geneSummary'] = handle_string_field(rjson["geneSummary"])
                cna_annotations.at[indxs,'variantSummary'] = handle_string_field(rjson["variantSummary"])
                cna_annotations.at[indxs,'tumorTypeSummary'] = handle_string_field(rjson["tumorTypeSummary"])
                cna_annotations.at[indxs,'treatments'] = handle_drugs_field(rjson["treatments"])

                treatments.extend(handle_treatments_oncokb(rjson["treatments"], 'CNA', hugosymbol + ':' + alteration))

            #print("Updated "+str(updatedf.count())+" CNAs")
        cna_annotations.drop(columns=cna_annotations.columns[0], axis=1, inplace=True)
        cna_annotations.to_csv("cna_annotated_oncokb.csv", sep="\t")
        trdf = pd.DataFrame(treatments)
        trdf.to_csv("treatments.csv", mode="a", sep="\t")
    else:
        print("Unable to request. Response: ", response.text)

    return response


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
    token = ONCOKB_TOKEN
    header = {"accept":"application/json", 'Content-Type': 'application/json', "Authorization":'Bearer '+token}
    request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange"
    #request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byHGVSg"

    snvs = snv_annotations.groupby(['chromosome', 'position', 'reference_allele', 'sample_allele', 'tumorType', 'referenceGenome'])
    uniques = []
    for keys, group in snvs:
        uniques.append(dict({'chromosome':keys[0], 'position':keys[1], 'reference_allele':keys[2], 'sample_allele':keys[3], 'tumorType':keys[4], 'referenceGenome':keys[5]}))

    data = [
        {
            "id": f"{row['chromosome']+':'+str(row['position'])+':'+row['reference_allele']+':'+row['sample_allele']}",
            "genomicLocation": f"{row['chromosome']+','+str(row['position'])+','+str(int(row['position'])+len(row['sample_allele']))+','+row['reference_allele']+','+row['sample_allele']}",
            "tumorType": f"{row['tumorType']}",
            "referenceGenome": f"{row['referenceGenome']}",
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
        treatments = []

        respjson = json.loads(response.text)
        for rjson in respjson:
            #print(rjson)
            #print("OBJ", rjson)
            id = str(rjson["query"]["id"])
            idsplit = id.split(":")
            chromosome = str(idsplit[0])
            position = int(idsplit[1])
            reference_allele = str(idsplit[2])
            sample_allele = str(idsplit[3])
            updatedf = snv_annotations.loc[(snv_annotations['chromosome']==chromosome) & (snv_annotations['position']==position) & (snv_annotations['reference_allele']==reference_allele) & (snv_annotations['sample_allele']==sample_allele)]

            for indxs, row in updatedf.iterrows():
                alteration = snv_annotations.at[indxs,'hugoSymbol']+":"+chromosome+":"+str(position)+":"+reference_allele+":"+sample_allele
                #snv_annotations.at[indxs,'hugoSymbol'] = handle_string_field(rjson["query"]["hugoSymbol"])
                snv_annotations.at[indxs, 'alteration'] = alteration
                snv_annotations.at[indxs,'tumorType'] = handle_string_field(rjson["query"]["tumorType"])
                #snv_annotations.at[indxs,'consequence'] = handle_string_field(rjson["query"]["consequence"])
                snv_annotations.at[indxs,'consequence_okb'] = handle_string_field(rjson["query"]["consequence"])
                snv_annotations.at[indxs,'oncogenic'] = handle_string_field(rjson["oncogenic"])
                snv_annotations.at[indxs,'mutationEffectDescription'] = handle_string_field(rjson["mutationEffect"]["description"])
                snv_annotations.at[indxs,'gene_role'] = handle_string_field(rjson["mutationEffect"]["knownEffect"])
                snv_annotations.at[indxs,'citationPMids'] = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"]))
                snv_annotations.at[indxs,'level_of_evidence'] = handle_string_field(rjson["highestSensitiveLevel"]) if handle_string_field(rjson["highestSensitiveLevel"]) else handle_string_field(rjson["highestResistanceLevel"])
                snv_annotations.at[indxs,'geneSummary'] = handle_string_field(rjson["geneSummary"])
                snv_annotations.at[indxs,'variantSummary'] = handle_string_field(rjson["variantSummary"])
                snv_annotations.at[indxs,'tumorTypeSummary'] = handle_string_field(rjson["tumorTypeSummary"])
                snv_annotations.at[indxs,'treatments'] = handle_drugs_field(rjson["treatments"])
                alteration = snv_annotations.at[indxs, 'alteration']
                treatments.extend(handle_treatments_oncokb(rjson["treatments"], 'SNV', alteration))

        print(snv_annotations)
        snv_annotations.drop(columns=snv_annotations.columns[0], axis=1, inplace=True)
        snv_annotations.to_csv("snv_annotated_oncokb.csv", index=False, mode='a', sep="\t")
        trdf = pd.DataFrame(treatments)
        trdf.to_csv("treatments.csv", mode="a", sep="\t")
        #print("Updated " + str(len(snvdf)) + " CNAs")
    else:
        print("[ERROR] Unable to request. Response: ", print(response.text))
        exit()

def launch_cgi_job_with_mulitple_variant_types(mutations_file, cnas_file, transloc_file, cancer_type, reference):
    """
        This function launches a CGI (Cancer Genome Interpreter) job with multiple variant types,
        using the CGI API. It takes in mutation, cnas, and translocation files, cancer type, and
        reference as input, and returns a job ID if the request is successful.

        Args:
        mutations_file (str): The path to the mutation file.
        cnas_file (str): The path to the cnas file.
        transloc_file (str): The path to the translocation file.
        cancer_type (str): The type of cancer.
        reference (str): The reference genome.

        Returns:
        jobid (str): The job ID if the request is successful.

        Raises:
        None.
        """

    request_url = "https://www.cancergenomeinterpreter.org/api/v1"
    login = CGI_LOGIN
    token = CGI_TOKEN

    print("Request CGI")
    # CGI api requires every type mutation files to be provided
    headers = {
        'Authorization': login+' '+token
    }

    if cnas_file:
        payload = {
            'cancer_type': cancer_type,
            'title': 'Title',
            'reference': reference,
            'cnas': ('cnas.ext', open(cnas_file, 'rb').read(), 'application/octet-stream')
        }
    if mutations_file:
        payload = {
            'cancer_type': cancer_type,
            'title': 'Title',
            'reference': reference,
            'mutations': ('snvs.ext', open(mutations_file, 'rb').read(), 'application/octet-stream'),
        }

    # Make the POST request using multipart/form-data with the files parameter
    http = urllib3.PoolManager()

    # Make the POST request using multipart/form-data with the files parameter
    response = http.request(
        'POST',
        'https://www.cancergenomeinterpreter.org/api/v1',
        fields=payload,
        headers=headers,
        multipart_boundary="----WebKitFormBoundary7MA4YWxkTrZu0gW",
        preload_content=False  # Set preload_content to False to allow streaming the files
    )

    # Attach the files using the files parameter


    # Send the request
    #response = http.urlopen(response)
    if (response.status == 200):

        jobid = response.data.decode("utf-8")
        print(jobid)
        return jobid

    else:
        print("[ERROR] Unable to request. Response: ", print(response.data))
        return 0


def query_cgi_job(jobid, snv_annotations: pd.DataFrame = None, cna_annotations: pd.DataFrame = None):
    """
      Query the CGI API with a job id and save the results to the database.

      Parameters:
          patient_id (int): The ID of the patient for whom the job was run.
          jobid (str): The job ID for the CGI job to query.

    """
    request_url = "https://www.cancergenomeinterpreter.org/api/v1/"
    print("Request CGI job by id")

    cgilogin = CGI_LOGIN
    cgitoken = CGI_TOKEN

    headers = {
        'Authorization': cgilogin + ' ' + cgitoken
    }
    payload = {'action': 'download'}
    # response = httpx.request("GET",request_url+jobid, headers=headers, fields=payload)
    response = httpx.get(request_url + jobid, params=payload, headers=headers, timeout=None)

    if response.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        fnames = z.namelist()
        treatmentsdf = None
        cgi_snvdf = None
        cgi_cnadf = None
        treatments = []
        for fn in fnames:
            # reader = z.open(f)
            # for row in reader.readlines():
            #    print(row)
            z.extract(fn)
            df = pd.read_csv(fn, sep="\t")
            print(fn)
            print(df)

            # Mutation response
            # ['Input ID', 'CHROMOSOME', 'POSITION', 'REF', 'ALT', 'chr', 'pos', 'ref','alt', 'ALT_TYPE', 'STRAND', 'CGI-Sample ID', 'CGI-Gene', 'CGI-Protein Change', 'CGI-Oncogenic Summary', 'CGI-Oncogenic Prediction', 'CGI-External oncogenic annotation','CGI-Mutation', 'CGI-Consequence', 'CGI-Transcript', 'CGI-STRAND', 'CGI-Type', 'CGI-HGVS', 'CGI-HGVSc', 'CGI-HGVSp']

            if fn == "alterations.tsv":
                cgi_snvdf = df
            if fn == "cna_analysis.tsv":
                cgi_cnadf = df
            if fn == "biomarkers.tsv":
                treatmentsdf = df

        bioms = treatmentsdf.loc[treatmentsdf['Match'] == 'YES']
        i = 0
        for index, biom in bioms.iterrows():
            # TODO: identify CNA and SNVs from ID and handle separately
            id = handle_string_field(biom["Sample ID"])
            idsplit = id.split(":")
            print(id)
            if idsplit[0] == "CNA":
                treatment = handle_treatments_cgi(biom, 'CNA', id)
                print(treatment)
                treatments.append(treatment)
                updatedf = cna_annotations.loc[
                    (((cna_annotations['oncogenic'] == "Unknown") |
                      (cna_annotations['oncogenic'].isna() == True)) & (
                             cna_annotations['hugoSymbol'] == idsplit[1]) & (
                             cna_annotations['alteration'] == idsplit[2]))]
                print(len(updatedf))

                for indxs, row in updatedf.iterrows():
                    i += 1
                    # snv_annotations.at[indxs, 'consequence_cgi'] = handle_string_field(row["CGI-Consequence"]),
                    cgi_cna = cgi_cnadf.loc[cgi_cnadf['sample'] == id].iloc[0]
                    cna_annotations.at[indxs, 'oncogenic'] = cna_annotations.at[
                                                                 indxs, 'oncogenic'] + " CGI:" + handle_string_field(
                        cgi_cna["driver"])
                    # snv_annotations.at[indxs,'mutationEffectDescription'] = handle_string_field(rjson["mutationEffect"]["description"])
                    cna_annotations.at[indxs, 'gene_role'] = cna_annotations.at[
                                                                 indxs, 'gene_role'] + " CGI:" + handle_string_field(
                        cgi_cna["gene_role"]),
                    # snv_annotations.at[indxs,'citationPMids'] = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"]))
                    # TODO: Evidence level is related to drug not alteration, show highest in level_of_evidence, treatments table include all levels
                    # level = map_cgi_evidence(biom)
                    # if level < cna_annotations.at[indxs, 'level_of_evidence']:
                    #    cna_annotations.at[indxs, 'level_of_evidence'] = "CGI:"+map_cgi_evidence(biom)
                    evid = handle_string_field(biom['Evidence']) + "(" + handle_string_field(biom['Response']) + ")"
                    cna_annotations.at[indxs, 'cgi_level'] = evid
                    # snv_annotations.at[indxs, 'geneSummary'] = handle_string_field(rjson["geneSummary"])
                    # snv_annotations.at[indxs, 'variantSummary'] = handle_string_field(row["CGI-External oncogenic annotation"])
                    cna_annotations.at[indxs, 'tumorTypeSummary'] = str(
                        cna_annotations.at[indxs, 'tumorTypeSummary']) + " CGI:" + handle_string_field(
                        cgi_cna["driver_statement"])
                    # snv_annotations.at[indxs, 'treatments'] = handle_drugs_field(rjson["treatments"])
                    # alteration = snv_annotations.at[indxs, 'alteration'].value

            if idsplit[0] == "SNV":
                chromosome = str(idsplit[1])
                position = int(idsplit[2])
                reference_allele = str(idsplit[3])
                sample_allele = str(idsplit[4])
                treatment = handle_treatments_cgi(biom, 'SNV', id)
                print(treatment)
                treatments.append(treatment)
                # TODO: try update only if oncokb oncogenic result is None e.g. not known by oncokb
                updatedf = snv_annotations.loc[
                    (((snv_annotations['oncogenic'] == "Unknown") | (snv_annotations['oncogenic'].isna() == True)) & (
                            snv_annotations['chromosome'] == chromosome) & (
                             snv_annotations['position'] == position) & (
                             snv_annotations['reference_allele'] == reference_allele) & (
                             snv_annotations['sample_allele'] == sample_allele))]
                print("SNV updatedf:"+str(len(updatedf)))

                for indxs, row in updatedf.iterrows():
                    # snv_annotations.at[indxs, 'consequence_cgi'] = handle_string_field(row["CGI-Consequence"]),
                    cgi_snv = cgi_snvdf.loc[cgi_snvdf['CGI-Sample ID'] == id].iloc[0]
                    snv_annotations.at[indxs, 'oncogenic'] = snv_annotations.at[indxs, 'oncogenic'] + " CGI:" + handle_string_field(cgi_snv["CGI-Oncogenic Summary"])
                    # snv_annotations.at[indxs,'mutationEffectDescription'] = handle_string_field(rjson["mutationEffect"]["description"])
                    #snv_annotations.at[indxs, 'gene_role'] = snv_annotations.at[indxs, 'gene_role']  + " CGI:" + handle_string_field(cgi_snv["CGI-Oncogenic Prediction"]),
                    # snv_annotations.at[indxs,'citationPMids'] = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"]))
                    # TODO: Evidence level is related to drug not alteration, show highest in level_of_evidence, treatments table include all levels
                    # level = map_cgi_evidence(biom)
                    # if level < snv_annotations.at[indxs, 'level_of_evidence']:
                    # snv_annotations.at[indxs, 'level_of_evidence'] = map_cgi_evidence(biom)
                    snv_annotations.at[indxs, 'cgi_level'] = handle_string_field(
                        biom['Evidence']) + "(" + handle_string_field(biom['Response']) + ")"
                    # snv_annotations.at[indxs, 'geneSummary'] = handle_string_field(rjson["geneSummary"])
                    # snv_annotations.at[indxs, 'variantSummary'] = handle_string_field(row["CGI-External oncogenic annotation"])
                    # snv_annotations.at[indxs, 'tumorTypeSummary'] =  str(snv_annotations.at[indxs, 'tumorTypeSummary']) +" CGI:"+ handle_string_field(cgi_snv["driver_statement"])
                    # snv_annotations.at[indxs, 'treatments'] = handle_drugs_field(rjson["treatments"])
                    # alteration = snv_annotations.at[indxs, 'alteration'].value

        if isinstance(snv_annotations, pd.DataFrame):
            #snv_annotations.drop(columns=snv_annotations.columns[0], axis=1, inplace=True)
            snv_annotations.to_csv("snv_annotated_cgi.csv", index=False, sep="\t")
            trdf = pd.DataFrame(treatments)
            trdf.to_csv("treatments_cgi_snv.csv", index=False, sep="\t")

        if isinstance(cna_annotations, pd.DataFrame):
        # cna_annotations.drop(columns=cna_annotations.columns[0], axis=1, inplace=True)
            cna_annotations.to_csv("cna_annotated_cgi.csv", index=False, sep="\t")
            trdf = pd.DataFrame(treatments)
            trdf.to_csv("treatments_cgi_cna.csv", index=False, sep="\t")

        return 1
    else:
    #print(response.status_code)
        print("No CGI results available for job id: "+str(jobid))
        return 0

def gene_id_convert(geneids, target):
    # geneids given as list with whitespace separator, target can be one of the target namespaces in https://biit.cs.ut.ee/gprofiler/convert
    request_url = "https://biit.cs.ut.ee/gprofiler/api/convert/convert/"
    print("Request gProfiler API "+request_url)
    data = '{"organism":"hsapiens", "target":"'+target+'", "query":"'+geneids+'"}'
    #{"organism":"hsapiens", "target":target, "query":geneids}
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode('utf-8')
    response = httpx.post(request_url, json=body, headers=headers, timeout=None)

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

def generate_temp_cgi_query_files(snv_annotations: pd.DataFrame = None, cna_annotations: pd.DataFrame = None, translocs: pd.DataFrame = None):

    header = "chr\tpos\tref\talt\tsample\n"
    try:
        if isinstance(snv_annotations, pd.DataFrame):
            with open("./tmp/snvs.ext", "w") as file1:
                file1.write(header)

                uniques = snv_annotations[['chromosome', 'position', 'reference_allele', 'sample_allele', 'tumorType', 'referenceGenome']].drop_duplicates()
                for indx, snv in uniques.iterrows():
                    id = "SNV:"+snv['chromosome']+':'+str(snv['position'])+':'+snv['reference_allele']+':'+snv['sample_allele']
                    row = snv['chromosome']+'\t'+str(snv['position'])+'\t'+snv['reference_allele']+'\t'+snv['sample_allele']+'\t'+id+'\n' #+'\t'+cryptocode.encrypt(snv.samples, settings.CRYPTOCODE)+'\n'
                    file1.write(row)
                file1.close()

        if isinstance(cna_annotations, pd.DataFrame):
            header = "gene\tcna\tsample\n"
            with open("./tmp/cnas.ext", "w") as file2:
                file2.write(header)

                uniques = cna_annotations[['hugoSymbol', 'alteration', 'referenceGenome', 'tumorType']].drop_duplicates()
                print(type(uniques))
                for indx, cna in uniques.iterrows():
                    print(cna)
                    id = "CNA:"+str(cna['hugoSymbol']) + ':' + str(cna['alteration'])
                    row = cna['hugoSymbol']+'\t'+cna_alt_to_cgi[cna['alteration']].value+'\t'+id+'\n'#+'\t'+cryptocode.encrypt(cna.sample_id, settings.CRYPTOCODE)+'\n'
                    file2.write(row)
                file2.close()

        # header = "fus\tsample\n"
        # with open("./tmp/fus.ext", "w") as file3:
        #     file3.write(header)
        #     for transloc in translocs:
        #         row = transloc+'\t'+cryptocode.encrypt(transloc.sample, settings.CRYPTOCODE)+'\n'
        #         file3.write(row)
        #     file3.close()
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise
    return 1

# def cnadf_to_django_model(cnadf):
#     cnaobjects = []
#     for index, row in cnadf.iterrows():
#         cnaobjects.append(cna_annotation(
#             patient_id=handle_string_field(row["patient_id"]),  # sample name includes cohort code which is mapped to patient id
#             sample_id=handle_string_field(row["sample_id"]),
#             referenceGenome=row["referenceGenome"],
#             hugoSymbol=handle_string_field(row["hugoSymbol"]),
#             alteration=handle_string_field(row["alteration"]),
#             tumorType=handle_string_field(row["tumorType"]),
#             nMajor=handle_int_field(row["nMajor"]),
#             nMinor=handle_int_field(row["nMinor"]),
#             lohstatus=handle_string_field(row["lohstatus"]),
#             ploidy=handle_decimal_field(row["ploidy"])
#         ))
#     try:
#         objs = cna_annotation.objects.bulk_create(cnaobjects)
#         print("Imported " + str(len(objs)) + " records.")
#     except Exception as e:
#         print("Exception: ", e)
#
#
# def snvs_to_django_model(snvs):
#     snvobjs = []
#     for index, row in snvs.iterrows():
#         snvobjs.append(snv_annotation(
#             patient_id=handle_string_field(row["patient_id"]),
#             # sample name includes cohort code which is mapped to patient id
#             sample_id=handle_string_field(row["sample_id"]),
#             referenceGenome=row["referenceGenome"],
#             ref_id=handle_string_field(row["ref_id"]),
#             chromosome=handle_string_field(row["chromosome"]),
#             position=handle_int_field(row["position"]),
#             reference_allele=handle_string_field(row["reference_allele"]),
#             sample_allele=handle_string_field(row["sample_allele"]),
#             hugoSymbol=handle_string_field(row["hugoSymbol"]),
#             # entrezGeneId = "",
#             # alteration: string;
#             tumorType=handle_string_field(row["tumorType"]),
#             consequence=handle_string_field(row["consequence"]),
#             # proteinStart: string;
#             # proteinEnd: string;
#             # oncogenic: string;
#             # mutationEffectDescription: string;
#             # gene_role: string;
#             # citationPMids: string;
#             # geneSummary: string;
#             # variantSummary: string;
#             # tumorTypeSummary: string;
#             # diagnosticSummary: string;
#             # diagnosticImplications: string;
#             # prognosticImplications: string;
#             # treatments: string;
#             nMinor=handle_int_field(row["nMinor"]),
#             nMajor=handle_int_field(row["nMajor"]),
#             # oncokb_level: string;
#             # cgi_level: string;
#             # rank: number;
#             ad0=handle_decimal_field(row["ad0"]),
#             ad1=handle_decimal_field(row["ad1"]),
#             af=handle_decimal_field(row["af"]),
#             depth=handle_decimal_field(row["depth"]),
#             lohstatus=handle_string_field(row["lohstatus"]),
#             hom_lo=handle_decimal_field(row["hom_lo"]),
#             hom_hi=handle_decimal_field(row["hom_hi"]),
#             hom_pbinom_lo=handle_decimal_field(row["hom_pbinom_lo"]),
#             homogenous=handle_string_field(row["homogenous"]),
#             cadd_score=handle_decimal_field(row["cadd_score"]),
#             ada_score=handle_decimal_field(row["ada_score"]),
#             rf_score=handle_decimal_field(row["rf_score"]),
#             amis_score=handle_decimal_field(["amis_score"]),
#             cosmic_id=handle_string_field(row["cosmic_id"]),
#             clinvar_id=handle_string_field(row["clinvar_id"]),
#             clinvar_sig=handle_string_field(row["clinvar_sig"]),
#             clinvar_status=handle_string_field(row["clinvar_status"]),
#             clinvar_assoc=handle_string_field(row["clinvar_assoc"]),
#             pathogenecity=handle_string_field(row["pathogenecity"]),
#             classification=handle_string_field(row["classification"])
#             # sift_cat: string;
#             # sift_val: number;  # Will be dded to WGS output in near future https://sift.bii.a-star.edu.sg/
#             # polyphen_cat: string;
#             # polyphen_val: number;  # Will be dded to WGS output in near future http://genetics.bwh.harvard.edu/pph2/
#
#         ))
#
#     try:
#         objs = snv_annotation.objects.bulk_create(snvobjs)
#         print("Imported " + str(len(objs)) + " records.")
#     except Exception as e:
#         print(e)

def main(**kwargs):

# OncoKB queries
    #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbcna --geneid=ENSG00000230280 --patientid=1"
    # if kwargs["import_to_django"]:
    #     if kwargs["copy_number_alterations"]:
    #         cna_data = pd.read_csv(kwargs.get("copy_number_alterations", ""), sep="\t")
    #         cnadf_to_django_model(cna_data)
    #     if kwargs["somatic_variants"]:
    #         snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t")
    #         snvs_to_django_model(snvs)



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


    if kwargs["oncokbcna"] and kwargs["copy_number_alterations"] and kwargs["all"]:
        #for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
        #    cnas = cna_annotation.objects.filter(patient_id=pid.get('patient_id'))
        #   if cnas:
        cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t")
        query_oncokb_cnas_to_csv(cnas)


    if kwargs["oncokbsnv"] and kwargs["somatic_variants"] and kwargs["all"]:
        #for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
        #    cnas = cna_annotation.objects.filter(patient_id=pid.get('patient_id'))
        #   if cnas:
        snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t")

        snvs['tumorType'] = ""
        snvs['consequence_okb'] = ""
        snvs['oncogenic'] = ""
        snvs['mutationEffectDescription'] = ""
        snvs['gene_role'] = ""
        snvs['citationPMids'] = ""
        snvs['level_of_evidence'] = ""
        snvs['cgi_level'] = ""
        snvs['geneSummary'] = ""
        snvs['variantSummary'] = ""
        snvs['tumorTypeSummary'] = ""
        snvs['treatments'] = ""

        chunks = [snvs[x:x + 4999] for x in range(0, len(snvs), 5000)]
        for c in chunks:
            query_oncokb_somatic_mutations(c)

    if kwargs["cgiquery"] and kwargs["somatic_variants"] and kwargs["all"]:
        snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t", dtype='string')
        if kwargs["cgijobid"]:
            jobid = kwargs["cgijobid"]
        else:
            generate_temp_cgi_query_files(snvs, None, None)
            jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext",None, None, "OVSE", "hg38").replace('"', '')
        time.sleep(30)
        while query_cgi_job(jobid, snvs) == 0:
            print("Waiting 30 seconds for the next try...")
            time.sleep(30)

    if kwargs["cgiquery"] and kwargs["copy_number_alterations"] and kwargs["all"]:
        cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t", dtype='string')
        if kwargs["cgijobid"]:
            jobid = kwargs["cgijobid"]
        else:
            generate_temp_cgi_query_files(None, cnas, None)
            jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, "OVSE", "hg38").replace('"', '')

        time.sleep(30)
        while query_cgi_job(jobid, None, cnas) == 0:
            print("Waiting 30 seconds for the next try...")
            time.sleep(30)

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

if __name__ == "__main__":

    def add_arguments(parser):
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


    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    main(**vars(args))
