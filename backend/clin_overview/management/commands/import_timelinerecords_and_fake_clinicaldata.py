from django.core.management.base import BaseCommand
from faker import Faker

from clin_overview.models import ClinicalData, TimelineRecord
from clin_overview.tests.utils import Provider, create_data
import pandas as pd


class Command(BaseCommand):
    """Fake data generator for the (initial ad hoc) clinical data model.

    Usage
    -------
        `python manage.py import_timelinerecords_and_fake_clinicaldata -clinicalpath <clinical filepath> -timelinepath <timeline filepath>`
    """

    help = "Import data for the database of clinical records faking patient data using faker."

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
        def handle_boolean_field(value):
            if str(value).lower() in ["yes", "t"]:
                return True
            elif str(value).lower() in ["no", "f"]:
                return False
            else:
                return None

        def handle_float_field(value):
            return None if pd.isna(value) else float(value)

        def handle_string_field(value):
            return None if pd.isna(value) else value

        def handle_int_field(value):
            return None if pd.isna(value) else value

        # for i in range(kwargs["num_samples"]):
        #     ClinicalData.objects.create(patient=f"patient{i}", **create_data(fake))

        fake = True
        if fake:
            fake = Faker()
            fake.add_provider(Provider)
        else:
            cl = pd.read_csv(kwargs["clinical_filepath"], sep=";", encoding='utf-8')

            for index, row in cl.iterrows():
                try:
                    rec = ClinicalData.objects.create(
                        patient                 = handle_int_field(row["Patient ID"]),
                        cohort_code             = handle_string_field(row["cohort_code"]),
                        extra_patient_info      = handle_string_field(row["Patient ID"]),
                        other_diagnosis         = handle_string_field(row["Patient ID"]),
                        chronic_illnesses       = handle_string_field(row["Patient ID"]),
                        other_medication        = handle_string_field(row["Patient ID"]),
                        cancer_in_family        = handle_boolean_field(row["Patient ID"]),
                        # enums
                        cud_histology           = handle_string_field(row["Patient ID"]),
                        disease_origin          = handle_string_field(row["Patient ID"]),
                        cud_stage               = handle_string_field(row["Patient ID"]),
                        cud_primary_therapy_outcome     = handle_string_field(row["Patient ID"]),
                        cud_survival                    = handle_string_field(row["Patient ID"]),
                        cud_treatment_strategy          = handle_string_field(row["Patient ID"]),
                        cud_current_treatment_phase     = handle_string_field(row["Patient ID"]),
                        maintenance_therapy             = handle_string_field(row["Patient ID"]),
                        cud_stage_info                  = handle_string_field(row["Patient ID"]),
                        progression_detection_method    = handle_string_field(row["Patient ID"]),
                        # chemo cycles info
                        primary_chemo_cycles        = handle_string_field(row["Patient ID"]),
                        nact_cycles                 = handle_string_field(row["Patient ID"]),
                        post_ids_cycles             = handle_string_field(row["Patient ID"]),
                        # Dates
                        cud_time_of_diagnosis       = handle_string_field(row["Patient ID"]),
                        primary_operation_date      = handle_string_field(row["Patient ID"]),
                        primary_laprascopy_date     = handle_string_field(row["Patient ID"]),
                        secondary_operation_date    = handle_string_field(row["Patient ID"]),
                        last_followup_visit         = handle_string_field(row["Patient ID"]),
                        next_followup_visit         = handle_string_field(row["Patient ID"]),
                        cud_progression_date        = handle_string_field(row["Patient ID"]),
                        cud_last_primary_chemo      = handle_string_field(row["Patient ID"]),
                        cud_date_of_outcome         = handle_string_field(row["Patient ID"]),
                        cud_date_of_death           = handle_string_field(row["Patient ID"]),
                        maintenance_therapy_end     = handle_string_field(row["Patient ID"]),
                        response_ct_date            = handle_string_field(row["Patient ID"]),
                        # Basic patient info
                        age     = handle_string_field(row["Patient ID"]),
                        height  = handle_string_field(row["Patient ID"]),
                        weight  = handle_string_field(row["Patient ID"]),
                        # aqcuired data from patient
                        has_response_ct         = handle_string_field(row["Patient ID"]),
                        has_ctdna               = handle_string_field(row["Patient ID"]),
                        has_petct               = handle_string_field(row["Patient ID"]),
                        has_wgs                 = handle_string_field(row["Patient ID"]),
                        has_singlecell          = handle_string_field(row["Patient ID"]),
                        has_germline_control    = handle_string_field(row["Patient ID"]),
                        has_paired_freshsample  = handle_string_field(row["Patient ID"]),
                        has_brca_mutation       = handle_string_field(row["Patient ID"]),
                        has_hrd                 = handle_string_field(row["Patient ID"]),
                    )
                    # {
                    #     "patient": "Patient.card..Patient",
                    #     "extra_patient_info": "Attention",
                    #     "other_diagnosis": "Histology.other.diagnosis",
                    #     "chronic_illnesses": "Chronic.illnesses.type",
                    #     "other_medication": "",
                    #     "cancer_in_family": "",
                    #     "cud_histology": "Histology",
                    #     "disease_origin": "",
                    #     "cud_stage": "Stage_FIGO2014",
                    #     "cud_primary_therapy_outcome": "Primary.therapy.outcome",
                    #     "cud_survival": "Survival",
                    #     "cud_current_treatment_strategy": "Treatment.strategy",
                    #     "cud_current_treatment_phase": "Current.phase.of.treatment",
                    #     "maintenance_therapy": "Maintenance.therapy.after.1st",
                    #     "cud_stage_info": "",
                    #     "progression_detection_method": "",
                    #     "primary_chemo_cycles": "Primary.chemotherapy.cycles",
                    #     "nact_cycles": "NACT.cycles",
                    #     "post_ids_cycles": "Post.IDS.chemotherapy.cycles",
                    #     "cud_time_of_diagnosis": "",
                    #     "primary_operation_date": "",
                    #     "primary_laprascopy_date": "",
                    #     "secondary_operation_date": "",
                    #     "last_followup_visit": "",
                    #     "next_followup_visit": "",
                    #     "cud_progression_date": "",
                    #     "cud_last_primary_chemo": "",
                    #     "cud_date_of_death": "",
                    #     "maintenance_therapy_end": "",
                    #     "response_ct_date": "",
                    #     "age": "Age.at.diagnosis",
                    #     "height": "",
                    #     "weight": "",
                    #     "bmi": "BMI.at.diagnosis",
                    #     "has_response_ct": "",
                    #     "has_ctdna": "",
                    #     "has_petct": "",
                    #     "has_wgs": "",
                    #     "has_singlecell": "",
                    #     "has_germline_control": "",
                    #     "has_paired_freshsample": "",
                    #     "has_brca_mutation": "",
                    #     "has_hrd": ""
                    # }
                    rec.save()
                except:
                    ...

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
                patient = ClinicalData.objects.get(patient=row["patient_id"])
            except:
                if fake:
                    patient = ClinicalData.objects.create(patient=row["patient_id"],  **create_data(fake))
                    patient.save()
                else:
                    print("No patient", row["patient_id"], "available in the database")
                    break
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


