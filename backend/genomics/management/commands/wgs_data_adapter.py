import argparse
import logging
import os

import pandas as pd
import psutil
from pandarallel import pandarallel
from typing import Callable, Optional, Tuple

from enum import Enum
from scipy import stats

def handle_boolean_field(value, field=None, default=False):
    if str(value).lower() in ["yes", "t", "true"]:
        return True
    elif str(value).lower() in ["no", "f", "false"]:
        return False
    else:
        return None if pd.isna(value) else value


def handle_float_field(value):
    return None if pd.isna(value) else float(value.replace(",", "."))


def handle_cn_type_field(value):
    if str(value).lower() in ["amp", "amplification"]:
        return "AMPLIFICATION"
    elif str(value).lower() in ["del", "deletion"]:
        return "DELETION"
    else:
        return None if pd.isna(value) else "UNKNOWN"


def handle_string_field(value):
    return None if pd.isna(value) else value


def handle_cn_field(value):
    return None if pd.isna(value) else value


def handle_int_field(value):
    return None if pd.isna(value) else value


def handle_date_field(value):
    return None if pd.isna(value) else value


def handle_decimal_field(value):
    return None if pd.isna(value) or str(value) == "." else value

def df_apply(
    df: pd.DataFrame,
    func: Callable,
    col: Optional[str] = None,
    extra_col: Optional[str] = None,
    parallel: bool = True,
    pbar: bool = False,
    cores: Optional[int] = 0,
    **kwargs,
) -> pd.Series:
    """Apply or parallel apply a function to any col of a DataFrame.

    Parameters
    ----------
        df : pd.DataFrame
            Input DataFrame.
        func : Callable
            A callable function.
        col : str, optional,
            The name of the column of the df that is used as the input
            to apply operation.
        extra_col : str, optional
            An extra column that can be used in the apply operation.
        parallel : bool, default=False
            Flag, whether to parallelize the operation with pandarallel
        pbar : bool, default=False
            Show progress bar when executing in parallel mode. Ignored if
            `parallel=False`
        **kwargs:
            Arbitrary keyword args for the `func` callable.

    Returns
    -------
        Output of applied function
    """


    if not parallel:
        if col is None:
            res = df.apply(func, **kwargs)
        else:
            if extra_col is None:
                res = df[col].apply(func, **kwargs)
            else:
                res = df[[col, extra_col]].apply(lambda x: func(*x, **kwargs), axis=1)
    else:
        pandarallel.initialize(nb_workers=cores, verbose=1, progress_bar=pbar)
        if col is None:
            res = df.parallel_apply(func, **kwargs, axis=1)
        else:
            if extra_col is None:
                res = df[col].parallel_apply(func, **kwargs)
            else:
                res = df[[col, extra_col]].parallel_apply(
                    lambda x: func(*x, **kwargs), axis=1
                )

    return res

class AlterationType(Enum):
    AMP = "AMPLIFICATION"
    DEL = "DELETION"
    GAIN = "GAIN"
    LOSS = "LOSS"
    TRANS = "TRANSLOCATION"
    DUP = "DUPLICATION"
    INS = "INSERTION"
    FUS = "FUSION"
    UNK = "UNKNOWN"
    Normal = "UNKNOWN"
    nan = "UNKNOWN"
    def __str__(self):
        return str(self.value)

class AlterationTypeLCase(Enum):
    AMP = "Amplification"
    DEL = "Deletion"
    UNK = "Unknown"
    def __str__(self):
        return str(self.value)

class CGI2OncoKBLevels(Enum):
    A = "LEVEL_1"
    B = "LEVEL_2"
    C = "LEVEL_3A"
    D = "LEVEL_3B"
    E = "LEVEL_4"
    R1 = "LEVEL_R1"
    R2 = "LEVEL_R2"
    def __str__(self):
        return str(self.value)



#
# def map_sample_to_patient_id(sample_name):
#
#     c_code = sample_name.split("_")[0]
#     try:
#         for rec in ClinicalData.objects.filter(cohort_code=c_code):
#             return int(getattr(rec,'patient_id'))
#
#     except Exception as e:
#         print("No patient with cohort code", c_code, "available in the database")
#
#
# def map_cohort_code_to_patient_id(cohort_code):
#     try:
#         for rec in ClinicalData.objects.filter(cohort_code=cohort_code):
#             return int(getattr(rec,'patient_id'))
#
#     except Exception as e:
#         logging.exception(e)
#         print("No patient with cohort code", cohort_code, "available in the database")
#

def get_variant_assoc_cnas(cnas, sid, gene):
    cnar = cnas.loc[(cnas['sample'] == sid) & (cnas['Gene'] == gene)]
    return cnar.iloc[0] if not cnar.empty else []

def expectedAF(N_t, CN_t, TF):
    return (N_t * TF) / (CN_t * TF + 2 * (1 - TF))


def parse_isoforms(aaChangeRefGene):
    records = aaChangeRefGene.split(",")
    isoforms = []
    for rec in records:
        fields = rec.split(":")
        if len(fields) > 1:
            gene = fields[0]
            protein = fields[len(fields)-1].split(".")[1]
            isoform = gene+":"+protein
            isoforms.append(isoform)

            # else aaChangeRefGene can have UNKNOWN status, what to do with it?
    return list(dict.fromkeys(isoforms))

def filter_cnas_by_ploidy(row, ascats=None):
    #print(ascats)
    #print(row)
    ploidy_coeff = 2.5
    ploidy = ascats.loc[ascats['sample'] == row['sample']]['ploidy']
    nminor = handle_int_field(row['nMinor'])
    nmajor = handle_int_field(row['nMajor'])
    if nminor and nmajor:
        cn = int(nminor) + int(nmajor)
        ploidy = ploidy.iloc[0]
        if ploidy > 0 and float(ploidy) > 0:
            if cn < 1 or cn > ploidy_coeff * float(ploidy):
                return pd.Series({
                    'patient_id': row["sample"].split("_")[0],    # Use cohort code here, map to pid later to reduce queries sample name includes cohort code which is mapped to patient id
                    'sample_id':handle_string_field(row["sample"]),
                    'referenceGenome' : "GRCh38",
                    'hugoSymbol':handle_string_field(row["Gene"]),
                    'alteration':handle_cn_type_field(row["CNstatus"]),
                    'tumorType':handle_string_field("HGSOC"),
                    'nMajor':handle_int_field(row["nMajor"]),
                    'nMinor':handle_int_field(row["nMinor"]),
                    'lohstatus':handle_string_field(row["LOHstatus"]),
                    'ploidy':handle_decimal_field(float(ploidy))
                })
    return None

def filter_and_classify_snvs(row, cnas=None, alphamissenses=None, ascats=None):
    pid = row['patient']
    sv_class = None

    snv_annotations = []

    amisscore = None
    amis_category = None
    sift_category = None
    sift_score = None  # Will be dded to WGS output in near future https://sift.bii.a-star.edu.sg/
    polyphen_category = None
    polyphen_score = None   # Will be dded to WGS output in near future http://genetics.bwh.harvard.edu/pph2/
    pathogenecity = handle_string_field(row["CLNSIG"]) # Currently Clinvar annotation is included in WGS pipeline output
    # TODO: Change pathogenecity annotation to voting after all scorings are included in output
    # if len(str(row['AAChange.refGene'])) > 2:
    #     isoforms = parse_isoforms(str(row['AAChange.refGene']))
    #     for isof in isoforms:
    #         ps = isof.split(':')
    #         protein = ps[1]
    #         amis = alphamissenses.loc[alphamissenses['protein_variant'] == protein]
    #         amisscore = amis.iloc[0]['am_pathogenicity'] if len(amis) > 0 else 0.0
    #         # TODO: vote pathogenecity by multiple estimates from sift,polyphen,oncokb,cgi
    #         amis_category = amis.iloc[0]['am_class'] if len(amis) > 0 else None
    #         pathogenecity = amis_category
    amisscore = row['AM_score']
    amis_category = row['AM_class']
    pathogenecity = amis_category

    samples = handle_string_field(row["samples"]).split(';') if handle_string_field(
        row["samples"]) else []
    readcounts = handle_string_field(row["readCounts"]).split(';') if handle_string_field(
        row["readCounts"]) else []
    i = 0

    exonicFuncMane = handle_string_field(row["ExonicFunc.MANE"])
    funcMane = handle_string_field(row["Func.MANE"])
    funcRefgene = handle_string_field(row["Func.refGene"])
    ada_score = handle_decimal_field(row["dbscSNV_ADA_SCORE"])
    rf_score = handle_decimal_field(row["dbscSNV_RF_SCORE"])
    for sample_id in samples:

        # Splicing mutations
        #  funcMane | funRefgene = splicing / splicesite / intronic = > dbscSNV_ADA / RF_SCORE > 0.95
        # funcMane = handle_string_field(row["Func.MANE"])
        # funcRefgene = handle_string_field(row["Func.refGene"])

        # Truncating and Missenses => test homogeneity
        # truncating

        # if exonicFuncMane == ("frameshift_insertion" or "frameshift_deletion" or "stopgain" or "nonsynonymous_SNV"):
        # Calculate homogeneity estimate
        tfs = ascats.loc[ascats['sample']==sample_id]['purity']
        tf = tfs.iloc[0] if len(tfs) > 0 else 0.0 # loc[ascats['sample'] == sample_id]['purity'].values[0]
        readcount = readcounts[i].split(',')
        ad0 = int(readcount[0])
        ad1 = int(readcount[1])
        depth = ad0 + ad1
        geneMANE = handle_string_field(row["Gene.MANE"]).split(';')
        genes = set(geneMANE)
        geneRefGene = handle_string_field(row["Gene.refGene"]).split(';')
        for g in geneRefGene:
            genes.add(g)
        for gene in genes:
            nMajor = None
            nMinor = None
            lohstatus = None
            vcnas = get_variant_assoc_cnas(cnas, sample_id, gene)
            nMajor = handle_cn_field(vcnas['nMajor']) if len(vcnas) > 0 else None
            nMinor = handle_cn_field(vcnas['nMinor']) if len(vcnas) > 0 else None
            lohstatus = vcnas['LOHstatus'] if len(vcnas) > 0 else None

            expHomAF = 0.0
            expHomCI_lo = 0.0
            expHomCI_hi = 0.0
            expHom_pbinom_lower = 0.0
            homogenous = None

            if nMajor and nMinor:
                cn = int(nMinor) + int(nMajor)
                expHomAF = float(expectedAF(cn, cn, tf))
                expHomCI_lo = float(stats.binom.ppf(0.025, depth, expHomAF))
                expHomCI_hi = float(stats.binom.ppf(0.975, depth, expHomAF))
                expHomCI_cover = expHomCI_lo <= ad1
                expHom_pbinom_lower = float(stats.binom.cdf(ad1, depth, expHomAF))
                homogenous = expHom_pbinom_lower > 0.05
            # TODO: Check FGFR2 in H266, why not estimated as homogenous
            if homogenous and exonicFuncMane == "nonsynonymous_SNV":
                sv_class = "Missense"
            if exonicFuncMane in ["frameshift_insertion", "frameshift_deletion", "stopgain"]:
                sv_class = "Truncating"
            if exonicFuncMane == ["nonframeshift_deletion", "nonframeshift_substitution", "nonframeshift_insertion"]:
                sv_class = "Other"
            if not sv_class:
                if funcMane in ["splicing", "splicesite", "intron", "intronic"] or funcRefgene in ["splicing", "splicesite", "intron", "intronic"]:
                    if (ada_score and float(ada_score) > 0.95) or (rf_score and float(rf_score) > 0.95):
                        sv_class = "Splicing"
                    else:
                        continue

            alteration = gene + ":" + handle_string_field(row["CHROM"]) + ":" + str(handle_int_field(row["POS"])) + ":" + handle_string_field(row["REF"]) + ">" + handle_string_field(row["ALT"])

            snv_annotations.append(pd.Series({
                    'patient_id':pid,
                    'sample_id':sample_id,
                    'ref_id':handle_string_field(row["ID"]),
                    'chromosome':handle_string_field(row["CHROM"]),
                    'position':handle_int_field(row["POS"]),
                    'reference_allele':handle_string_field(row["REF"]),
                    'sample_allele':handle_string_field(row["ALT"]),
                    'referenceGenome':"GRCh38",
                    'hugoSymbol':gene,
                    'alteration':alteration,
                    # ensemblGeneId ': "",
                    # alteration: string;
                    'tumorType':"HGSOC",
                    'consequence':exonicFuncMane,
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
                    'nMinor':nMinor,
                    'nMajor':nMajor,
                    # oncokb_level: string;
                    # cgi_level: string;
                    # rank: number;
                    'ad0':ad0,
                    'ad1':ad1,
                    'af':expHomAF,
                    'depth':depth,
                    'lohstatus':lohstatus,
                    'hom_lo':"{:.9f}".format(expHomCI_lo),
                    'hom_hi':"{:.9f}".format(expHomCI_hi),
                    'hom_pbinom_lo':"{:.9f}".format(expHom_pbinom_lower),
                    'homogenous':homogenous,
                    # 'funcMane':handle_string_field(row["Func.MANE"]),
                    # 'funcRefgene':handle_string_field(row["Func.refGene"]),
                    # 'exonicFuncMane':handle_string_field(row["ExonicFunc.MANE"]),
                    'cadd_score':handle_decimal_field(row["CADD_phred"]),
                    'ada_score':ada_score,
                    'rf_score':rf_score,
                    'sift_category': sift_category,
                    'sift_score': sift_score,  # Will be dded to WGS output in near future https://sift.bii.a-star.edu.sg/
                    'polyphen_category': polyphen_category,
                    'polyphen_score': polyphen_score,  # Will be dded to WGS output in near future http://genetics.bwh.harvard.edu/pph2/
                    'amis_category': amis_category,
                    'amis_score':handle_decimal_field(amisscore),
                    'cosmic_id':handle_string_field(row["COSMIC_ID"]),
                    'clinvar_id':handle_string_field(row["CLNALLELEID"]),
                    'clinvar_sig':handle_string_field(row["CLNSIG"]),
                    'clinvar_status':handle_string_field(row["CLNREVSTAT"]),
                    'clinvar_assoc':handle_string_field(row["CLNDN"]),
                    'pathogenecity':handle_string_field(pathogenecity),
                    'classification':sv_class,
                }))
        i += 1
    if len(snv_annotations) > 0:
        return snv_annotations

def post_filter_and_classify_snvs(row, cnas=None, ascats=None):
    try:
        exonicFuncMane = handle_string_field(row["exonicFuncMane"])
        sample_id =row['sample_id']

        # Calculate homogeneity estimate
        tfs = ascats.loc[ascats['sample'] == sample_id]['purity']
        tf = tfs.iloc[0] if len(tfs) > 0 else 0.0  # loc[ascats['sample'] == sample_id]['purity'].values[0]
        ad0 = int(row['ad0'])
        ad1 = int(row['ad1'])
        depth = ad0 + ad1
        gene= handle_string_field(row["hugoSymbol"])

        nMajor = None
        nMinor = None
        lohstatus = None
        vcnas = get_variant_assoc_cnas(cnas, sample_id, gene)
        nMajor = handle_cn_field(vcnas['nMajor']) if len(vcnas) > 0 else None
        nMinor = handle_cn_field(vcnas['nMinor']) if len(vcnas) > 0 else None
        lohstatus = vcnas['LOHstatus'] if len(vcnas) > 0 else None
        expHomAF = 0.0
        expHomCI_lo = 0.0
        expHomCI_hi = 0.0
        expHom_pbinom_lower = 0.0
        homogenous = None

        if nMajor and nMinor:
            cn = int(nMinor) + int(nMajor)
            expHomAF = float(expectedAF(cn, cn, tf))
            expHomCI_lo = float(stats.binom.ppf(0.025, depth, expHomAF))
            expHomCI_hi = float(stats.binom.ppf(0.975, depth, expHomAF))
            expHomCI_cover = expHomCI_lo <= ad1
            expHom_pbinom_lower = float(stats.binom.cdf(ad1, depth, expHomAF))
            homogenous = expHom_pbinom_lower > 0.05

        row['nMinor'] = nMinor
        row['nMajor'] = nMajor
        row['lohstatus'] = lohstatus
        row['hom_lo'] = "{:.9f}".format(expHomCI_lo),
        row['hom_hi'] = "{:.9f}".format(expHomCI_hi),
        row['hom_pbinom_lo'] = "{:.9f}".format(expHom_pbinom_lower),
        row['homogenous'] = homogenous
        row['af'] = expHomAF
        if homogenous and exonicFuncMane == "nonsynonymous_SNV":
            row['classification'] = "Missense"
        row['hom_lo'] = row['hom_lo'][0] if isinstance(row['hom_lo'], tuple) else row['hom_lo']
        row['hom_hi'] = row['hom_hi'][0] if isinstance(row['hom_hi'], tuple) else row['hom_hi']
        row['hom_pbinom_lo'] = row['hom_pbinom_lo'][0] if isinstance(row['hom_pbinom_lo'], tuple) else row['hom_pbinom_lo']

    except Exception as e:
        print(e)
        pass

    return row

def post_filter_and_classify_snvs_by_sample(row, cnas=None, ascats=None):

    try:

        exonicFuncMane = handle_string_field(row["exonicFuncMane"])
        sample_id =row['sample_id']

        # Calculate homogeneity estimate
        tfs = ascats.loc[ascats['sample'] == sample_id]['purity']
        tf = tfs.iloc[0] if len(tfs) > 0 else 0.0  # loc[ascats['sample'] == sample_id]['purity'].values[0]
        ad0 = int(row['ad0'])
        ad1 = int(row['ad1'])
        depth = ad0 + ad1
        gene= handle_string_field(row["hugoSymbol"])

        nMajor = None
        nMinor = None
        lohstatus = None
        pathogenecity = handle_string_field(row["clinvar_sig"])
        vcnas = get_variant_assoc_cnas(cnas, sample_id, gene)
        nMajor = handle_cn_field(vcnas['nMajor']) if len(vcnas) > 0 else None
        nMinor = handle_cn_field(vcnas['nMinor']) if len(vcnas) > 0 else None
        lohstatus = vcnas['LOHstatus'] if len(vcnas) > 0 else None
        expHomAF = 0.0
        expHomCI_lo = 0.0
        expHomCI_hi = 0.0
        expHom_pbinom_lower = 0.0
        homogenous = None

        if nMajor and nMinor:
            cn = int(nMinor) + int(nMajor)
            expHomAF = float(expectedAF(cn, cn, tf))
            expHomCI_lo = float(stats.binom.ppf(0.025, depth, expHomAF))
            expHomCI_hi = float(stats.binom.ppf(0.975, depth, expHomAF))
            expHomCI_cover = expHomCI_lo <= ad1
            expHom_pbinom_lower = float(stats.binom.cdf(ad1, depth, expHomAF))
            homogenous = expHom_pbinom_lower > 0.05
        if homogenous == True and row['classification'] == "Truncating":
            pathogenecity = "Pathogenic"

        row['nMinor'] = nMinor
        row['nMajor'] = nMajor
        row['lohstatus'] = lohstatus
        row['hom_lo'] = "{:.9f}".format(expHomCI_lo),
        row['hom_hi'] = "{:.9f}".format(expHomCI_hi),
        row['hom_pbinom_lo'] = "{:.9f}".format(expHom_pbinom_lower),
        row['homogenous'] = homogenous
        row['pathogenecity'] = pathogenecity
        row['af'] = expHomAF
        if homogenous and exonicFuncMane == "nonsynonymous_SNV":
            row['classification'] = "Missense"
        row['hom_lo'] = row['hom_lo'][0] if isinstance(row['hom_lo'], tuple) else row['hom_lo']
        row['hom_hi'] = row['hom_hi'][0] if isinstance(row['hom_hi'], tuple) else row['hom_hi']
        row['hom_pbinom_lo'] = row['hom_pbinom_lo'][0] if isinstance(row['hom_pbinom_lo'], tuple) else row['hom_pbinom_lo']

    except Exception as e:
        print(e)
        pass

    return row

def main(**kwargs): #clinical_data: pd.DataFrame, cna_data: pd.DataFrame, snv_data: pd.DataFrame, ascat_data: pd.DataFrame, amis_data: pd.DataFrame):
    """Import genomic variants produced by sequencing analysis pipelines to populate corresponding models into Django database.

      Usage
    -------
        `python manage.py import_genomic_variants --somatic_variants <filepath> --copy_number_alterations <filepath> --filter=<field> --equal=<value>`

    """
    help = "Import genomic alterations into the database."

    #clinical_data = pd.read_csv(kwargs.get("clinical_data", ""), sep="\t")

    #snv_data = pd.read_csv(kwargs.get("somatic_variants", ""), sep="\t")
    #ascat_data = pd.read_csv(kwargs.get("ascatestimates", ""), sep="\t")
    #amis_data = pd.read_csv(kwargs.get("alphamissenses", ""), sep="\t")

    cna_objects = []

    # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --copy_number_alterations /path/to/file"
    if kwargs["copy_number_alterations"]:
        output = kwargs["output"]
        cores = int(kwargs["cores"]) if kwargs["cores"] else 0
        cna_data = pd.read_csv(kwargs.get("copy_number_alterations", ""), sep="\t")

        refgenome = kwargs["refgen"] if kwargs["refgen"] else "GRCh38"
        ploidy_coeff = 2.5
        ploidy = None
        # TODO: if given, map tumortype(implement internal list) to external api identificator in query phase, else None
        tumortype = kwargs["tumortype"] if kwargs["tumortype"] else "HGSOC"
        header = ["ID","Gene","chr","start","end","strand","band","type","sample","nProbesCr","nProbesAf","logR","baf","nAraw","nBraw","nMajor","nMinor","purifiedLogR","purifiedBaf","purifiedLoh","CNstatus","LOHstatus","minPurifiedLogR","maxPurifiedLogR","breaksInGene"]

        cnaobjects = []

        ascats = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
        cnas_filtered = df_apply(cna_data, filter_cnas_by_ploidy, None, None, True, False, cores=cores, ascats=ascats).dropna()
        cnadf = pd.DataFrame(dict(zip(cnas_filtered.index, cnas_filtered.values))).T
        #cnadf = pd.DataFrame([cnas_filtered.T])
        cnadf.to_csv(output, sep='\t')

        print(cnadf)

        # TODO: query OncoKB and CGI after raw importing, harmonize results
        #external_api_requests.query_oncokb_cnas(cnaobjects)

        # TODO: Rank results by Sift, Polyphen, Alphamissense scores, OncoKB and CGI levels

    if kwargs["somatic_variants"] and not kwargs["post_annotate"]:
        output = kwargs["output"]
        cores = int(kwargs["cores"]) if kwargs["cores"] else 0
        refgenome = kwargs["refgen"] if kwargs["refgen"] else "GRCh38"
        tumortype = kwargs["tumortype"] if kwargs["tumortype"] else "HGSOC"
        ascats = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
        #alphamissenses = pd.read_csv(kwargs["alphamissenses"], sep="\t", encoding='utf-8')
        snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t", encoding='utf-8')
        cnas = pd.read_csv(kwargs["cn_annotations"], sep="\t", encoding='utf-8')[['sample','Gene','nMinor','nMajor','LOHstatus']].dropna(subset=['Gene','nMinor', 'nMajor','LOHstatus'])

        print("CNAs len",len(cnas))
        snvs_filtered = df_apply(snvs, filter_and_classify_snvs, None, None, True, True, cores=cores, cnas=cnas, alphamissenses=None, ascats=ascats)

        joined = []
        for s in snvs_filtered:
            if isinstance(s, list):
                joined.extend(s)
        #print(joined)
        #snvdf = pd.DataFrame(dict(zip(snvs_filtered[0][0].index, snvs_filtered[0][0].values))).T
        #snvdf = pd.concat([s for s in joined], axis=0)
        snvdf = pd.DataFrame(joined)

        snvdf.to_csv(output, sep='\t')
        print(snvdf)

    if kwargs["somatic_variants"] and kwargs["post_annotate"]:
        output = kwargs["output"]
        cores = int(kwargs["cores"]) if kwargs["cores"] else 0
        refgenome = kwargs["refgen"] if kwargs["refgen"] else "GRCh38"
        tumortype = kwargs["tumortype"] if kwargs["tumortype"] else "HGSOC"
        ascats = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
        snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t", encoding='utf-8')
        cnas = pd.read_csv(kwargs["cn_annotations"], sep="\t", encoding='utf-8')[['sample','Gene','nMinor','nMajor','LOHstatus']].dropna(subset=['Gene','nMinor', 'nMajor','LOHstatus'])

        print("CNAs len",len(cnas))
        cna_grps = cnas.groupby('sample')
        snv_grps = snvs.groupby('sample_id')
        for gname, cna_grp in cna_grps:
            print(gname)
            try:
                if os.path.exists(output+"/"+gname+"_snvs.csv"):
                    print("Output exists! Skipping..")
                    continue
                snv_grp = snv_grps.get_group(gname)
                snvs_filtered = df_apply(snv_grp, post_filter_and_classify_snvs_by_sample, None, None, True, True, cores=cores,
                                         cnas=cna_grp, ascats=ascats)
                snvdf = pd.DataFrame(snvs_filtered)
                snvdf.to_csv(output+"/"+gname+"_snvs.csv", sep='\t', header=False)
            except Exception as e:
                print(e)
                pass

        #snvs_filtered = df_apply(snvs, post_filter_and_classify_snvs, None, None, True, True, cores=cores, cnas=cnas, ascats=ascats)

        #joined = []
        #for s in snvs_filtered:
        #    if isinstance(s, list):
        #        joined.extend(s)
        #print(joined)
        #snvdf = pd.DataFrame(dict(zip(snvs_filtered[0][0].index, snvs_filtered[0][0].values))).T
        #snvdf = pd.concat([s for s in joined], axis=0)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        help="Path to CSV or TSV file",
    )
    parser.add_argument(
        "--somatic_variants",
        type=str,
        required=False,
        help="Path to CSV or TSV file to import data",
    )
    parser.add_argument(
        "--copy_number_alterations",
        type=str,
        required=False,
        help="Path to CSV or TSV file to import data",
    )
    parser.add_argument(
        "--clinical_data",
        type=str,
        required=False,
        help="Path to CSV or TSV file to import data",
    )
    parser.add_argument(
        "--oncokb_actionable_targets",
        type=str,
        required=False,
        help="Path to CSV or TSV file to import data",
    )
    parser.add_argument(
        "--ascatestimates",
        type=str,
        required=False,
        help="Path to CSV or TSV file to import data",
    )

    parser.add_argument(
        "--alphamissenses",
        type=str,
        required=False,
        help="Path to CSV or TSV file to import data",
    )

    parser.add_argument(
        "--filter",
        type=str,
        required=False,
        help="Field to filter data",
    )
    parser.add_argument(
        "--contains",
        type=str,
        required=False,
        help="Value to filter data",
    )
    parser.add_argument(
        "--equal",
        type=str,
        required=False,
        help="Value to filter data",
    )
    parser.add_argument(
        "--notequal",
        type=str,
        required=False,
        help="Value to filter data",
    )
    parser.add_argument(
        "--gt",
        type=str,
        required=False,
        help="Greater than value to filter data",
    )
    parser.add_argument(
        "--lt",
        type=str,
        required=False,
        help="Less than value to filter data",
    )
    parser.add_argument(
        "--deletesnvs",
        action='store_true',
        required=False,
        help="Remove variants from database",
    )
    parser.add_argument(
        "--deletecnas",
        action='store_true',
        required=False,
        help="Remove variants from database",
    )
    parser.add_argument(
        "--noheader",
        action='store_true',
        required=False,
        help="Use hardcoded header",
    )
    parser.add_argument(
        "--cnfilter",
        action='store_true',
        required=False,
        help="Filter by copynumber threshold",

    )
    parser.add_argument(
        "--all",
        action='store_true',
        required=False,
        help="Pass all variants",

    )
    parser.add_argument(
        "--tumortype",
        type=str,
        required=False,
        help="tumortype identifier OncoKB: HGSOC = CGI: OVE",
    )

    parser.add_argument(
        "--refgen",
        type=str,
        required=False,
        help="Reference genome version in format GRCh38",
    )
    parser.add_argument(
        "--cores",
        type=str,
        required=False,
        help="",
    )
    parser.add_argument(
        "--cn_annotations",
        type=str,
        required=False,
        help="Filtered and annotated CNAs",
    )
    parser.add_argument(
        "--post_annotate",
        action='store_true',
        required=False,
        help="",

    )
    args = parser.parse_args()

    main(**vars(args))