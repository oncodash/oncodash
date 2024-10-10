import io
import logging
import time
import zipfile
from itertools import chain

import pandas as pd
import urllib3

from datetime import datetime
import json

http = urllib3.PoolManager()

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

def handle_list_field(value):
    return None if len(value)==0 else value

def handle_int_field(value):
    return None if pd.isna(value) else value

def handle_date_field(value):

    return None if pd.isna(value) else datetime.strptime(value, "%m/%d/%Y")

def handle_cgi_response_field(biomarker):
    evidence = biomarker['evidence']
    response = biomarker['response']
    return None if pd.isna(response) else CGI2OncoKBLevels[evidence].value

def handle_cgi_resistance_field(biomarker):
    evidence = biomarker['evidence']
    resistance = biomarker['resistance']
    if pd.isna(resistance):
        return None
    else:
        if CGI2OncoKBLevels[evidence] in ["LEVEL_1", "LEVEL_2"]:
            return CGI2OncoKBLevels["R1"]
        if CGI2OncoKBLevels[evidence] in ["LEVEL_3A", "LEVEL_3B", "LEVEL_4"]:
            return CGI2OncoKBLevels["R2"]
    return None

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
def get_cna(patient_id, gene_id):
    try:
        for rec in CopyNumberAlteration.objects.filter(patient_id=patient_id, gene_id=gene_id):
            return rec

    except Exception as e:
        logging.exception(e)
        print("No CNAfor", patient_id, gene_id, "available in the database")

def get_cna_by_gene(patient_id, gene):
    try:
        for rec in CopyNumberAlteration.objects.filter(patient_id=patient_id, gene=gene):
            return rec

    except Exception as e:
        logging.exception(e)
        print("No CNA for", patient_id, gene, "available in the database")

def get_cnas_by_gene_list(patient_id, targets):
    try:
        return CopyNumberAlteration.objects.filter(patient_id=patient_id).filter(gene__in=targets).exclude(CNstatus="Normal")

    except Exception as e:
        logging.exception(e)
        print("No CNAs for patient", patient_id, "available in the database")

def get_snvs_by_gene_list(patient_id, targets):
    try:
        actionable = []
        for gene in targets:
            actionable.append(SomaticVariant.objects.filter(patient_id=patient_id).filter(Q(geneMANE__contains=str(gene.gene)) | Q(geneRefGene__contains=str(gene.gene))))
        joined = list(chain(*actionable))
        for g in joined:
            print(g.geneMANE)
        return joined
    except Exception as e:
        logging.exception(e)
        print("No SNVs for patient", patient_id, "available in the database")
def get_cnas(patient_id):
    try:
        return CopyNumberAlteration.objects.filter(patient_id=patient_id)

    except Exception as e:
        logging.exception(e)
        print("No CNAs for patient", patient_id, "available in the database")

def get_cnas_by_cn_and_ploidy(patient_id, cnthreshold = 9, targets=None):
    try:
        #ascat_ests_qs = CNAscatEstimate.objects.all().filter(patient_id=patient_id)

        # Filter significant CNAs by purifiedLogR >= 1.5 (median 9 copies) or nMajor+nMinor >= 2.5*ploidy == Amplification,  nMajor+nMinor=0 == Deletion
        dels = CopyNumberAlteration.objects.filter(patient_id=patient_id).annotate(cn=F('nMinor') + F('nMajor')).filter(cn=0)
        for d in dels:
            print("q: ",d.gene)
            d.CNstatus="DEL"
            d.save()

        #cnthreshold = 2.5*(2**1.5)

        amps = CopyNumberAlteration.objects.filter(patient_id=patient_id).annotate(cn=F('nMinor') + F('nMajor')).filter(Q(cn__gte=cnthreshold))
        for a in amps:
            print("q: ",a.gene)
            a.CNstatus="AMP"
            a.save()
        # Filter by gene target list
        if targets:
            ap = amps.filter(gene__in=targets)
            for a in ap:
                print(a.gene)
            return dels.filter(gene__in=targets).union(amps.filter(gene__in=targets))
        else:
            for a in amps:
                print(a.gene)
            return dels.union(amps)

    except Exception as e:
        logging.exception(e)
        print("No CNAs for patient", patient_id, "available in the database")

def get_cnas_by_type(patient_id, cnatype):
    try:
        return CopyNumberAlteration.objects.filter(patient_id=patient_id, CNstatus=cnatype)

    except Exception as e:
        logging.exception(e)
        print("No CNAs for patient", patient_id, "available in the database")

def get_cnas_by_type_and_gene(patient_id, cnatype, gene):
    try:
        return CopyNumberAlteration.objects.filter(patient_id=patient_id, CNstatus=cnatype, gene=gene)

    except Exception as e:
        logging.exception(e)
        print("No CNAs for patient", patient_id, "available in the database")

def get_snv(patient_id, ref_id):
    try:
        for rec in SomaticVariant.objects.filter(patient_id=patient_id, ref_id=ref_id):
            return rec

    except Exception as e:
        logging.exception(e)
        print("No SNV", ref_id, "available in the database")

def get_actionable_snvs_by_aaChangeRefGene(patient_id):
    try:
        return SomaticVariant.objects.filter(patient_id=patient_id).exclude(aaChangeRefGene=".")

    except Exception as e:
        logging.exception(e)
        print("No actionable SNV for patient ", patient_id, "available in the database")

def get_all_actionable_snvs_by_aaChangeRefGene():
    try:
        return SomaticVariant.objects.exclude(aaChangeRefGene=".")

    except Exception as e:
        logging.exception(e)
        print("No actionable SNVs available in the database")

def get_all_exonic_snvs_of_patient(patient_id, targets=None):
    try:
        if targets:
            actionable = []
            for gene in targets:
                actionable.append(SomaticVariant.objects.filter(patient_id=patient_id, funcRefGene="exonic").filter(Q(geneMANE__contains=str(gene.gene)) | Q(geneRefGene__contains=str(gene.gene))))
            joined = list(chain(*actionable))
            return joined
        else:
            return SomaticVariant.objects.filter(patient_id=patient_id, funcRefGene="exonic")

    except Exception as e:
        logging.exception(e)
        print("No exonic SNV for patient ", patient_id, "available in the database")

def get_all_exonic_snvs():
    try:
        return SomaticVariant.objects.filter(funcRefGene="exonic")

    except Exception as e:
        logging.exception(e)
        print("No exonic SNVs available in the database")


def query_cgi_job(patient_id, jobid):
    """
      Query the CGI API with a job id and save the results to the database.

      Parameters:
          patient_id (int): The ID of the patient for whom the job was run.
          jobid (str): The job ID for the CGI job to query.

    """
    request_url = "https://www.cancergenomeinterpreter.org/api/v1/"
    print("Request CGI job by id")

    cgilogin = settings.CGI_LOGIN
    cgitoken = settings.CGI_TOKEN

    headers = {
        'Authorization': cgilogin + ' ' + cgitoken
    }
    payload = {'action':'download'}
    response = http.request("GET",request_url+jobid, headers=headers, fields=payload)

    if response.status == 200:
        z = zipfile.ZipFile(io.BytesIO(response.data))
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
            #['Input ID', 'CHROMOSOME', 'POSITION', 'REF', 'ALT', 'chr', 'pos', 'ref','alt', 'ALT_TYPE', 'STRAND', 'CGI-Sample ID', 'CGI-Gene', 'CGI-Protein Change', 'CGI-Oncogenic Summary', 'CGI-Oncogenic Prediction', 'CGI-External oncogenic annotation','CGI-Mutation', 'CGI-Consequence', 'CGI-Transcript', 'CGI-STRAND', 'CGI-Type', 'CGI-HGVS', 'CGI-HGVSc', 'CGI-HGVSp']

            if fn == "alterations.tsv":
                for index, row in df.iterrows():
                    #if handle_string_field(row["CGI-Oncogenic Prediction"]) != None and handle_string_field(row["CGI-Oncogenic Prediction"]).find("driver") <= 0:
                    #    continue
                    try:
                        print("alterations: ", row.keys)
                        print("Alterations: ", row.values)
                        rec, created = CGIMutation.objects.get_or_create(
                            patient_id      = int(patient_id),
                            sample = handle_string_field(cryptocode.decrypt(row["CGI-Sample ID"], settings.CRYPTOCODE)),
                            gene  = handle_string_field(row["CGI-Gene"]),
                            protein_change   = handle_string_field(row["CGI-Protein Change"]),
                            oncogenic_summary    = handle_string_field(row["CGI-Oncogenic Summary"]),
                            oncogenic_prediction      = handle_string_field(row["CGI-Oncogenic Prediction"]),
                            ext_oncogenic_annotation  = handle_string_field(row["CGI-External oncogenic annotation"]),
                            mutation = handle_string_field(row["CGI-Mutation"]),
                            consequence = handle_string_field(row["CGI-Consequence"]),
                            transcript = handle_string_field(row["CGI-Transcript"]),
                            strand = handle_string_field(row["CGI-STRAND"]),
                            type = handle_string_field(row["CGI-Type"])
                        )
                        rec.save()
                    except Exception as e:
                        logging.exception(e)
                        pass


            # CNA Query
            # gene	cna
            # ERBB2	AMP
            # CNA response
            # sample	gene	cna	predicted_in_tumors	known_in_tumors	gene_role	cancer	internal_id	driver	driver_statement	predicted_match	known_match
            # single_sample	ERBB2	AMP	CESC;ESCA;HNSC;LUAD;PAAD;STAD;UCEC	BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED	Act	OVE	0	known	known in: BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED
            if fn == "cna_analysis.tsv":
                cnas = df.loc[~(df['driver_statement'] == 'known')]
                for index, row in cnas.iterrows():
                    try:
                        print("cna_analysis: ", row.keys)
                        print("cna_analysis: ", row.values)

                        rec, created = CGICopyNumberAlteration.objects.get_or_create(
                            patient_id   = int(patient_id),
                            sample = handle_string_field(cryptocode.decrypt(row["sample"], settings.CRYPTOCODE)),
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
                        logging.exception(e)
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
                            sample = handle_string_field(cryptocode.decrypt(row["sample"], settings.CRYPTOCODE)),
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
                        logging.exception(e)
                        pass

            # Sample ID	Alterations	Biomarker	Drugs	Diseases	Response	Evidence	Match	Source	BioM	Resist.	Tumor type
            # single_sample	ABL1__BCR 	ABL1 (T315I,V299L,G250E,F317L)	Bosutinib (BCR-ABL inhibitor 3rd gen)	Acute lymphoblastic leukemia, Chronic myeloid leukemia	Resistant	A	NO	cgi	only gene		ALL, CML
            if fn == "biomarkers.tsv":
                bioms = df.loc[df['Match'] == 'YES']
                for index, row in bioms.iterrows():
                    try:

                        print("biomarkers: : ", row.keys)
                        rec, created = CGIDrugPrescriptions.objects.get_or_create(
                            patient_id  = int(patient_id),
                            sample = handle_string_field(cryptocode.decrypt(row["Sample ID"], settings.CRYPTOCODE)),
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
                        logging.exception(e)
                        pass
        return 1
    else:
        print(response.status)
        print("No CGI results available for job id: "+str(jobid))
        return 0


def query_cgi_job_merge_db(patient_id, jobid):
    """
      Query the CGI API with a job id and save the results to the database.

      Parameters:
          patient_id (int): The ID of the patient for whom the job was run.
          jobid (str): The job ID for the CGI job to query.

    """
    request_url = "https://www.cancergenomeinterpreter.org/api/v1/"
    print("Request CGI job by id")

    cgilogin = settings.CGI_LOGIN
    cgitoken = settings.CGI_TOKEN

    headers = {
        'Authorization': cgilogin + ' ' + cgitoken
    }
    payload = {'action':'download'}
    response = http.request("GET",request_url+jobid, headers=headers, fields=payload)

    if response.status == 200:
        z = zipfile.ZipFile(io.BytesIO(response.data))
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

            if fn == "biomarkers.tsv":
                bioms = df.loc[df['Match'] == 'YES']
                for index, row in bioms.iterrows():
                    try:
                        rec, created = CGIDrugPrescriptions.objects.get_or_create(
                            patient_id  = int(patient_id),
                            sample = handle_string_field(cryptocode.decrypt(row["Sample ID"], settings.CRYPTOCODE)),
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
                        logging.exception(e)
                        pass

            # Mutation Query
            # chr	pos	ref	alt
            # chr3	178936091	G	A

            # Mutation response
            #['Input ID', 'CHROMOSOME', 'POSITION', 'REF', 'ALT', 'chr', 'pos', 'ref','alt', 'ALT_TYPE', 'STRAND', 'CGI-Sample ID', 'CGI-Gene', 'CGI-Protein Change', 'CGI-Oncogenic Summary', 'CGI-Oncogenic Prediction', 'CGI-External oncogenic annotation','CGI-Mutation', 'CGI-Consequence', 'CGI-Transcript', 'CGI-STRAND', 'CGI-Type', 'CGI-HGVS', 'CGI-HGVSc', 'CGI-HGVSp']

            if fn == "alterations.tsv":
                for index, row in df.iterrows():
                    #if handle_string_field(row["CGI-Oncogenic Prediction"]) != None and handle_string_field(row["CGI-Oncogenic Prediction"]).find("driver") <= 0:
                    #    continue

                    try:
                        rec, created = CGIMutation.objects.get_or_create(
                            patient_id      = int(patient_id),
                            sample = handle_string_field(cryptocode.decrypt(row["CGI-Sample ID"], settings.CRYPTOCODE)),
                            gene  = handle_string_field(row["CGI-Gene"]),
                            protein_change   = handle_string_field(row["CGI-Protein Change"]),
                            oncogenic_summary    = handle_string_field(row["CGI-Oncogenic Summary"]),
                            oncogenic_prediction      = handle_string_field(row["CGI-Oncogenic Prediction"]),
                            ext_oncogenic_annotation  = handle_string_field(row["CGI-External oncogenic annotation"]),
                            mutation = handle_string_field(row["CGI-Mutation"]),
                            consequence = handle_string_field(row["CGI-Consequence"]),
                            transcript = handle_string_field(row["CGI-Transcript"]),
                            strand = handle_string_field(row["CGI-STRAND"]),
                            type = handle_string_field(row["CGI-Type"])
                        )
                        # rec, created = OncoKBAnnotation.objects.get_or_create(
                        #     patient_id=int(patient_id),
                        #     sample_id=handle_string_field(cryptocode.decrypt(row["CGI-Sample ID"], settings.CRYPTOCODE)),
                        #     hugoSymbol=handle_string_field(row["CGI-Gene"]),
                        #     #entrezGeneId=handle_string_field(rjson["query"]["entrezGeneId"]),
                        #     alteration=handle_string_field(rjson["query"]["alteration"]),
                        #     #alterationType=handle_string_field(rjson["query"]["alterationType"]),
                        #     svType=handle_string_field(rjson["query"]["svType"]),
                        #     tumorType=handle_string_field(rjson["query"]["tumorType"]),
                        #     consequence=handle_string_field(rjson["query"]["consequence"]),
                        #     proteinStart=handle_int_field(rjson["query"]["proteinStart"]),
                        #     proteinEnd=handle_int_field(rjson["query"]["proteinEnd"]),
                        #     hgvs=handle_string_field(rjson["query"]["hgvs"]),
                        #     geneExist=handle_boolean_field(rjson["geneExist"]),
                        #     variantExist=handle_boolean_field(rjson["variantExist"]),
                        #     alleleExist=handle_boolean_field(rjson["alleleExist"]),
                        #     oncogenic=handle_string_field(rjson["oncogenic"]),
                        #     mutationEffectDescription=handle_string_field(rjson["mutationEffect"]["description"]),
                        #     knownEffect=handle_string_field(rjson["mutationEffect"]["knownEffect"]),
                        #     citationPMids=handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"])),
                        #     citationAbstracts=handle_string_field(
                        #         str(rjson["mutationEffect"]["citations"]["abstracts"])),
                        #     highestSensitiveLevel=handle_string_field(rjson["highestSensitiveLevel"]),
                        #     highestResistanceLevel=handle_string_field(rjson["highestResistanceLevel"]),
                        #     highestDiagnosticImplicationLevel=handle_string_field(
                        #         rjson["highestDiagnosticImplicationLevel"]),
                        #     highestPrognosticImplicationLevel=handle_string_field(
                        #         rjson["highestPrognosticImplicationLevel"]),
                        #     highestFdaLevel=handle_string_field(rjson["highestFdaLevel"]),
                        #     otherSignificantSensitiveLevels=handle_string_field(
                        #         rjson["otherSignificantSensitiveLevels"]),
                        #     otherSignificantResistanceLevels=handle_string_field(
                        #         rjson["otherSignificantResistanceLevels"]),
                        #     hotspot=handle_boolean_field(rjson["hotspot"]),
                        #     geneSummary=handle_string_field(rjson["geneSummary"]),
                        #     variantSummary=handle_string_field(rjson["variantSummary"]),
                        #     tumorTypeSummary=handle_string_field(rjson["tumorTypeSummary"]),
                        #     prognosticSummary=handle_string_field(rjson["prognosticSummary"]),
                        #     diagnosticSummary=handle_string_field(rjson["diagnosticSummary"]),
                        #     diagnosticImplications=handle_string_field(rjson["diagnosticImplications"]),
                        #     prognosticImplications=handle_string_field(rjson["prognosticImplications"]),
                        #     treatments=handle_treatments_field(rjson["treatments"]),
                        #     dataVersion=handle_string_field(rjson["dataVersion"]),
                        #     lastUpdate=handle_date_field(rjson["lastUpdate"]),
                        #     vus=handle_boolean_field(rjson["vus"])
                        # )

                        rec.save()
                    except Exception as e:
                        logging.exception(e)
                        pass


            # CNA Query
            # gene	cna
            # ERBB2	AMP
            # CNA response
            # sample	gene	cna	predicted_in_tumors	known_in_tumors	gene_role	cancer	internal_id	driver	driver_statement	predicted_match	known_match
            # single_sample	ERBB2	AMP	CESC;ESCA;HNSC;LUAD;PAAD;STAD;UCEC	BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED	Act	OVE	0	known	known in: BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED
            if fn == "cna_analysis.tsv":
                #cnas = df.loc[~(df['driver_statement'] == 'known')]
                oncokb_obj = OncoKBAnnotation.objects.all().filter(patient_id=patient_id)
                df_oncokb = pd.DataFrame.from_records(oncokb_obj)
                inoncokb = df_oncokb['hugoSymbol'].unique().to_list()
                cnas = df[~df['gene'].isin(inoncokb)]

                for index, row in cnas.iterrows():
                    try:
                        # TODO: get matches from biomarkers CGIDrugPrescriptions.objects.filter
                        cgi_biomarkers = CGIDrugPrescriptions.objects.all().filter(patient_id=patient_id)
                        relevant = cgi_biomarkers.filter(Q(alterations=handle_string_field(row["gene"])+":"+handle_string_field(row["cna"]).lower()) and Q(tumor_type__contains="OV"))
                        if relevant.count() == 0:
                            relevant = cgi_biomarkers.filter(
                                Q(alterations=handle_string_field(row["gene"]) + ":" + handle_string_field(
                                    row["cna"]).lower()))
                        biomarker = relevant.order_by('evidence')[0]
                        rec, created = CGICopyNumberAlteration.objects.get_or_create(
                            patient_id   = int(patient_id),
                            sample = handle_string_field(cryptocode.decrypt(row["sample"], settings.CRYPTOCODE)),
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
                        # rec, created = OncoKBAnnotation.objects.get_or_create(
                        #     patient_id=int(patient_id),
                        #     sample_id=handle_string_field(cryptocode.decrypt(row["sample"], settings.CRYPTOCODE)),
                        #     hugoSymbol=handle_string_field(row["gene"]),
                        #     # entrezGeneId=handle_string_field(rjson["query"]["entrezGeneId"]),
                        #     alteration=handle_string_field(AlterationTypeLCase[row["cna"]].value),
                        #     # alterationType=handle_string_field(rjson["query"]["alterationType"]),
                        #     # svType=handle_string_field(rjson["query"]["svType"]),
                        #     tumorType=handle_string_field(row["tumor_type"]),
                        #     #consequence=handle_string_field(row["consequence"]),
                        #     #proteinStart=handle_int_field(rjson["query"]["proteinStart"]),
                        #     #proteinEnd=handle_int_field(rjson["query"]["proteinEnd"]),
                        #     #hgvs=handle_string_field(rjson["query"]["hgvs"]),
                        #     #geneExist=handle_boolean_field(rjson["geneExist"]),
                        #     #variantExist=handle_boolean_field(rjson["variantExist"]),
                        #     #alleleExist=handle_boolean_field(rjson["alleleExist"]),
                        #     oncogenic=handle_string_field(row["driver"]),
                        #     #mutationEffectDescription=handle_string_field(rjson["mutationEffect"]["description"]),
                        #     knownEffect=handle_string_field(row["gene_role"]),
                        #     #citationPMids=handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"])),
                        #     #citationAbstracts=handle_string_field(
                        #     #    str(rjson["mutationEffect"]["citations"]["abstracts"])),
                        #     highestSensitiveLevel=handle_cgi_response_field(biomarker),
                        #     highestResistanceLevel=handle_cgi_resistance_field(biomarker),
                        #     #highestDiagnosticImplicationLevel=handle_string_field(rjson["highestDiagnosticImplicationLevel"]),
                        #     #highestPrognosticImplicationLevel=handle_string_field(
                        #     #    rjson["highestPrognosticImplicationLevel"]),
                        #     #highestFdaLevel=handle_string_field(rjson["highestFdaLevel"]),
                        #     #otherSignificantSensitiveLevels=handle_string_field(
                        #     #    rjson["otherSignificantSensitiveLevels"]),
                        #     #otherSignificantResistanceLevels=handle_string_field(
                        #     #    rjson["otherSignificantResistanceLevels"]),
                        #     #hotspot=handle_boolean_field(rjson["hotspot"]),
                        #     geneSummary=handle_string_field(rjson["geneSummary"]),
                        #     variantSummary=handle_string_field(rjson["variantSummary"]),
                        #     tumorTypeSummary=handle_string_field(rjson["tumorTypeSummary"]),
                        #     #prognosticSummary=handle_string_field(rjson["prognosticSummary"]),
                        #     #diagnosticSummary=handle_string_field(rjson["diagnosticSummary"]),
                        #     #diagnosticImplications=handle_string_field(rjson["diagnosticImplications"]),
                        #     #prognosticImplications=handle_string_field(rjson["prognosticImplications"]),
                        #     treatments=handle_treatments_field(rjson["treatments"]),
                        #     #dataVersion=handle_string_field(rjson["dataVersion"]),
                        #     #lastUpdate=handle_date_field(),
                        #     #vus=handle_boolean_field(rjson["vus"])
                        # )
                        rec.save()
                    except Exception as e:
                        logging.exception(e)
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
                            sample = handle_string_field(cryptocode.decrypt(row["sample"], settings.CRYPTOCODE)),
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
                        logging.exception(e)
                        pass

            # Sample ID	Alterations	Biomarker	Drugs	Diseases	Response	Evidence	Match	Source	BioM	Resist.	Tumor type
            # single_sample	ABL1__BCR 	ABL1 (T315I,V299L,G250E,F317L)	Bosutinib (BCR-ABL inhibitor 3rd gen)	Acute lymphoblastic leukemia, Chronic myeloid leukemia	Resistant	A	NO	cgi	only gene		ALL, CML

        return 1
    else:
        print(response.status)
        print("No CGI results available for job id: "+str(jobid))
        return 0


def generate_temp_cgi_query_files(snvs: [SomaticVariant], cnas: [CopyNumberAlteration], translocs: [str]):

    header = "chr\tpos\tref\talt\tsample\n"
    try:
        with open("./tmp/snvs.ext", "w") as file1:
            file1.write(header)
            for snv in snvs:
                row = snv.chromosome+'\t'+str(snv.position)+'\t'+snv.reference_allele+'\t'+snv.sample_allele+'\t'+cryptocode.encrypt(snv.samples, settings.CRYPTOCODE)+'\n'
                file1.write(row)
            file1.close()

        header = "gene\tcna\tsample\n"
        with open("./tmp/cnas.ext", "w") as file2:
            file2.write(header)
            for cna in cnas:
                row = cna.gene+'\t'+cna.CNstatus+'\t'+cryptocode.encrypt(cna.sample_id, settings.CRYPTOCODE)+'\n'
                file2.write(row)
            file2.close()

        header = "fus\tsample\n"
        with open("./tmp/fus.ext", "w") as file3:
            file3.write(header)
            for transloc in translocs:
                row = transloc+'\t'+cryptocode.encrypt(transloc.sample, settings.CRYPTOCODE)+'\n'
                file3.write(row)
            file3.close()
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise
    return 1


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
    login = settings.CGI_LOGIN
    token = settings.CGI_TOKEN

    print("Request CGI")
    # CGI api requires every type mutation files to be provided
    headers = {
        'Authorization': login+' '+token
    }

    if cnas_file:
        payload = {
            'cancer_type': "CANCER",
            'title': 'Title',
            'reference': reference,
            'cnas': ('cnas.ext', open(cnas_file, 'rb').read(), 'application/octet-stream')
        }
    if mutations_file:
        payload = {
            'cancer_type': "CANCER",
            'title': 'Title',
            'reference': reference,
            'mutations': ('snvs.ext', open(mutations_file, 'rb').read(), 'application/octet-stream'),
        }

    # Create a connection pool
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

def query_oncokb_cna(cna: CopyNumberAlteration, tumorType):

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
    # curl -X GET "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?hugoSymbol=HNRNPA1P59&copyNameAlterationType=AMPLIFICATION&referenceGenome=GRCh38&tumorType=HGSOC" -H "accept: application/json" -H "Authorization: Bearer xx-xx-xx"

    hugosymbol = gene_id_convert(cna.gene_id, "HGNC")
    api_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?"

    request_url = api_url + 'copyNameAlterationType='+AlterationType[cna.CNstatus].value+'&hugoSymbol='+hugosymbol+'&tumorType='+tumorType
    header = {"accept":"application/json", 'Content-Type': 'application/json', "Authorization":'Bearer '+token}

    print("Request OncoKB API "+request_url)

    # Sending a GET request and getting back response as HTTPResponse object.
    response = http.request("GET",request_url, headers=header)
    #response = http.request("GET",request_url, headers=header)
    print(response.status)
    print(response.url)
    if (response.status == 200):
        rjson = json.loads(response.data.decode('utf-8'))
        try:
            rec, created = OncoKBAnnotation.objects.get_or_create(
                patient_id  = handle_int_field(cna.patient_id),
                sample_id = handle_string_field(cna.sample_id),
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
                citationPMids = handle_string_field(str(rjson["mutationEffect"]["citations"]["pmids"])),
                citationAbstracts = handle_string_field(str(rjson["mutationEffect"]["citations"]["abstracts"])),
                highestSensitiveLevel = handle_string_field(rjson["highestSensitiveLevel"]),
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
                treatments = handle_treatments_field(rjson["treatments"]),
                dataVersion = handle_string_field(rjson["dataVersion"]),
                lastUpdate = handle_date_field(rjson["lastUpdate"]),
                vus = handle_boolean_field(rjson["vus"])
            )
            rec.save()
        except Exception as e:
            logging.exception(e)
            pass

        return response
    else:
        print("[ERROR] Unable to request. Response: ", print(response.data))
        exit()
def getAlterationType(cna):
    if cna.CNstatus == "AMP" or cna.CNstatus == "DEL":
        return AlterationType[cna.CNstatus]
    else:
        return AlterationType["UNK"]

def query_oncokb_cnas(cna_annotations: [cna_annotation]):

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
    jd = json.loads(data)
    print(json.dumps(jd, indent=4))

    # Sending a POST request and getting back response as HTTPResponse object.
    response = http.request("POST", api_url, body=data, headers={'accept':'application/json','Content-Type':'application/json','Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    #response = httpx.post(api_url, json=data, headers={'Authorization':'Bearer 16d3a20d-c93c-4b2d-84ad-b3657a367fdb'})
    #response = http.request("GET",request_url, headers=header)
    print(response.data)
    #print(response.data.decode('utf-8'))

    if (response.status == 200):

        respjson = json.loads(response.data.decode('utf-8'))
        #print(data)
        print(json.dumps(respjson, indent=4))

        for rjson in respjson:
            hugosymbol = handle_string_field(rjson["query"]["hugoSymbol"])
            alteration = str.upper(handle_string_field(rjson["query"]["alteration"]))
            print(handle_string_field(rjson["query"]["hugoSymbol"]))
            #idsplit = str(cryptocode.decrypt(rjson["query"]["id"], settings.CRYPTOCODE)).split(":")
            #cna_id = idsplit[2]
            objs = cna_annotations.filter(hugoSymbol=hugosymbol).filter(alteration=alteration)
            objs.update(
                #patient_id  = idsplit[0],
                #sample_id = idsplit[1],
                hugoSymbol = handle_string_field(rjson["query"]["hugoSymbol"]),
                entrezGeneId = handle_string_field(rjson["query"]["entrezGeneId"]),
                alteration = str.upper(handle_string_field(rjson["query"]["alteration"])),
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
    else:
        print("Unable to request. Response: ", response.data)
        logging.warning(response.data)

    return response.status


def query_oncokb_cna_direct(geneid, cnatype, tumorType, patient_id, sample_id):

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

    hugosymbol = gene_id_convert(geneid, "HGNC")
    api_url = "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations?"
    request_url = api_url + 'copyNameAlterationType='+cnatype+'&hugoSymbol='+hugosymbol+'&tumorType='+tumorType
    header = {"accept":"application/json", 'Content-Type': 'application/json', "Authorization":'Bearer '+token}

    print("Request OncoKB API "+request_url)
    response = http.request("GET",request_url, headers=header)
    print(response.status)
    #print(response.url)
    if (response.status == 200):
        rjson = json.loads(response.data.decode('utf-8'))

        rec, created = OncoKBAnnotation.objects.get_or_create(
            patient_id  = handle_int_field(patient_id),
            sample_id = handle_string_field(sample_id),
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
            citationPMids = handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"])),
            citationAbstracts = handle_string_field(str(rjson["mutationEffect"]["citations"]["abstracts"])),
            highestSensitiveLevel = handle_string_field(rjson["highestSensitiveLevel"]),
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
            treatments = handle_treatments_field(rjson["treatments"]),
            dataVersion = handle_string_field(rjson["dataVersion"]),
            lastUpdate = handle_date_field(rjson["lastUpdate"]),
            vus = handle_boolean_field(rjson["vus"])
        )
        rec.save()

        return response
    else:
        print("[ERROR] Unable to request. Response: ", print(response.data))
        exit()

def query_oncokb_somatic_mutation(snv: SomaticVariant , tumorType):
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

    altlength = len(snv.sample_allele)
    genomicLocation = snv.chromosome+','+str(snv.position)+','+(str(int(snv.position)+int(altlength)))+','+snv.reference_allele+','+snv.sample_allele
    print(genomicLocation)
    token = settings.ONCOKB_TOKEN
    header = {"accept":"application/json", 'Content-Type': 'application/json', "Authorization":'Bearer '+token}
    request_url = "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange?"

    print("Request OncoKB API "+request_url)
    #response = http.request("GET",request_url+'genomicLocation='+genomicLocation+'&tumorType='+tumorType+'&evidenceType=ONCOGENIC', headers=header)
    response = http.request("GET",
        request_url + 'genomicLocation=' + genomicLocation + '&tumorType=' + tumorType,
        headers=header)

    if (response.status == 200):
        rjson = json.loads(response.data.decode('utf-8'))
        try:
            sids = snv.samples.split(";")
            for sid in sids:
                rec, created = OncoKBAnnotation.objects.get_or_create(
                    patient_id =handle_int_field(snv.patient_id),
                    sample_id=handle_string_field(sid),
                    hugoSymbol=handle_string_field(rjson["query"]["hugoSymbol"]),
                    entrezGeneId=handle_string_field(rjson["query"]["entrezGeneId"]),
                    alteration=handle_string_field(rjson["query"]["alteration"]),
                    alterationType=handle_string_field(rjson["query"]["alterationType"]),
                    svType=handle_string_field(rjson["query"]["svType"]),
                    tumorType=handle_string_field(rjson["query"]["tumorType"]),
                    consequence=handle_string_field(rjson["query"]["consequence"]),
                    proteinStart=handle_int_field(rjson["query"]["proteinStart"]),
                    proteinEnd=handle_int_field(rjson["query"]["proteinEnd"]),
                    hgvs=handle_string_field(rjson["query"]["hgvs"]),
                    geneExist=handle_boolean_field(rjson["geneExist"]),
                    variantExist=handle_boolean_field(rjson["variantExist"]),
                    alleleExist=handle_boolean_field(rjson["alleleExist"]),
                    oncogenic=handle_string_field(rjson["oncogenic"]),
                    mutationEffectDescription=handle_string_field(rjson["mutationEffect"]["description"]),
                    knownEffect=handle_string_field(rjson["mutationEffect"]["knownEffect"]),
                    citationPMids=handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"])),
                    citationAbstracts=handle_string_field(str(rjson["mutationEffect"]["citations"]["abstracts"])),
                    highestSensitiveLevel=handle_string_field(rjson["highestSensitiveLevel"]),
                    highestResistanceLevel=handle_string_field(rjson["highestResistanceLevel"]),
                    highestDiagnosticImplicationLevel=handle_string_field(rjson["highestDiagnosticImplicationLevel"]),
                    highestPrognosticImplicationLevel=handle_string_field(rjson["highestPrognosticImplicationLevel"]),
                    highestFdaLevel=handle_string_field(rjson["highestFdaLevel"]),
                    otherSignificantSensitiveLevels=handle_string_field(rjson["otherSignificantSensitiveLevels"]),
                    otherSignificantResistanceLevels=handle_string_field(rjson["otherSignificantResistanceLevels"]),
                    hotspot=handle_boolean_field(rjson["hotspot"]),
                    geneSummary=handle_string_field(rjson["geneSummary"]),
                    variantSummary=handle_string_field(rjson["variantSummary"]),
                    tumorTypeSummary=handle_string_field(rjson["tumorTypeSummary"]),
                    prognosticSummary=handle_string_field(rjson["prognosticSummary"]),
                    diagnosticSummary=handle_string_field(rjson["diagnosticSummary"]),
                    diagnosticImplications=handle_string_field(rjson["diagnosticImplications"]),
                    prognosticImplications=handle_string_field(rjson["prognosticImplications"]),
                    treatments=handle_treatments_field(rjson["treatments"]),
                    dataVersion=handle_string_field(rjson["dataVersion"]),
                    lastUpdate=handle_date_field(rjson["lastUpdate"]),
                    vus=handle_boolean_field(rjson["vus"])
                )
                rec.save()
        except Exception as e:
            logging.exception(e)
            pass

        return response
    else:
        print("[ERROR] Unable to request. Response: ", print(response.data))
        exit()

def query_oncokb_somatic_mutations(snvs: [snv_annotation] , tumorType):
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

    # data = [
    #     {
    #         "id": f"{cryptocode.encrypt(str(snvs[i].patient_id) + ':' + snvs[i].samples + ':' + str(i), settings.CRYPTOCODE)}",
    #         "hgvsg": f"{snvs[i].chromosome + ':g.' + str(snvs[i].position) + snvs[i].reference_allele + '>' + snvs[i].sample_allele}",
    #         "tumorType": f"{tumorType}",
    #         "referenceGenome": "GRCh38"
    #     }
    #     for i in range(len(snvs))
    # ]

    data = [
        {
            "id": f"{cryptocode.encrypt(str(snvs[i].patient_id) + ':' + snvs[i].samples+':'+str(snvs[i].id), settings.CRYPTOCODE)}",
            "genomicLocation": f"{snvs[i].chromosome+','+str(snvs[i].position)+','+(str(int(snvs[i].position)+len(snvs[i].sample_allele)))+','+snvs[i].reference_allele+','+snvs[i].sample_allele}",
            "tumorType": f"{snvs[i].tumorType}",
            "referenceGenome": "GRCh38"
        }
        for i in range(len(snvs))
    ]

    print(json.dumps(data, indent=4))

    # Sending a GET request and getting back response as HTTPResponse object.
    print("Request OncoKB API "+request_url)
    response = http.request("POST", request_url, body=data, headers=header)

    # response = http.request("GET",request_url, headers=header)
    print(response.status)

    #TODO: check why EGFR chr7,55181426,55181427,A,C  is not found but is found from web api (and also from CGI)
    if (response.status == 200):

        respjson = json.loads(response.data.decode('utf-8'))
        print(json.dumps(respjson, indent=4))
        for rjson in respjson:

            if handle_string_field(rjson["query"]["hugoSymbol"]) is not None and len(rjson["query"]["alteration"]) > 0 and handle_string_field(rjson["query"]["consequence"]) is not "synonymous_variant":
                #print("OBJ", rjson)
                idsplit = str(cryptocode.decrypt(rjson["query"]["id"], settings.CRYPTOCODE)).split(":")
                sids = idsplit[1].split(";")
                pid = idsplit[0]
                for sid in sids:
                    snv_id = idsplit[2]
                    snv = snv_annotation.objects.all().filter(id=int(snv_id)).first()
                    print(handle_string_field(rjson["query"]["hugoSymbol"]))
                    try:
                        rec, created = snv_annotation.objects.update_or_create(
                        patient_id=pid,
                        sample_id=sid,
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
                        citationPMids=handle_string_field(",".join(rjson["mutationEffect"]["citations"]["pmids"])),
                        citationAbstracts=handle_string_field(str(rjson["mutationEffect"]["citations"]["abstracts"])),
                        highestSensitiveLevel = handle_string_field(rjson["highestSensitiveLevel"]),
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
                        treatments = handle_treatments_field(rjson["treatments"]),
                        dataVersion = handle_string_field(rjson["dataVersion"]),
                        lastUpdate = handle_date_field(rjson["lastUpdate"]),
                        vus = handle_boolean_field(rjson["vus"]),
                        #nMinor=models.IntegerField(null=True)
                        #nMajor = models.IntegerField(null=True)
                        #ad0 = handle_readcount_field0(snv.readCounts, sids, sid),
                        #ad1 = handle_readcount_field1(snv.readCounts, sids, sid),
                        #af = models.IntegerField(null=True)
                        #dp = models.IntegerField(null=True)
                        #lohstatus = models.CharField(max_length=16, default=None, blank=True, null=True)
                        #exphomci = models.BooleanField(default=False, blank=False, null=True)
                        #copynumber = handle_copynumber_field(cna.nMinor, cna.nMajor)
                        )
                        rec.save()
                    except Exception as e:
                        print(e)
                        pass

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
    response = http.request("POST", url=request_url, body=body, headers=headers)
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

def generate_proteinchange_query_file(snvs: [SomaticVariant]):

    header = "protein\n"
    with open("./tmp/prot.ext", "w") as file1:
        file1.write(header)
        for snv in snvs:
            isoforms = parse_isoforms(snv.aaChangeRefGene)
            for isoform in isoforms:
                file1.write(isoform+"\n")
        file1.close()

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

def sql_query_db():

    # Examples for checking duplicates
    """SELECT * FROM genomics_oncokbannotation
        WHERE id NOT IN
        (SELECT MIN(id)
        FROM genomics_oncokbannotation
        GROUP BY patient_id, hugoSymbol, alteration)

        SELECT * FROM genomics_cgicopynumberalteration
        WHERE id NOT IN
        (SELECT MIN(id)
        FROM genomics_cgicopynumberalteration
        GROUP BY patient_id, gene, cnatype)

        SELECT * FROM genomics_cgimutation
        WHERE id NOT IN
        (SELECT MIN(id)
        FROM genomics_cgimutation
        GROUP BY patient_id, mutation)

        SELECT * FROM genomics_copynumberalteration
        WHERE id NOT IN
        (SELECT MIN(id)
        FROM genomics_copynumberalteration
        GROUP BY sample_id, gene_id)

        SELECT * FROM genomics_somaticvariant
        WHERE id NOT IN
        (SELECT MIN(id)
        FROM genomics_somaticvariant
        GROUP BY patient_id, chromosome, position)"""

    try:
        for rec in SomaticVariant.objects.raw("SELECT * FROM genomics_somaticvariant"):
            print(rec.ref_id, rec.sample_allele)

    except Exception as e:
        logging.exception(e)





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


    def handle(self, *args, **kwargs):
        if kwargs["sqlsnvs"]:
            sql_query_db()

    # OncoKB queries
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbcna --geneid=ENSG00000230280 --patientid=1"
        if kwargs["oncokbcna"] and kwargs["geneid"] and not kwargs["direct"]:
            cna = get_cna(kwargs["patientid"], kwargs["geneid"])
            resp = query_oncokb_cna(cna, kwargs["cancer"])
            print(json.dumps(resp.json(), indent=4))
        if kwargs["oncokbcna"] and kwargs["gene"] and not kwargs["direct"] and not kwargs["cnatype"]:
            cna = get_cna_by_gene(kwargs["patientid"], kwargs["gene"])
            resp = query_oncokb_cna(cna, kwargs["cancer"])
            print(json.dumps(resp.json(), indent=4))
        if kwargs["oncokbcna"] and kwargs["direct"]:
            resp = query_oncokb_cna_direct(kwargs["geneid"], kwargs["cnatype"],kwargs["cancer"], kwargs["patientid"], kwargs["cohortcode"])
            print(json.dumps(resp.json(), indent=4))
        if kwargs["oncokbcna"] and kwargs["all"] and kwargs["patientid"]:
            cnas = get_cnas(kwargs["patientid"])
            query_oncokb_cnas(cnas, kwargs["cancer"])
        if kwargs["oncokbcna"] and kwargs["all"] and kwargs["cnatype"]:
            for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
                cnas = get_cnas_by_type(pid['patient_id'], kwargs["cnatype"])
                query_oncokb_cnas(cnas, kwargs["cancer"])
                time.sleep(1)
        if kwargs["oncokbcna"] and kwargs["cnatype"] and kwargs["patientid"] and not kwargs["gene"]:
            cnas = get_cnas_by_type(kwargs["patientid"], kwargs["cnatype"])
            query_oncokb_cnas(cnas, kwargs["cancer"])
        if kwargs["oncokbcna"] and kwargs["cnatype"] and kwargs["gene"] and kwargs["patientid"]:
            cnas = get_cnas_by_type_and_gene(kwargs["patientid"], kwargs["cnatype"], kwargs["gene"])
            query_oncokb_cnas(cnas, kwargs["cancer"])

        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbsnv=rs61769312 --patientid=1"
        if kwargs["oncokbsnv"] and kwargs["refid"]:
            snv = get_snv(kwargs["patientid"], kwargs["refid"])
            resp = query_oncokb_somatic_mutation(snv, kwargs["cancer"])
            print(json.dumps(resp.json(), indent=4))
        if kwargs["oncokbsnv"] and kwargs["proteinchange"] and kwargs["cohortcode"]: # Query all exonic mutations for given patient
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snvs = get_actionable_snvs_by_aaChangeRefGene(pid)
            query_oncokb_somatic_mutations(snvs, kwargs["cancer"])
        if kwargs["oncokbsnv"] and kwargs["exonic"] and kwargs["cohortcode"]: # Query all exonic mutations for given patient
            targets = ActionableTarget.objects.all()
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snvs = get_all_exonic_snvs_of_patient(pid, targets)
            query_oncokb_somatic_mutations(snvs, kwargs["cancer"])
            #chunks = [snvs[x:x+10] for x in range(0, len(snvs), 10)]
            #for c in chunks:
            #    query_oncokb_somatic_mutations(c, kwargs["cancer"])
            #    time.sleep(1)
        if kwargs["oncokbcna"] and kwargs["targetall"] and kwargs["cohortcode"]:
            targets = ActionableTarget.objects.all()
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            cnas = get_cnas_by_gene_list(pid, targets)
            query_oncokb_cnas(cnas, kwargs["cancer"])

        if kwargs["oncokbcna"] and kwargs["actionable"] and kwargs["cohortcode"]:
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            targets = ActionableTarget.objects.all()
            cnas = get_cnas_by_cn_and_ploidy(pid, kwargs["cnthr"], targets)
            query_oncokb_cnas(cnas, kwargs["cancer"])

        if kwargs["oncokbsnv"] and kwargs["actionable"] and kwargs["cohortcode"] and not kwargs["single"]:
            targets = ActionableTarget.objects.all()
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snvs = get_snvs_by_gene_list(pid, targets)
            #chunks = [snvs[x:x + 30] for x in range(0, len(snvs), 30)]
            #for c in chunks:
            query_oncokb_somatic_mutations(snvs, kwargs["cancer"])

        if kwargs["oncokbsnv"] and kwargs["actionable"] and kwargs["cohortcode"] and kwargs["single"]:
            targets = ActionableTarget.objects.all()
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snvs = get_snvs_by_gene_list(pid, targets)
            for snv in snvs:
                query_oncokb_somatic_mutation(snv, kwargs["cancer"])
                #time.sleep(1)

        if kwargs["oncokbcna"] and kwargs["targetall"] and kwargs["all"]:
            targets = ActionableTarget.objects.all()
            for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
                cnas = get_cnas_by_gene_list(pid['patient_id'], targets)
                if cnas:
                    query_oncokb_cnas(cnas)
                    time.sleep(1)

        if kwargs["oncokbcna"] and kwargs["actionable"] and kwargs["all"]:
            #for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
            #    cnas = cna_annotation.objects.filter(patient_id=pid.get('patient_id'))
            #   if cnas:
            query_oncokb_cnas(cna_annotation.objects.all())

        if kwargs["oncokbsnv"] and kwargs["actionable"] and kwargs["all"]:
            targets = ActionableTarget.objects.all()
            for pid in ClinicalData.objects.order_by().values('patient_id').distinct():
                snvs = get_snvs_by_gene_list(pid['patient_id'], targets)
                query_oncokb_somatic_mutations(snvs, kwargs["cancer"])
                time.sleep(1)

    # CGI queries
        if kwargs["cgijobid"]:
            cgijobid=kwargs["cgijobid"]
            query_cgi_job(kwargs["patientid"], cgijobid)

        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --snv --refid=rs907584225 --patientid=1"
        if kwargs["cgiquery"] and kwargs["snv"] and kwargs["refid"]:
            snv = get_snv(kwargs["patientid"], kwargs["refid"])
            generate_temp_cgi_query_files(snv,[],[])
            jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext", None, None, kwargs["cancer"], "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(30)
        if kwargs["cgiquery"] and kwargs["cna"] and kwargs["all"]:
            cnas = get_cnas(kwargs["patientid"])
            generate_temp_cgi_query_files([],cnas,[])
            jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(30)
        if kwargs["cgiquery"] and kwargs["direct"] and kwargs["genelist"]:
            generate_cgi_cna_file_from_list(kwargs["genelist"].split(','))
            jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(30)

        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --cna --geneid=PTPN14 --patientid=1"
        if kwargs["cgiquery"] and kwargs["cna"] and kwargs["geneid"]:
            ensg = gene_id_convert(kwargs["geneid"], "ENSG")
            cna = get_cna(kwargs["patientid"], ensg)
            generate_temp_cgi_query_files([],[cna],[])
            jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(30)
        #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --exonic --patientid=1"
        if kwargs["cgiquery"] and kwargs["exonic"] and kwargs["snv"] and kwargs["cohortcode"]: # Query all exonic mutations for given patient
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snv = get_all_exonic_snvs_of_patient(pid)
            generate_temp_cgi_query_files(snv,[],[])
            jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext", None, None, kwargs["cancer"], "hg38")
            if jobid != 0:
                while query_cgi_job(pid, jobid.replace('"', '')) == 0:
                    print("Waiting 120 seconds for the next try...")
                    time.sleep(30)
         #USAGE: docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --proteinchange --patientid=1"
        if kwargs["cgiquery"] and kwargs["proteinchange"] and kwargs["snv"] and kwargs["cohortcode"]: # Query all protein affecting mutations for all patients
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snvs = get_actionable_snvs_by_aaChangeRefGene(kwargs["patientid"])
            generate_proteinchange_query_file(snvs)
            jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/prot.ext", None, None, kwargs["cancer"], "hg38")
            while query_cgi_job(pid, jobid.replace('"', '')) == 0:
                print("Waiting 120 seconds for the next try...")
                time.sleep(120)
        if kwargs["cgiquery"] and kwargs["fusgenes"] and kwargs["patientid"]: # Query list of fusion genes for given patient
            fusgenes=kwargs["fusgenes"].split(',')
            generate_temp_cgi_query_files([],[],fusgenes)
            jobid = launch_cgi_job_with_mulitple_variant_types(None, None, "./tmp/fus.ext", kwargs["cancer"], "hg38")
            time.sleep(10)
            while query_cgi_job(kwargs["patientid"], jobid.replace('"', '')) == 0:
                print("Waiting 30 seconds for the next try...")
                time.sleep(30)

        # May be impossible to query every patient at once from cgi, could be done if distinct genes of every patient mapped to same query file
        if kwargs["cgiquery"] and kwargs["cna"] and kwargs["targetall"] and kwargs["cohortcode"]:
            targets = ActionableTarget.objects.all()
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            cnas = get_cnas_by_gene_list(pid, targets)
            if cnas:
                generate_temp_cgi_query_files([], cnas, [])
                jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
                time.sleep(10)
                while query_cgi_job(pid, jobid.replace('"', '')) == 0:
                    print("Waiting 30 seconds for the next try...")
                    time.sleep(30)

        if kwargs["cgiquery"] and kwargs["cna"] and kwargs["actionable"] and kwargs["cohortcode"]:
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            targets = ActionableTarget.objects.all()
            cnas = get_cnas_by_cn_and_ploidy(pid, kwargs["cnthr"], targets)
            if cnas:
                genfiles = generate_temp_cgi_query_files([], cnas, [])
                if genfiles:
                    jobid = launch_cgi_job_with_mulitple_variant_types(None, "./tmp/cnas.ext", None, kwargs["cancer"], "hg38")
                    time.sleep(10)
                    if jobid != 0:
                        while query_cgi_job(pid, jobid.replace('"', '')) == 0:
                            print("Waiting 30 seconds for the next try...")
                            time.sleep(30)
                else:
                    print("No cgi variant files generated!")
            else:
                print("No CNAs!")
        if kwargs["cgiquery"] and kwargs["snv"] and kwargs["actionable"] and kwargs["cohortcode"]:
            targets = ActionableTarget.objects.all()
            pid = map_cohort_code_to_patient_id(kwargs["cohortcode"])
            snvs = get_snvs_by_gene_list(pid, targets)
            if snvs:
                generate_temp_cgi_query_files(snvs, [], [])
                jobid = launch_cgi_job_with_mulitple_variant_types("./tmp/snvs.ext", None, None, kwargs["cancer"], "hg38")
                time.sleep(10)
                while query_cgi_job(pid, jobid.replace('"', '')) == 0:
                        print("Waiting 30 seconds for the next try...")
                        time.sleep(30)
