from django.core.management.base import BaseCommand
from faker import Faker

from clin_overview.models import ClinicalData, TimelineRecord
from clin_overview.tests.utils import Provider, create_data
import pandas as pd


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

    def handle(self, *args, **kwargs):
        print("." * 100)
        def handle_boolean_field(value, field=None, default=False,):
            if str(value).lower() in ["yes", "t"]:
                return True
            elif str(value).lower() in ["no", "f"]:
                return False
            else:
                return None if field is None or field.__dict__["field"].null else default

        def handle_float_field(value):
            return None if pd.isna(value) else (value if type(value) == float else float(str(value).replace(",", ".")))

        def handle_string_field(value):
            return None if pd.isna(value) else value

        def handle_int_field(value):
            return None if pd.isna(value) else value

        # for i in range(kwargs["num_samples"]):
        #     ClinicalData.objects.create(patient=f"patient{i}", **create_data(fake))

        cl = pd.read_csv(kwargs["clinical_filepath"], sep=";", encoding='utf-8')

        for index, row in cl.iterrows():
            try:
                rec, created = ClinicalData.objects.get_or_create(
                    patient_id                                    = handle_int_field(row["patient_id"]),
                    followup_time                                 = handle_int_field(row["followup_time"]),
                    platinum_free_interval_at_update              = handle_int_field(row["platinum_free_interval_at_update"]),
                    platinum_free_interval                        = handle_int_field(row["platinum_free_interval"]),
                    days_to_progression                           = handle_int_field(row["days_to_progression"]),
                    days_from_beva_maintenance_end_to_progression = handle_int_field(row["days_from_beva_maintenance_end_to_progression"]),
                    days_to_death                                 = handle_int_field(row["days_to_death"]),
                    age_at_diagnosis                              = handle_int_field(row["age_at_diagnosis"]),


                    height_at_diagnosis                           = handle_float_field(row["height_at_diagnosis"]),
                    weight_at_diagnosis                           = handle_float_field(row["weight_at_diagnosis"]),
                    bmi_at_diagnosis                              = handle_float_field(row["bmi_at_diagnosis"]),


                    cohort_code                                   = handle_string_field(row["cohort_code"]),
                    chronic_illnesses_type                        = handle_string_field(row["chronic_illnesses_type"]),
                    histology                                     = handle_string_field(row["histology"]),
                    stage                                         = handle_string_field(row["stage"]),
                    primary_therapy_outcome                       = handle_string_field(row["primary_therapy_outcome"]),
                    survival                                      = handle_string_field(row["survival"]),
                    treatment_strategy                            = handle_string_field(row["treatment_strategy"]),
                    previous_cancer_diagnosis                     = handle_string_field(row["previous_cancer_diagnosis"]),
                    residual_tumor_pds                            = handle_string_field(row["residual_tumor_pds"]),
                    residual_tumor_ids                            = handle_string_field(row["residual_tumor_ids"]),
                    brca_mutation_status                          = handle_string_field(row["brca_mutation_status"]),
                    hr_signature_pretreatment_wgs                 = handle_string_field(row["hr_signature_pretreatment_wgs"]),
                    hr_signature_per_patient                      = handle_string_field(row["hr_signature_per_patient"]),
                    hrd_myriad_status                             = handle_string_field(row["hrd_myriad_status"]),
                    maintenance_therapy                           = handle_string_field(row["maintenance_therapy"]),
                    current_treatment_phase                       = handle_string_field(row["current_treatment_phase"]),
                    drug_trial_name                               = handle_string_field(row["drug_trial_name"]),
                    germline_pathogenic_variant                   = handle_string_field(row["germline_pathogenic_variant"]),


                    chronic_illnesses_at_dg                       = handle_boolean_field(row["chronic_illnesses_at_dg"], ClinicalData.chronic_illnesses_at_dg),
                    previous_cancer                               = handle_boolean_field(row["previous_cancer"], ClinicalData.previous_cancer),
                    progression                                   = handle_boolean_field(row["progression"], ClinicalData.progression),
                    operation1_cancelled                          = handle_boolean_field(row["operation1_cancelled"], ClinicalData.operation1_cancelled),
                    wgs_available                                 = handle_boolean_field(row["wgs_available"], ClinicalData.wgs_available),
                    operation2_cancelled                          = handle_boolean_field(row["operation2_cancelled"], ClinicalData.operation2_cancelled),
                    debulking_surgery_ids                         = handle_boolean_field(row["debulking_surgery_ids"], ClinicalData.debulking_surgery_ids),
                    sequencing_available                          = handle_boolean_field(row["sequencing_available"], ClinicalData.sequencing_available),
                    paired_fresh_samples_available                = handle_boolean_field(row["paired_fresh_samples_available"], ClinicalData.paired_fresh_samples_available),
                    drug_trial_unblinded                          = handle_boolean_field(row["drug_trial_unblinded"], ClinicalData.drug_trial_unblinded),
                    clinical_trial                                = handle_boolean_field(row["clinical_trial"], ClinicalData.clinical_trial),




                )
                rec.save()
            except Exception as e:
                print(row["patient_id"], e)

        df = pd.read_csv(kwargs["timeline_filepath"], sep=";", encoding='utf-8', dtype={"id": "string",
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

        print(df)

        for index, row in df.iterrows():
            print(f"::: {index} \r")
            try:
                patient = ClinicalData.objects.get(patient_id=row["patient_id"])
            except:
                print("No patient", row["patient_id"], "available in the database")
                continue
                #break
            try:
                rec = TimelineRecord.objects.create(
                    external_record_id      = handle_string_field(row["id"]),
                    patient                 = patient,
                    event                   = handle_string_field(row["event"]),
                    interval                = handle_boolean_field(row["interval"]),
                    ongoing                 = handle_boolean_field(row["ongoing"]),
                    interval_length         = handle_int_field(row["interval_length"]),
                    date_relative           = handle_int_field(row["date_relative"]),
                    interval_end_relative   = handle_int_field(row["interval_end_relative"]),
                    name                    = handle_string_field(row["name"]),
                    result                  = handle_float_field(row["result"]),
                    aux_id                  = handle_float_field(row["aux_id"]),
                    source_system           = handle_string_field(row["source_system"]),
                )
                rec.save()
            except:
                ...



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


