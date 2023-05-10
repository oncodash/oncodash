from django.core.management.base import BaseCommand

from clin_overview.models import ClinicalData, TimelineRecord
import pandas as pd
import csv
import sys

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


class Command(BaseCommand):
    """Import clinical data and timeline records to populate corresponding models.

    Usage
    -------
        `python manage.py import_timelinerecords_and_clinicaldata -clinicalpath <clinical filepath> -timelinepath <timeline filepath>`
    """

    help = "Import data for the database of clinical records and clinical data."

    def add_arguments(self, parser):
        parser.add_argument(
            "-clinicalpath",
            "--clinical_filepath",
            type=str,
            required=True,
            help="File to import clinical data",
        )
        parser.add_argument(
            "-timelinepath",
            "--timeline_filepath",
            type=str,
            required=True,
            help="File to import timeline data",
        )
        parser.add_argument(
            "-d",
            "--errors-details",
            action='store_true',
            help="Show the details of all import errors/warnings (like row numbers)",
        )

    print("Import clinical data...", file=sys.stderr, flush=True)
    def handle(self, *args, **kwargs):
        # print("." * 100)
        def handle_boolean_field(row, field_name, errors, index, field=None, default=False):
            if field_name not in row:
                errors.add("Field '"+field_name+"'expected but not found")
                return None
            value = row[field_name]
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

        def handle_float_field(row, field_name, errors, index):
            if field_name not in row:
                errors.add("Field '"+field_name+"' expected but not found")
                return None
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
            # return None if pd.isna(value) else (value if type(value) == float else float(str(value).replace(",", ".")))

        def handle_string_field(row, field_name, errors, index):
            if field_name not in row:
                errors.add("Field '"+field_name+"' expected but not found")
                return None
            value = row[field_name]
            return None if pd.isna(value) else value

        def handle_int_field(row, field_name, errors, index):
            if field_name not in row:
                errors.add("Field '"+field_name+"' expected but not found")
                return None
            value = row[field_name]
            return None if pd.isna(value) else value

        # for i in range(kwargs["num_samples"]):
        #     ClinicalData.objects.create(patient=f"patient{i}", **create_data(fake))

        cl = pd.read_csv(kwargs["clinical_filepath"], sep=',', encoding='utf-8', quoting=csv.QUOTE_MINIMAL, quotechar='"')

        errors = ErrorSet(kwargs["errors_details"])

        for index, row in cl.iterrows():
            print(f"{index} /",cl.shape[0], end="\r", file=sys.stderr, flush=True)
            try:
                rec, created = ClinicalData.objects.get_or_create(
                    patient_id                                    = handle_int_field(row,"patient_id", errors, index),
                    followup_time                                 = handle_int_field(row,"followup_time", errors, index),
                    platinum_free_interval_at_update              = handle_int_field(row,"platinum_free_interval_at_update", errors, index),
                    platinum_free_interval                        = handle_int_field(row,"platinum_free_interval", errors, index),
                    days_to_progression                           = handle_int_field(row,"days_to_progression", errors, index),
                    days_from_beva_maintenance_end_to_progression = handle_int_field(row,"days_from_beva_maintenance_end_to_progression", errors, index),
                    days_to_death                                 = handle_int_field(row,"days_to_death", errors, index),
                    age_at_diagnosis                              = handle_int_field(row,"age_at_diagnosis", errors, index),


                    height_at_diagnosis                           = handle_float_field(row,"height_at_diagnosis", errors, index),
                    weight_at_diagnosis                           = handle_float_field(row,"weight_at_diagnosis", errors, index),
                    bmi_at_diagnosis                              = handle_float_field(row,"bmi_at_diagnosis", errors, index),


                    cohort_code                                   = handle_string_field(row,"cohort_code", errors, index),
                    chronic_illnesses_type                        = handle_string_field(row,"chronic_illnesses_type", errors, index),
                    histology                                     = handle_string_field(row,"histology", errors, index),
                    stage                                         = handle_string_field(row,"stage", errors, index),
                    primary_therapy_outcome                       = handle_string_field(row,"primary_therapy_outcome", errors, index),
                    survival                                      = handle_string_field(row,"survival", errors, index),
                    treatment_strategy                            = handle_string_field(row,"treatment_strategy", errors, index),
                    previous_cancer_diagnosis                     = handle_string_field(row,"previous_cancer_diagnosis", errors, index),
                    residual_tumor_pds                            = handle_string_field(row,"residual_tumor_pds", errors, index),
                    residual_tumor_ids                            = handle_string_field(row,"residual_tumor_ids", errors, index),
                    brca_mutation_status                          = handle_string_field(row,"brca_mutation_status", errors, index),
                    hr_signature_pretreatment_wgs                 = handle_string_field(row,"hr_signature_pretreatment_wgs", errors, index),
                    hr_signature_per_patient                      = handle_string_field(row,"hr_signature_per_patient", errors, index),
                    hrd_myriad_status                             = handle_string_field(row,"hrd_myriad_status", errors, index),
                    maintenance_therapy                           = handle_string_field(row,"maintenance_therapy_after_1st_line", errors, index),
                    current_treatment_phase                       = handle_string_field(row,"current_phase_of_treatment", errors, index),
                    drug_trial_name                               = handle_string_field(row,"drug_trial_name", errors, index),
                    germline_pathogenic_variant                   = handle_string_field(row,"germline_pathogenic_variant", errors, index),


                    chronic_illnesses_at_dg                       = handle_boolean_field(row,"chronic_illnesses_at_dg", errors, index, ClinicalData.chronic_illnesses_at_dg),
                    previous_cancer                               = handle_boolean_field(row,"previous_cancer", errors, index, ClinicalData.previous_cancer),
                    progression                                   = handle_boolean_field(row,"progression", errors, index, ClinicalData.progression),
                    operation1_cancelled                          = handle_boolean_field(row,"operation1_cancelled", errors, index, ClinicalData.operation1_cancelled),
                    wgs_available                                 = handle_boolean_field(row,"wgs_available", errors, index, ClinicalData.wgs_available),
                    operation2_cancelled                          = handle_boolean_field(row,"operation2_cancelled", errors, index, ClinicalData.operation2_cancelled),
                    debulking_surgery_ids                         = handle_boolean_field(row,"debulking_surgery_ids", errors, index, ClinicalData.debulking_surgery_ids),
                    sequencing_available                          = handle_boolean_field(row,"sequencing_available", errors, index, ClinicalData.sequencing_available),
                    paired_fresh_samples_available                = handle_boolean_field(row,"paired_fresh_samples_available", errors, index, ClinicalData.paired_fresh_samples_available),
                    drug_trial_unblinded                          = handle_boolean_field(row,"drug_trial_unblinded", errors, index, ClinicalData.drug_trial_unblinded),
                    clinical_trial                                = handle_boolean_field(row,"clinical_trials_participation", errors, index, ClinicalData.clinical_trial),




                )
                rec.save()
            except Exception as e:
                print("When importing patient", row["patient_id"], "the following error occured:", e, sys.exc_info()[0], file=sys.stderr, flush=True)

        if len(errors) > 0:
            print("\nEncountered errors:\n", errors, file=sys.stderr, flush=True)
        else:
            print("\nDone", file=sys.stderr, flush=True)


        print("Import timeline data...", file=sys.stderr, flush=True)

        df = pd.read_csv(kwargs["timeline_filepath"], sep=",", encoding='utf-8', quoting=csv.QUOTE_MINIMAL, quotechar='"',
                dtype={"id": "string",
                        "patient_id": "string",
                        "cohort_code": "string",
                        "event": "string",
                        "interval": "string",
                        "ongoing": "string",
                        "interval_length": "string",
                        "date_relative": "string",
                        "interval_end_relative": "string",
                        "name": "string",
                        "result": "string",
                        "aux_id": "string",
                        "source_system": "string",
                        })

        # print(df)

        errors = ErrorSet(kwargs["errors_details"])
        for index, row in df.iterrows():
            print(f"{index} /", df.shape[0], end="\r", file=sys.stderr, flush=True)
            assert("patient_id" in row)
            try:
                patient = ClinicalData.objects.get(patient_id=row["patient_id"])
            except:
                errors.add("No timeline data for patient '"+row["patient_id"]+"'")
                continue
            try:
                rec = TimelineRecord.objects.create(
                    external_record_id      = handle_string_field(row,"id", errors, index),
                    patient                 = patient,
                    event                   = handle_string_field(row,"event", errors, index),
                    interval                = handle_boolean_field(row,"interval", errors, index),
                    ongoing                 = handle_boolean_field(row,"ongoing", errors, index),
                    interval_length         = handle_int_field(row,"interval_length", errors, index),
                    date_relative           = handle_int_field(row,"date_relative", errors, index),
                    interval_end_relative   = handle_int_field(row,"interval_end_relative", errors, index),
                    name                    = handle_string_field(row,"name", errors, index),
                    result                  = handle_float_field(row,"result", errors, index),
                    aux_id                  = handle_string_field(row,"aux_id", errors, index),
                    source_system           = handle_string_field(row,"source_system", errors, index),
                )
                rec.save()
            except Exception as e:
                errors.add("Failed to import timeline data with external id '"+handle_string_field(row,"id",errors,index)+"' ; ERROR: "+str(e))
                continue

        if len(errors) > 0:
            print("\nEncountered errors:\n", errors, file=sys.stderr, flush=True)
        else:
            print("\nDone", file=sys.stderr, flush=True)

        # external_record_id = models.IntegerField(unique=True)
        # patient_id = models.ForeignKey(ClinicalData, on_delete=models.CASCADE)
        # cohort_code = models.CharField(max_length=255)
        # event = models.CharField(max_length=255)
        # interval = models.BooleanField()
        # ongoing = models.BooleanField()
        # interval_length = models.IntegerField()
        # date_relative = models.IntegerField()
        # interval_end_relative = models.IntegerField()
        # name = models.CharField(max_length=255)
        # result = models.FloatField()
        # aux_id = models.CharField(max_length=255)
        # source_system = models.CharField(max_length=255)


