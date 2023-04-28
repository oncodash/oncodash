import pandas as pd
from clin_overview.models import ClinicalData
from django.core.management.base import BaseCommand
from genomics.models import CopyNumberAlteration
from genomics.models import SomaticVariant


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
        print("No patient with cohort code", cohort_code, "available in the database")


class Command(BaseCommand):
    """Import genomic variants to populate corresponding models.

      Usage
    -------
        `python manage.py import_genomic_variants --somatic_variants <filepath> --copy_number_alterations <filepath>`
    """

    help = "Import genomic alterations into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "-snvs",
            "--somatic_variants",
            type=str,
            required=False,
            help="File to import data",
        )
        parser.add_argument(
            "-cnas",
            "--copy_number_alterations",
            type=str,
            required=False,
            help="File to import data",
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

        def handle_int_field(value):
            return None if pd.isna(value) else value

        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --somatic_variants /path/to/file"
        if kwargs["somatic_variants"]:
            snvs = pd.read_csv(kwargs["somatic_variants"], sep="\t", encoding='utf-8')

            for index, row in snvs.iterrows():
                try:
                    # patient	CHROM	POS	REF	ALT	ID	FILTER	cytoBand	Func.MANE	Gene.MANE	GeneDetail.MANE	ExonicFunc.MANE	AAChange.MANE	Func.refGene	Gene.refGene	GeneDetail.refGene	ExonicFunc.refGene	AAChange.refGene	genomicSuperDups	dbscSNV_ADA_SCORE	dbscSNV_RF_SCORE	COSMIC_ID	COSMIC_OCCURRENCE	COSMIC_TOTAL_OCC	COSMIC_CONF_SOMA	CLNSIG	CLNSIGCONF	CLNDN	CLNREVSTAT	CLNALLELEID	CLNDISDB	Interpro_domain	regulomeDB	CADD_raw	CADD_phred	1000G_ALL	1000G_EUR	gnomAD_genome_ALL	gnomAD_genome_NFE	gnomAD_genome_FIN	gnomAD_genome_max	gnomAD_exome_nc_ALL	gnomAD_exome_nc_NFE	gnomAD_exome_nc_NFE_SWE	gnomAD_exome_nc_FIN	gnomAD_exome_nc_max	Truncal	readCounts	samples
                    rec, created = SomaticVariant.objects.get_or_create(
                        patient_id=handle_string_field(row["patient"]),  # patient field is actually cohort code
                        chromosome=handle_string_field(row["CHROM"]),
                        position=handle_string_field(row["POS"]),
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
                        dbscSNV_ADA_SCORE = handle_string_field(row["dbscSNV_ADA_SCORE"]),
                        dbscSNV_RF_SCORE = handle_string_field(row["dbscSNV_RF_SCORE"]),
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
                        cadd_raw = handle_string_field(row["CADD_raw"]),
                        cadd_phred = handle_string_field(row["CADD_phred"]),
                        thousandG_ALL	 = handle_string_field(row["1000G_ALL"]),
                        thousandG_EUR	 = handle_string_field(row["1000G_EUR"]),
                        gnomAD_genome_ALL	 = handle_string_field(row["gnomAD_genome_ALL"]),
                        gnomAD_genome_NFE	 = handle_string_field(row["gnomAD_genome_NFE"]),
                        gnomAD_genome_FIN	 = handle_string_field(row["gnomAD_genome_FIN"]),
                        gnomAD_genome_max	 = handle_string_field(row["gnomAD_genome_max"]),
                        gnomAD_exome_nc_ALL	 = handle_string_field(row["gnomAD_exome_nc_ALL"]),
                        gnomAD_exome_nc_NFE	 = handle_string_field(row["gnomAD_exome_nc_NFE"]),
                        gnomAD_exome_nc_NFE_SWE	 = handle_string_field(row["gnomAD_exome_nc_NFE_SWE"]),
                        gnomAD_exome_nc_FIN	 = handle_string_field(row["gnomAD_exome_nc_FIN"]),
                        gnomAD_exome_nc_max	 = handle_string_field(row["gnomAD_exome_nc_max"]),
                        truncal	 = handle_string_field(row["Truncal"]),
                        readCounts	 = handle_string_field(row["readCounts"]),
                        samples = handle_string_field(row["samples"]),
                    )

                    rec.save()
                except Exception as e:
                    print("Exception: ", row["patient"], e)

        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --copy_number_alterations /path/to/file"
        if kwargs["copy_number_alterations"]:
            cnas = pd.read_csv(kwargs["copy_number_alterations"], sep="\t", encoding='utf-8')

            for index, row in cnas.iterrows():
                try:
                    ### "ID"			"Gene"		"chr"	"start"		"end"		"strand""band"		"type"		"sample"	"nProbesCr"	"nProbesAf"	"logR""baf"	"nAraw"	"nBraw"	"nMajor"	"nMinor"	"purifiedLogR"	"purifiedBaf"	"purifiedLoh"	"CNstatus"	"LOHstatus"	"minPurifiedLogR"	"maxPurifiedLogR"	"breaksInGene"
                    ### "ENSG00000177757"	"FAM87B"	"chr1"	"817371"	"819837"	"1"	"p36.33"	"lincRNA"	"D327_BDNA13411"	"196557"	"114286"	"-0.0059"	"0.4998"	"0.9964"	"0.9955"	"1"	"1"	"-0.0059"	"0.4998"	"4e-04"	"Normal"	"HET"	"-0.0059"	"-0.0059"	"0"
                    pid = map_sample_to_patient_id(row["sample"])
                    rec, created = CopyNumberAlteration.objects.get_or_create(
                        patient_id=pid,    # sample name includes cohort code which is mapped to patient id
                        sample_id=handle_string_field(row["sample"]),
                        chromosome=handle_string_field(row["chr"]),
                        start=handle_string_field(row["start"]),
                        end=handle_string_field(row["end"]),
                        band=handle_string_field(row["band"]),
                        type=handle_string_field(row["type"]),
                        gene_id=handle_string_field(row["ID"]),
                        gene = handle_string_field(row["Gene"]),
                        strand = handle_string_field(row["strand"]),
                        nProbesCr = handle_string_field(row["nProbesCr"]),
                        nProbesAf = handle_string_field(row["nProbesAf"]),
                        logR =  handle_string_field(row["logR"]),
                        baf = handle_string_field(row["baf"]),
                        nAraw = handle_string_field(row["nAraw"]),
                        nBraw = handle_string_field(row["nBraw"]),
                        nMajor = handle_string_field(row["nMajor"]),
                        purifiedLogR = handle_string_field(row["purifiedLogR"]),
                        purifiedBaf = handle_string_field(row["purifiedBaf"]),
                        purifiedLoh = handle_string_field(row["purifiedLoh"]),
                        CNstatus = handle_string_field(row["CNstatus"]),
                        LOHstatus = handle_string_field(row["LOHstatus"]),
                        minPurifiedLogR=handle_string_field(row["minPurifiedLogR"]),
                        maxPurifiedLogR = handle_string_field(row["maxPurifiedLogR"]),
                        breaksInGene = handle_string_field(row["breaksInGene"]),
                    )

                    rec.save()
                except Exception as e:
                    print("Exception: ",row["sample"], e)
