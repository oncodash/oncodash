import logging

import pandas as pd
from clin_overview.models import ClinicalData
from django.core.management.base import BaseCommand
from genomics.models import CopyNumberAlteration, CNAscatEstimate
from genomics.models import SomaticVariant
from genomics.models import ActionableTarget
from genomics.models import cna_annotation, snv_annotation
from genomics.models import AlterationType
from scipy import stats
from genomics.management.commands import external_api_requests


def map_sample_to_patient_id(sample_name):

    c_code = sample_name.split("_")[0]
    try:
        for rec in ClinicalData.objects.filter(cohort_code=c_code):
            return int(getattr(rec,'patient_id'))

    except Exception as e:
        print("No patient with cohort code", c_code, "available in the database")


def map_cohort_code_to_patient_id(cohort_code):
    try:
        for rec in ClinicalData.objects.filter(cohort_code=cohort_code):
            return int(getattr(rec,'patient_id'))

    except Exception as e:
        logging.exception(e)
        print("No patient with cohort code", cohort_code, "available in the database")

def get_nminor(pid, sid, gene):
    cna = cna_annotation.objects.all().filter(patient_id=pid).filter(sample_id=sid).filter(hugoSymbol=gene)
    if cna:
        return cna[0].nMinor
    else:
        return None
def get_nmajor(pid, sid, gene):
    cna = cna_annotation.objects.all().filter(patient_id=pid).filter(sample_id=sid).filter(hugoSymbol=gene)
    if cna:
        return cna[0].nMinor
    else:
        return None

def get_loh(pid, sid, gene):
    cna = cna_annotation.objects.all().filter(patient_id=pid).filter(sample_id=sid).filter(hugoSymbol=gene)
    if cna:
        return cna[0].lohstatus
    else:
        return "NA"

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


class Command(BaseCommand):
    """Import genomic variants produced by sequencing analysis pipelines to populate corresponding models into Django database.

      Usage
    -------
        `python manage.py import_genomic_variants --somatic_variants <filepath> --copy_number_alterations <filepath> --filter=<field> --equal=<value>`

    """

    help = "Import genomic alterations into the database."

    def add_arguments(self, parser):
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
            "--alphamissense",
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

    def handle(self, *args, **kwargs):

        def handle_boolean_field(value, field=None, default=False):
            if str(value).lower() in ["yes", "t", "true"]:
                return True
            elif str(value).lower() in ["no", "f", "false"]:
                return False
            else:
                return None if pd.isna(value) else value

        def handle_float_field(value):
            return None if pd.isna(value) else float(value.replace(",", "."))

        def handle_string_field(value):
            return None if pd.isna(value) else value

        def handle_cn_field(value):
            return None if pd.isna(value) else value

        def handle_int_field(value):
            return None if pd.isna(value) else value

        def handle_date_field(value):
            return None if pd.isna(value) else value

        def handle_decimal_field(value):
            return None if pd.isna(value) else value


        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --somatic_variants /path/to/file"
        if kwargs["somatic_variants"]:
            refgenome = kwargs["refgen"] if kwargs["refgen"] else "GRCh38"
            tumortype = kwargs["tumortype"] if kwargs["tumortype"] else "HGSOC"
            ascats = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
            alphamissense = pd.read_csv(kwargs["alphamissense"], sep="\t", encoding='utf-8')
            snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t", encoding='utf-8')
            snvobjs = []
            for index, row in snvs.iterrows():
                varfilter = False
                if kwargs["filter"]:
                    fvalue = handle_string_field(row[kwargs["filter"]])
                    if kwargs["equal"]:
                        if fvalue == kwargs["equal"]:
                            varfilter = True
                    if kwargs["notequal"]:
                        if fvalue != kwargs["notequal"]:
                            varfilter = True
                    if kwargs["contains"]:
                        if kwargs["contains"] in fvalue:
                            varfilter = True
                    if kwargs["gt"]:
                        if handle_decimal_field(fvalue) > float(kwargs["gt"]):
                            varfilter = True
                    if kwargs["lt"]:
                        if handle_decimal_field(fvalue) < float(kwargs["lt"]):
                            varfilter = True

                # patient	CHROM	POS	REF	ALT	ID	FILTER	cytoBand	Func.MANE	Gene.MANE	GeneDetail.MANE	ExonicFunc.MANE	AAChange.MANE	Func.refGene	Gene.refGene	GeneDetail.refGene	ExonicFunc.refGene	AAChange.refGene	genomicSuperDups	dbscSNV_ADA_SCORE	dbscSNV_RF_SCORE	COSMIC_ID	COSMIC_OCCURRENCE	COSMIC_TOTAL_OCC	COSMIC_CONF_SOMA	CLNSIG	CLNSIGCONF	CLNDN	CLNREVSTAT	CLNALLELEID	CLNDISDB	Interpro_domain	regulomeDB	CADD_raw	CADD_phred	1000G_ALL	1000G_EUR	gnomAD_genome_ALL	gnomAD_genome_NFE	gnomAD_genome_FIN	gnomAD_genome_max	gnomAD_exome_nc_ALL	gnomAD_exome_nc_NFE	gnomAD_exome_nc_NFE_SWE	gnomAD_exome_nc_FIN	gnomAD_exome_nc_max	Truncal	readCounts	samples
                if varfilter == True or kwargs["filter"] is None:
                    pid = map_cohort_code_to_patient_id(row["patient"])
                        
                    if pid:
                        sv_class = None
                        amisscore = None
                        pathogenecity = None
                        if len(str(row['AAChange.refGene'])) > 2:
                            isoforms = parse_isoforms(str(row['AAChange.refGene']))
                            for isof in isoforms:
                                ps = isof.split(':')
                                protein = ps[1]
                                print("protein: "+protein)
                                amis = alphamissense.loc[alphamissense['protein_variant'] == protein]
                                amisscore = amis['am_pathogenicity'].values[0] if len(amis['am_pathogenicity']) > 0 else 0.0
                                # TODO: vote pathogenecity by multiple estimates from sift,polyphen,oncokb,cgi
                                pathogenecity = amis['am_class'].values[0] if len(amis['am_class']) > 0 else None

                        samples = handle_string_field(row["samples"]).split(';') if handle_string_field(row["samples"]) else []
                        readcounts = handle_string_field(row["readCounts"]).split(';') if handle_string_field(row["readCounts"]) else []
                        i = 0

                        exonicFuncMane = handle_string_field(row["ExonicFunc.MANE"])
                        funcMane = handle_string_field(row["Func.MANE"])
                        funcRefgene = handle_string_field(row["Func.refGene"])
                        ada_score = handle_decimal_field(row["dbscSNV_ADA_SCORE"])
                        rf_score = handle_decimal_field(row["dbscSNV_RF_SCORE"])
                        for sample_id in samples:

                            # Splicing mutations
                            #   funcMane | funRefgene = splicing / splicesite / intronic = > dbscSNV_ADA / RF_SCORE > 0.95
                            # funcMane = handle_string_field(row["Func.MANE"])
                            # funcRefgene = handle_string_field(row["Func.refGene"])

                            # Truncating and Missenses => test homogeneity
                            #truncating

                            #if exonicFuncMane == ("frameshift_insertion" or "frameshift_deletion" or "stopgain" or "nonsynonymous_SNV"):
                                # Calculate homogeneity estimate
                            tf = ascats.filter(sample=sample_id)[0].purity #loc[ascats['sample'] == sample_id]['purity'].values[0]
                            readcount = readcounts[i].split(',')
                            ad0 = int(readcount[0])
                            ad1 = int(readcount[1])
                            depth = ad0+ad1
                            geneMANE = handle_string_field(row["Gene.MANE"]).split(';')
                            genes = set(geneMANE)
                            geneRefGene = handle_string_field(row["Gene.refGene"]).split(';')
                            for g in geneRefGene:
                                genes.add(g)
                            for gene in genes:
                                nMajor = handle_cn_field(get_nmajor(pid, sample_id, gene))
                                nMinor = handle_cn_field(get_nminor(pid, sample_id, gene))
                                lohstatus = get_loh(pid, sample_id, gene)
                                expHomAF = 0.0
                                expHomCI_lo = 0.0
                                expHomCI_hi = 0.0
                                expHom_pbinom_lower = 0.0
                                homogenous = None

                                if nMajor and nMinor:
                                    cn = int(nMinor)+int(nMajor)
                                    expHomAF = expectedAF(cn, cn, tf)
                                    expHomCI_lo = stats.binom.ppf(0.025, depth, expHomAF)
                                    expHomCI_hi = stats.binom.ppf(0.975, depth, expHomAF)
                                    expHomCI_cover = expHomCI_lo <= ad1
                                    expHom_pbinom_lower = stats.binom.cdf(ad1, depth, expHomAF)
                                    homogenous = expHom_pbinom_lower > 0.05

                                if homogenous and exonicFuncMane == "nonsynonymous_SNV":
                                    sv_class = "Missense"
                                if exonicFuncMane == ("frameshift_insertion" or "frameshift_deletion" or "stopgain"):
                                    sv_class = "Truncating"
                                if exonicFuncMane == (
                                        "nonframeshift_deletion" or "nonframeshift_substitution" or "nonframeshift_insertion"):
                                    sv_class = "Other"
                                if not sv_class:
                                    if funcMane == ("splicing" or "splicesite" or "intron" or "intronic") or funcRefgene == ("splicing" or "splicesite" or "intron" or "intronic"):
                                        if (ada_score and float(ada_score) > 0.95) or (rf_score and float(rf_score) > 0.95):
                                            sv_class = "Splicing"
                                        else:
                                            continue
                                if(sv_class):
                                    snvobjs.append(snv_annotation(
                                        patient_id=pid,
                                        sample_id= sample_id,
                                        ref_id = handle_string_field(row["ID"]),
                                        chromosome = handle_string_field(row["CHROM"]),
                                        position = handle_int_field(row["POS"]),
                                        reference_allele = handle_string_field(row["REF"]),
                                        sample_allele = handle_string_field(row["ALT"]),
                                        referenceGenome = refgenome,
                                        hugoSymbol = gene,
                                        #entrezGeneId = "",
                                        #alteration: string;
                                        tumorType = tumortype,
                                        consequence = exonicFuncMane,
                                        #proteinStart: string;
                                        #proteinEnd: string;
                                        #oncogenic: string;
                                        #mutationEffectDescription: string;
                                        #gene_role: string;
                                        #citationPMids: string;
                                        #geneSummary: string;
                                        #variantSummary: string;
                                        #tumorTypeSummary: string;
                                        #diagnosticSummary: string;
                                        #diagnosticImplications: string;
                                        #prognosticImplications: string;
                                        #treatments: string;
                                        nMinor = nMinor,
                                        nMajor = nMajor,
                                        #oncokb_level: string;
                                        #cgi_level: string;
                                        #rank: number;
                                        ad0 = ad0,
                                        ad1 = ad1,
                                        af = expHomAF,
                                        readcount = ad0+ad1,
                                        depth = depth,
                                        lohstatus = lohstatus,
                                        hom_lo = expHomCI_lo,
                                        hom_hi = expHomCI_hi,
                                        hom_pbinom_lo = expHom_pbinom_lower,
                                        homogenous = homogenous,
                                        funcMane = handle_string_field(row["Func.MANE"]),
                                        funcRefgene = handle_string_field(row["Func.refGene"]),
                                        exonicFuncMane = handle_string_field(row["ExonicFunc.MANE"]),
                                        cadd_score = handle_decimal_field(row["CADD_phred"]),
                                        ada_score = ada_score,
                                        rf_score = rf_score,
                                        #sift_cat: string;
                                        #sift_val: number;  # Will be dded to WGS output in near future https://sift.bii.a-star.edu.sg/
                                        #polyphen_cat: string;
                                        #polyphen_val: number;  # Will be dded to WGS output in near future http://genetics.bwh.harvard.edu/pph2/
                                        amis_score = handle_decimal_field(amisscore),
                                        cosmic_id = handle_string_field(row["COSMIC_ID"]),
                                        clinvar_id = handle_string_field(row["CLNALLELEID"]),
                                        clinvar_sig = handle_string_field(row["CLNSIG"]),
                                        clinvar_status = handle_string_field(row["CLNREVSTAT"]),
                                        clinvar_assoc = handle_string_field(row["CLNDN"]),
                                        pathogenecity = handle_string_field(pathogenecity),
                                        classification = sv_class,
                                    ))
                                    print("class: "+sv_class)
                            i += 1
                    else:
                        logging.warning("No clinical data available for patient "+row["patient"])

            try:
                objs = snv_annotation.objects.bulk_create(snvobjs)
                logging.info("Imported " + str(len(objs)) + " records.")
            except Exception as e:
                logging.exception(e)

        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --copy_number_alterations /path/to/file"
        if kwargs["copy_number_alterations"]:
            refgenome = kwargs["refgen"] if kwargs["refgen"] else "GRCh38"
            ploidy_coeff = 2.5
            ploidy = None
            # TODO: if given, map tumortype(implement internal list) to external api identificator in query phase, else None
            tumortype = kwargs["tumortype"] if kwargs["tumortype"] else "HGSOC"
            header = ["ID","Gene","chr","start","end","strand","band","type","sample","nProbesCr","nProbesAf","logR","baf","nAraw","nBraw","nMajor","nMinor","purifiedLogR","purifiedBaf","purifiedLoh","CNstatus","LOHstatus","minPurifiedLogR","maxPurifiedLogR","breaksInGene"]
            if kwargs["noheader"]:
                cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t", encoding='utf-8', names=header)
            else:
                cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t", encoding='utf-8')

            cnaobjects = []
            ascats = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
            for index, row in cnas.iterrows():
                ploidy = ascats.loc[ascats['sample']==row["sample"]]['ploidy'].values[0]
                varfilter = False
                if kwargs["filter"]:
                    fvalue = handle_string_field(row[kwargs["filter"]])
                    if kwargs["equal"]:
                        if fvalue == kwargs["equal"]:
                            varfilter = True
                    if kwargs["notequal"]:
                        if fvalue != kwargs["notequal"]:
                            varfilter = True
                    if kwargs["contains"]:
                        if kwargs["contains"] in fvalue:
                            varfilter = True
                    if kwargs["gt"]:
                        if handle_decimal_field(fvalue) > float(kwargs["gt"]):
                            varfilter = True
                    if kwargs["lt"]:
                        if handle_decimal_field(fvalue) < float(kwargs["lt"]):
                            varfilter = True
                if kwargs["cnfilter"]:
                    nminor = handle_cn_field(row['nMinor'])
                    nmajor = handle_cn_field(row['nMajor'])
                    if nminor and nmajor:
                        cn = int(nminor) + int(nmajor)
                        if ploidy and float(ploidy) > 0:
                            if cn < 1 or cn > ploidy_coeff * float(ploidy):
                                varfilter = True

                if kwargs["all"]:
                    varfilter = True

                if varfilter == True:
                    logging.info(row["sample"])
                    ### "ID"			"Gene"		"chr"	"start"		"end"		"strand""band"		"type"		"sample"	"nProbesCr"	"nProbesAf"	"logR""baf"	"nAraw"	"nBraw"	"nMajor"	"nMinor"	"purifiedLogR"	"purifiedBaf"	"purifiedLoh"	"CNstatus"	"LOHstatus"	"minPurifiedLogR"	"maxPurifiedLogR"	"breaksInGene"
                    pid = map_sample_to_patient_id(row["sample"])
                    if pid:
                        cnaobjects.append(cna_annotation(
                            patient_id=pid,    # sample name includes cohort code which is mapped to patient id
                            sample_id=handle_string_field(row["sample"]),
                            referenceGenome = refgenome,
                            hugoSymbol=handle_string_field(row["Gene"]),
                            entrezGeneId=handle_string_field(row["ID"]),
                            alteration=str.upper(handle_string_field(AlterationType[row["CNstatus"]].value)),
                            tumorType=handle_string_field(tumortype),
                            nMajor=handle_int_field(row["nMajor"]),
                            nMinor=handle_int_field(row["nMinor"]),
                            lohstatus=handle_string_field(row["LOHstatus"]),
                            ploidy=handle_decimal_field(ploidy)
                        ))
                    else:
                        logging.warning("No patient available with sample " + row["sample"])

            try:
                objs = cna_annotation.objects.bulk_create(cnaobjects)
                logging.info("Imported " + str(len(objs)) + " records.")
            except Exception as e:
                logging.exception(e)
                print("Exception: ", e)

            # TODO: query OncoKB and CGI after raw importing, harmonize results
            #external_api_requests.query_oncokb_cnas(cnaobjects)

            # TODO: Rank results by Sift, Polyphen, Alphamissense scores, OncoKB and CGI levels



        if kwargs["oncokb_actionable_targets"]:
            csv = pd.read_csv(kwargs["oncokb_actionable_targets"], sep="\t", encoding='utf-8')
            for index, row in csv.iterrows():
                try:
                    rec, created = ActionableTarget.objects.get_or_create(
                        gene=handle_string_field(row["Gene"]),
                    )
                    rec.save()
                except Exception as e:
                    logging.exception(e)

        if kwargs["ascatestimates"]:
            csv = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
            estobjects = []
            #"sample"    "aberrant"    "purity"    "psi"    "ploidy"    "TP53.purity.mean"    "TP53.VAF"    "goodnessOfFit"    "penalizedGoodnessOfFit"

            for index, row in csv.iterrows():
                patient_id = map_cohort_code_to_patient_id(row["sample"].split("_")[0])
                if patient_id:
                    estobjects.append(CNAscatEstimate(
                            patient_id = patient_id,
                            sample = handle_string_field(row["sample"]),
                            aberrant = handle_boolean_field(row["aberrant"]),
                            purity = handle_decimal_field(row["purity"]),
                            psi = handle_decimal_field(row["psi"]),
                            ploidy = handle_decimal_field(row["ploidy"]),
                            TP53_purity_mean = handle_decimal_field(row["TP53.purity.mean"]),
                            TP53_VAF = handle_decimal_field(row["TP53.VAF"]),
                            goodnessOfFit = handle_decimal_field(row["goodnessOfFit"]),
                            penalizedGoodnessOfFit = handle_decimal_field(row["penalizedGoodnessOfFit"])
                    ))
            try:
                created = CNAscatEstimate.objects.bulk_create(estobjects)
                print("Imported " + str(len(created)) + " records.")
            except Exception as e:
                logging.exception(e)
                print("Exception: ", e)
