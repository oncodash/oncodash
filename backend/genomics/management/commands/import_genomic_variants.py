import logging

import pandas as pd
from clin_overview.models import ClinicalData
from django.core.management.base import BaseCommand
from genomics.models import CopyNumberAlteration, CNAscatEstimate
from genomics.models import SomaticVariant
from genomics.models import ActionableTarget


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

        def handle_cn_field(value):
            return None if pd.isna(value) else value

        def handle_int_field(value):
            return None if pd.isna(value) else value

        def handle_date_field(value):
            return None if pd.isna(value) else value

        def handle_decimal_field(value):
            return value if pd.isna(value) else None


        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --somatic_variants /path/to/file"
        if kwargs["somatic_variants"]:
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
                        snvobjs.append(SomaticVariant(
                            patient_id=pid,  # patient field is actually cohort code
                            chromosome=handle_string_field(row["CHROM"]),
                            position=handle_int_field(row["POS"]),
                            reference_allele=handle_string_field(row["REF"]),
                            sample_allele=handle_string_field(row["ALT"]),
                            ref_id=handle_string_field(row["ID"]),
                            filter = handle_string_field(row["FILTER"]),
                            cytoBand = handle_string_field(row["cytoBand"]),
                            funcMANE = handle_string_field(row["Func.MANE"]),
                            geneMANE = handle_string_field(row["Gene.MANE"]),
                            geneDetailMANE = handle_string_field(row["GeneDetail.MANE"]),
                            exonicFuncMANE = handle_string_field(row["ExonicFunc.MANE"]),
                            aaChangeMANE = handle_string_field(row["AAChange.MANE"]),
                            funcRefGene = handle_string_field(row["Func.refGene"]),
                            geneRefGene = handle_string_field(row["Gene.refGene"]),
                            geneDetailRefGene = handle_string_field(row["GeneDetail.refGene"]),
                            exonicFuncRefGene = handle_string_field(row["ExonicFunc.refGene"]),
                            aaChangeRefGene = handle_string_field(row["AAChange.refGene"]),
                            genomicSuperDups = handle_string_field(row["genomicSuperDups"]),
                            dbscSNV_ADA_SCORE = handle_decimal_field(row["dbscSNV_ADA_SCORE"]),
                            dbscSNV_RF_SCORE = handle_decimal_field(row["dbscSNV_RF_SCORE"]),
                            cosmic_id = handle_string_field(row["COSMIC_ID"]),
                            cosmic_occurrence = handle_string_field(row["COSMIC_OCCURRENCE"]),
                            cosmic_total_occ = handle_string_field(row["COSMIC_TOTAL_OCC"]),
                            cosmic_conf_soma = handle_string_field(row["COSMIC_CONF_SOMA"]),
                            clnsig = handle_string_field(row["CLNSIG"]),
                            clnsigconf = handle_string_field(row["CLNSIGCONF"]),
                            clndn = handle_string_field(row["CLNDN"]),
                            clnrevstat = handle_string_field(row["CLNREVSTAT"]),
                            clnalleleid = handle_string_field(row["CLNALLELEID"]),
                            clndisdb = handle_string_field(row["CLNDISDB"]),
                            interpro_domain = handle_string_field(row["Interpro_domain"]),
                            regulomeDB = handle_string_field(row["regulomeDB"]),
                            cadd_raw = handle_decimal_field(row["CADD_raw"]),
                            cadd_phred = handle_decimal_field(row["CADD_phred"]),
                            thousandG_ALL	 = handle_decimal_field(row["1000G_ALL"]),
                            thousandG_EUR	 = handle_decimal_field(row["1000G_EUR"]),
                            gnomAD_genome_ALL	 = handle_decimal_field(row["gnomAD_genome_ALL"]),
                            gnomAD_genome_NFE	 = handle_decimal_field(row["gnomAD_genome_NFE"]),
                            gnomAD_genome_FIN	 = handle_decimal_field(row["gnomAD_genome_FIN"]),
                            gnomAD_genome_max	 = handle_decimal_field(row["gnomAD_genome_max"]),
                            gnomAD_exome_nc_ALL	 = handle_decimal_field(row["gnomAD_exome_nc_ALL"]),
                            gnomAD_exome_nc_NFE	 = handle_decimal_field(row["gnomAD_exome_nc_NFE"]),
                            gnomAD_exome_nc_NFE_SWE	 = handle_decimal_field(row["gnomAD_exome_nc_NFE_SWE"]),
                            gnomAD_exome_nc_FIN	 = handle_decimal_field(row["gnomAD_exome_nc_FIN"]),
                            gnomAD_exome_nc_max	 = handle_decimal_field(row["gnomAD_exome_nc_max"]),
                            truncal	 = handle_string_field(row["Truncal"]),
                            readCounts	 = handle_string_field(row["readCounts"]),
                            samples = handle_string_field(row["samples"]),
                        ))
                    else:
                        logging.warning("No clinical data available for patient "+row["patient"])

            try:
                objs = SomaticVariant.objects.bulk_create(snvobjs)
                logging.info("Imported " + str(len(objs)) + " records.")
            except Exception as e:
                logging.exception(e)

        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --copy_number_alterations /path/to/file"
        if kwargs["copy_number_alterations"]:
            ploidy_coeff = 2.5
            ascats = pd.read_csv(kwargs["ascatestimates"], sep="\t", encoding='utf-8')
            header = ["ID","Gene","chr","start","end","strand","band","type","sample","nProbesCr","nProbesAf","logR","baf","nAraw","nBraw","nMajor","nMinor","purifiedLogR","purifiedBaf","purifiedLoh","CNstatus","LOHstatus","minPurifiedLogR","maxPurifiedLogR","breaksInGene"]
            if kwargs["noheader"]:
                cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t", encoding='utf-8', names=header)
            else:
                cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t", encoding='utf-8')

            cnaobjects = []
            for index, row in cnas.iterrows():
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
                        ploidys = ascats.loc[ascats['sample'] == row["sample"]]['ploidy']
                        for ploidy in ploidys:
                            if cn < 1 or cn > ploidy_coeff * float(ploidy):
                                varfilter = True

                if kwargs["all"]:
                    varfilter = True

                if varfilter == True:
                    ### "ID"			"Gene"		"chr"	"start"		"end"		"strand""band"		"type"		"sample"	"nProbesCr"	"nProbesAf"	"logR""baf"	"nAraw"	"nBraw"	"nMajor"	"nMinor"	"purifiedLogR"	"purifiedBaf"	"purifiedLoh"	"CNstatus"	"LOHstatus"	"minPurifiedLogR"	"maxPurifiedLogR"	"breaksInGene"
                    pid = map_sample_to_patient_id(row["sample"])

                    if pid:
                        cnaobjects.append(CopyNumberAlteration(
                            patient_id=pid,    # sample name includes cohort code which is mapped to patient id
                            sample_id=handle_string_field(row["sample"]),
                            chromosome=handle_string_field(row["chr"]),
                            start=handle_int_field(row["start"]),
                            end=handle_int_field(row["end"]),
                            band=handle_string_field(row["band"]),
                            type=handle_string_field(row["type"]),
                            gene_id=handle_string_field(row["ID"]),
                            gene = handle_string_field(row["Gene"]),
                            strand = handle_int_field(row["strand"]),
                            nProbesCr = handle_int_field(row["nProbesCr"]),
                            nProbesAf = handle_int_field(row["nProbesAf"]),
                            logR =  handle_decimal_field(row["logR"]),
                            baf = handle_decimal_field(row["baf"]),
                            nAraw = handle_decimal_field(row["nAraw"]),
                            nBraw = handle_decimal_field(row["nBraw"]),
                            nMajor = handle_int_field(row["nMajor"]),
                            nMinor = handle_int_field(row["nMinor"]),
                            purifiedLogR = handle_decimal_field(row["purifiedLogR"]),
                            purifiedBaf = handle_decimal_field(row["purifiedBaf"]),
                            purifiedLoh = handle_decimal_field(row["purifiedLoh"]),
                            CNstatus = handle_string_field(row["CNstatus"]),
                            LOHstatus = handle_string_field(row["LOHstatus"]),
                            minPurifiedLogR=handle_decimal_field(row["minPurifiedLogR"]),
                            maxPurifiedLogR = handle_decimal_field(row["maxPurifiedLogR"]),
                            breaksInGene = handle_string_field(row["breaksInGene"]),
                        ))
                    else:
                        logging.warning("No patient available with sample " + row["sample"])

            try:
                objs = CopyNumberAlteration.objects.bulk_create(cnaobjects)
                logging.info("Imported " + str(len(objs)) + " records.")
            except Exception as e:
                logging.exception(e)
                print("Exception: ", e)


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

        if kwargs["ascatestimates"] and not kwargs['copy_number_alterations']:
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
