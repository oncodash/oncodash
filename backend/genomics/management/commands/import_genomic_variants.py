import sys
import pandas as pd
from clin_overview.models import ClinicalData
from django.core.management.base import BaseCommand
from genomics.models import CopyNumberAlteration
from genomics.models import SomaticVariant

class ErrorSet(set):
    """A list of messages avoiding duplicates"""
    def __init__(self, show_details = False):
        super().__init__()
        self.show_details = show_details

    def add(self, err, details=""):
        if __debug__ and self.show_details:
            print("\n", err+details, file=sys.stderr, flush=True)
        super().add(err)

    def __str__(self):
        s=""
        for e in sorted(self):
            s += f"WARNING: {e}\n"
        return s


def map_sample_to_patient_id(sample_name):

    c_code = sample_name.split("_")[0]
    try:
        for rec in ClinicalData.objects.filter(cohort_code=c_code):
            return int(getattr(rec,'patient_id'))

    except Exception as e:
        print("No patient with cohort code", c_code, "available in the database", file=sys.stderr, flush=True)


def map_cohort_code_to_patient_id(cohort_code):
    try:
        for rec in ClinicalData.objects.filter(cohort_code=cohort_code):
            return int(getattr(rec,'patient_id'))

    except Exception as e:
        print("No patient with cohort code", cohort_code, "available in the database", file=sys.stderr, flush=True)


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
            "-d",
            "--errors-details",
            action='store_true',
            required=False,
            help="Show the details of all import errors/warnings (like row numbers)",
        )
        parser.add_argument(
            "-s", "--sep",
            type=str,
            required=False,
            default='\t',
            help="Separator expected in the input data",
        )
        parser.add_argument(
            "--chunksize",
            type=int,
            required=False,
            default=1000,
            help="How many input data rows to read at once",
        )


    def handle(self, *args, **kwargs):

        def handle_boolean_field(row, field_name, errors, index, field=None, default=False, ):
            if pd.isna(value):
                # errors.add("Field '"+field_name+"' has no value in row "+str(index))
                return None
            elif str(value).lower() in ["yes", "t", "true"]:
                return True
            elif str(value).lower() in ["no", "f", "false"]:
                return False
            else:
                final = None if field is None or field.__dict__["field"].null else default
                errors.add("Field '"+field_name+"' has unsupported value '"+str(value)+"'", " in row "+str(index)+", replaced by '"+str(final)+"'")
                return final
                # return None if field is None or field.__dict__["field"].null else default

        def handle_float_field(row, field_name, errors, index):
            value = row[field_name]
            if pd.isna(value):
                return None
            else:
                if type(value) == float:
                    return value
                else:
                    try:
                        float(str(value).replace(",", "."))
                    except ValueError as e:
                        errors.add(str(e)+" for field '"+field_name+"'", " in row "+str(index))
                        return None
            # return None if pd.isna(value) else float(value.replace(",", "."))

        def handle_string_field(row, field_name, errors, index):
            value = row[field_name]
            return None if pd.isna(value) else value

        def handle_int_field(row, field_name, errors, index):
            value = row[field_name]
            return None if pd.isna(value) else value

        def handle_date_field(row, field_name, errors, index):
            value = row[field_name]
            return None if pd.isna(value) else value

        def handle_decimal_field(row, field_name, errors, index):
            value = row[field_name]
            if str(value) == ".":
                return None
            return None if pd.isna(value) else value

        errors = ErrorSet(kwargs["errors_details"])

        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --somatic_variants /path/to/file"
        print("Import somatic variants...", file=sys.stderr, flush=True)
        if kwargs["somatic_variants"]:
            print("Parse somatic variants data...", file=sys.stderr, flush=True)
            index = 0
            with pd.read_csv(kwargs["somatic_variants"], sep=kwargs["sep"], encoding='utf-8', chunksize=kwargs["chunksize"]) as snvs:

                print("Load somatic variants data...", file=sys.stderr, flush=True)
                # for index, row in snvs.iterrows():
                for chunk in snvs:
                    for i,row in chunk.iterrows():
                        print(f"{index}", end="\r", file=sys.stderr, flush=True)
                        try:
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
                                rec, created = SomaticVariant.objects.get_or_create(
                                    patient_id=pid,  # patient field is actually cohort code
                                    chromosome=handle_string_field(row, "CHROM", errors, index),
                                    position=handle_int_field(row, "POS", errors, index),
                                    reference_allele=handle_string_field(row, "REF", errors, index),
                                    sample_allele=handle_string_field(row, "ALT", errors, index),
                                    ref_id=handle_string_field(row, "ID", errors, index),
                                    filter = handle_string_field(row, "FILTER", errors, index),
                                    cytoBand = handle_string_field(row, "cytoBand", errors, index),
                                    funcMANE = handle_string_field(row, "Func.MANE", errors, index),
                                    geneMANE = handle_string_field(row, "Gene.MANE", errors, index),
                                    geneDetailMANE = handle_string_field(row, "GeneDetail.MANE", errors, index),
                                    exonicFuncMANE = handle_string_field(row, "ExonicFunc.MANE", errors, index),
                                    aaChangeMANE = handle_string_field(row, "AAChange.MANE", errors, index),
                                    funcRefGene = handle_string_field(row, "Func.refGene", errors, index),
                                    geneRefGene = handle_string_field(row, "Gene.refGene", errors, index),
                                    geneDetailRefGene = handle_string_field(row, "GeneDetail.refGene", errors, index),
                                    exonicFuncRefGene = handle_string_field(row, "ExonicFunc.refGene", errors, index),
                                    aaChangeRefGene = handle_string_field(row, "AAChange.refGene", errors, index),
                                    genomicSuperDups = handle_string_field(row, "genomicSuperDups", errors, index),
                                    dbscSNV_ADA_SCORE = handle_decimal_field(row, "dbscSNV_ADA_SCORE", errors, index),
                                    dbscSNV_RF_SCORE = handle_decimal_field(row, "dbscSNV_RF_SCORE", errors, index),
                                    cosmic_id = handle_string_field(row, "COSMIC_ID", errors, index),
                                    cosmic_occurrence = handle_string_field(row, "COSMIC_OCCURRENCE", errors, index),
                                    cosmic_total_occ = handle_string_field(row, "COSMIC_TOTAL_OCC", errors, index),
                                    cosmic_conf_soma = handle_string_field(row, "COSMIC_CONF_SOMA", errors, index),
                                    clnsig = handle_string_field(row, "CLNSIG", errors, index),
                                    clnsigconf = handle_string_field(row, "CLNSIGCONF", errors, index),
                                    clndn = handle_string_field(row, "CLNDN", errors, index),
                                    clnrevstat = handle_string_field(row, "CLNREVSTAT", errors, index),
                                    clnalleleid = handle_string_field(row, "CLNALLELEID", errors, index),
                                    clndisdb = handle_string_field(row, "CLNDISDB", errors, index),
                                    interpro_domain = handle_string_field(row, "Interpro_domain", errors, index),
                                    regulomeDB = handle_string_field(row, "regulomeDB", errors, index),
                                    cadd_raw = handle_decimal_field(row, "CADD_raw", errors, index),
                                    cadd_phred = handle_decimal_field(row, "CADD_phred", errors, index),
                                    thousandG_ALL = handle_decimal_field(row, "1000G_ALL", errors, index),
                                    thousandG_EUR = handle_decimal_field(row, "1000G_EUR", errors, index),
                                    gnomAD_genome_ALL = handle_decimal_field(row, "gnomAD_genome_ALL", errors, index),
                                    gnomAD_genome_NFE = handle_decimal_field(row, "gnomAD_genome_NFE", errors, index),
                                    gnomAD_genome_FIN = handle_decimal_field(row, "gnomAD_genome_FIN", errors, index),
                                    gnomAD_genome_max = handle_decimal_field(row, "gnomAD_genome_max", errors, index),
                                    gnomAD_exome_nc_ALL = handle_decimal_field(row, "gnomAD_exome_nc_ALL", errors, index),
                                    gnomAD_exome_nc_NFE = handle_decimal_field(row, "gnomAD_exome_nc_NFE", errors, index),
                                    gnomAD_exome_nc_NFE_SWE = handle_decimal_field(row, "gnomAD_exome_nc_NFE_SWE", errors, index),
                                    gnomAD_exome_nc_FIN = handle_decimal_field(row, "gnomAD_exome_nc_FIN", errors, index),
                                    gnomAD_exome_nc_max = handle_decimal_field(row, "gnomAD_exome_nc_max", errors, index),
                                    truncal = handle_string_field(row, "Truncal", errors, index),
                                    readCounts = handle_string_field(row, "readCounts", errors, index),
                                    samples = handle_string_field(row, "samples", errors, index),
                                )

                                rec.save()
                        except KeyError as e:
                            errors.add("Field not found "+str(e), " in row "+str(index))
                        except Exception as e:
                            errors.add(str(e), " in row "+str(index))
                        finally:
                                index += 1

            print("Imported", str(index), "records.", file=sys.stderr, flush=True)


        # USAGE:  docker compose run --rm backend sh -c "python manage.py import_genomic_variants --copy_number_alterations /path/to/file"
        if kwargs["copy_number_alterations"]:
            index = 0
            print("Parse copy number data...", file=sys.stderr, flush=True)
            with pd.read_csv(kwargs["copy_number_alterations"], sep=kwargs["sep"], encoding='utf-8', chunksize=kwargs["chunksize"]) as cnas:
                print("Load copy number data...", file=sys.stderr, flush=True)
                for chunk in cnas:
                    for index, row in chunk.iterrows():
                        print(f"{index}", end="\r", file=sys.stderr, flush=True)
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

                        if varfilter == True or kwargs["filter"] is None:
                            try:
                                ### "ID"			"Gene"		"chr"	"start"		"end"		"strand""band"		"type"		"sample"	"nProbesCr"	"nProbesAf"	"logR""baf"	"nAraw"	"nBraw"	"nMajor"	"nMinor"	"purifiedLogR"	"purifiedBaf"	"purifiedLoh"	"CNstatus"	"LOHstatus"	"minPurifiedLogR"	"maxPurifiedLogR"	"breaksInGene"
                                ### "ENSG00000177757"	"FAM87B"	"chr1"	"817371"	"819837"	"1"	"p36.33"	"lincRNA"	"D327_BDNA13411"	"196557"	"114286"	"-0.0059"	"0.4998"	"0.9964"	"0.9955"	"1"	"1"	"-0.0059"	"0.4998"	"4e-04"	"Normal"	"HET"	"-0.0059"	"-0.0059"	"0"
                                pid = map_sample_to_patient_id(row["sample"])
                                rec, created = CopyNumberAlteration.objects.get_or_create(
                                    patient_id=pid,    # sample name includes cohort code which is mapped to patient id
                                    sample_id=handle_string_field(row, "sample", errors, index),
                                    chromosome=handle_string_field(row, "chr", errors, index),
                                    start=handle_int_field(row, "start", errors, index),
                                    end=handle_int_field(row, "end", errors, index),
                                    band=handle_string_field(row, "band", errors, index),
                                    type=handle_string_field(row, "type", errors, index),
                                    gene_id=handle_string_field(row, "ID", errors, index),
                                    gene = handle_string_field(row, "Gene", errors, index),
                                    strand = handle_int_field(row, "strand", errors, index),
                                    nProbesCr = handle_int_field(row, "nProbesCr", errors, index),
                                    nProbesAf = handle_int_field(row, "nProbesAf", errors, index),
                                    logR =  handle_decimal_field(row, "logR", errors, index),
                                    baf = handle_decimal_field(row, "baf", errors, index),
                                    nAraw = handle_decimal_field(row, "nAraw", errors, index),
                                    nBraw = handle_decimal_field(row, "nBraw", errors, index),
                                    nMajor = handle_int_field(row, "nMajor", errors, index),
                                    nMinor = handle_int_field(row, "nMinor", errors, index),
                                    purifiedLogR = handle_decimal_field(row, "purifiedLogR", errors, index),
                                    purifiedBaf = handle_decimal_field(row, "purifiedBaf", errors, index),
                                    purifiedLoh = handle_decimal_field(row, "purifiedLoh", errors, index),
                                    CNstatus = handle_string_field(row, "CNstatus", errors, index),
                                    LOHstatus = handle_string_field(row, "LOHstatus", errors, index),
                                    minPurifiedLogR=handle_decimal_field(row, "minPurifiedLogR", errors, index),
                                    maxPurifiedLogR = handle_decimal_field(row, "maxPurifiedLogR", errors, index),
                                    breaksInGene = handle_string_field(row, "breaksInGene", errors, index),
                                )

                                rec.save()
                            except KeyError as e:
                                errors.add("Field not found: "+str(e), " in row "+str(index))
                            except Exception as e:
                                errors.add(str(e), " in row "+str(index))
                            finally:
                                index += 1

            print("Imported", str(index), "records.", file=sys.stderr, flush=True)

        if len(errors) > 0:
            print("\nEncountered errors:\n", errors, file=sys.stderr, flush=True)
        else:
            print("\nDone", file=sys.stderr, flush=True)

        if kwargs["deletesnvs"]:
            SomaticVariant.objects.all().delete()

        if kwargs["deletecnas"]:
            CopyNumberAlteration.objects.all().delete()
