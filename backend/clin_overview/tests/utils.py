import random
from django.utils.timezone import make_aware
from typing import Dict
from faker import Faker
from faker.providers import BaseProvider


CUDSTAGE = ["IA", "IB", "IIA", "IIB", "IIIB", "IIIC"]
CUDTREATPHASE = ["PROGRESSION", "FOLLOWUP", "PRIMARYCHEMO", "DRUGTRIAL"]
CUDTREATSTRAT = ["NACT", "PDS"]
TISSUETYPE = ["OVARY", ""]
CUDHISTOLOGY = ["HGSOC", "MUCINOUS", "ENDOMETRIOID"]
CUDSURVIVAL = ["ALIVE"]
CUDTHERAPYOUTCOME = ["PARTIAL", "COMPLETE", "PROGRESSIVE", "STOPPED", ""]
MAINTENANCETHERAPY = ["NOMAINTENANCE", "BEVACIZUMAB", "PARPI"]
CYCLES = [3, 4, 5, 6]


class Provider(BaseProvider):
    def get_cudstage(self) -> str:
        return self.random_element(CUDSTAGE)

    def get_cudphase(self) -> str:
        return self.random_element(CUDTREATPHASE)

    def get_cudstrategy(self) -> str:
        return self.random_element(CUDTREATSTRAT)

    def get_tissuetype(self) -> str:
        return self.random_element(TISSUETYPE)

    def get_cudhistology(self) -> str:
        return self.random_element(CUDHISTOLOGY)

    def get_cudsurvival(self) -> str:
        return self.random_element(CUDSURVIVAL)

    def get_cudoutcome(self) -> str:
        return self.random_element(CUDTHERAPYOUTCOME)

    def get_maintenance(self) -> str:
        return self.random_element(MAINTENANCETHERAPY)

    def get_cycles(self) -> int:
        return self.random_element(CYCLES)


def create_data(fake: Faker) -> Dict:
    """Create one fake data row.

    Args
    ----
        fake (Faker):
            A Faker object

    Returns
    -------
        Dict:
            A Dictionary containing the CLinData model values
    """
    ret_dict = {}

    # enums
    ret_dict["cud_stage"] = fake.get_cudstage()
    ret_dict["cud_current_treatment_phase"] = fake.get_cudphase()
    ret_dict["cud_treatment_strategy"] = fake.get_cudstrategy()
    ret_dict["disease_origin"] = fake.get_tissuetype()
    ret_dict["cud_histology"] = fake.get_cudhistology()
    ret_dict["cud_survival"] = fake.get_cudsurvival()
    ret_dict["cud_primary_therapy_outcome"] = fake.get_cudoutcome()
    ret_dict["maintenance_therapy"] = fake.get_maintenance()

    # cycles
    ret_dict["nact_cycles"] = None
    if ret_dict["cud_treatment_strategy"] == "NACT":
        ret_dict["nact_cycles"] = fake.get_cycles()

    ret_dict["post_ids_cycles"] = None
    if ret_dict["cud_primary_therapy_outcome"] in ("PROGRESSIVE", "PARTIAL"):
        ret_dict["post_ids_cycles"] = fake.get_cycles()

    ret_dict["primary_chemo_cycles"] = fake.get_cycles()

    # dates
    ret_dict["primary_laprascopy_date"] = make_aware(
        fake.date_time_between(start_date="-7y", end_date="-5y")
    )
    ret_dict["cud_time_of_diagnosis"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["primary_laprascopy_date"], end_date="-5y"
        )
    )
    ret_dict["primary_operation_date"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["cud_time_of_diagnosis"], end_date="-4y8m"
        )
    )
    ret_dict["last_followup_visit"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["primary_operation_date"], end_date="-4y"
        )
    )
    ret_dict["cud_last_primary_chemo"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["primary_operation_date"], end_date="-4y"
        )
    )
    ret_dict["next_followup_visit"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["last_followup_visit"], end_date="-2y6m"
        )
    )

    ret_dict["maintenance_therapy_end"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["cud_last_primary_chemo"], end_date="-2y6m"
        )
    )

    ret_dict["secondary_operation_date"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["maintenance_therapy_end"], end_date="-2y"
        )
    )

    ret_dict["cud_date_of_outcome"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["secondary_operation_date"], end_date="-1y"
        )
    )

    ret_dict["cud_progression_date"] = make_aware(
        fake.date_time_between(
            start_date=ret_dict["maintenance_therapy_end"], end_date="-2y6m"
        )
    )

    # free text fields
    ret_dict["extra_patient_info"] = ""
    if random.randint(0, 1):
        ret_dict["extra_patient_info"] = fake.sentence(
            nb_words=5,
            variable_nb_words=True,
            ext_word_list=[
                "simultaneous",
                "cancer",
                "hormonal",
                "malignant",
                "NACT",
                "growth",
            ],
        )

    ret_dict["cud_stage_info"] = ""
    if random.randint(0, 1):
        ret_dict["cud_stage_info"] = fake.sentence(
            nb_words=5,
            variable_nb_words=True,
            ext_word_list=[
                "tumor",
                "biopsy",
                "no",
                "pleural fluid",
                "thorax norm",
                "auxilliary",
            ],
        )

    ret_dict["other_diagnosis"] = ""
    if random.randint(0, 1):
        ret_dict["other_diagnosis"] = fake.word(
            ext_word_list=[
                "breast cancer",
                "renal cancer",
                "lung cancer",
                "leukemia",
            ],
        )

    ret_dict["chronic_illnesses"] = ""
    if random.randint(0, 1):
        ret_dict["chronic_illnesses"] = fake.word(
            ext_word_list=["diabetes", "rheumatic", "gout", "parkinson"],
        )

    ret_dict["other_medication"] = ""
    if random.randint(0, 1):
        ret_dict["other_medication"] = fake.word(
            ext_word_list=["drug1", "drug2", "drug3", "drug4"],
        )

    ret_dict["cancer_in_family"] = ""
    if random.randint(0, 1):
        ret_dict["cancer_in_family"] = fake.word(
            ext_word_list=[
                "Mother leukemia",
                "Dad lung cancer",
                "GG",
                "Aunt melanoma",
            ],
        )

    ret_dict["progression_detection_method"] = ""
    if CUDTREATPHASE == "PROGRESSION":
        ret_dict["progression_detection_method"] = fake.word(
            ext_word_list=["CT", "CA125 > 5" "MRI"],
        )

    ret_dict["has_ctdna"] = random.randint(0, 1)
    ret_dict["has_petct"] = random.randint(0, 1)
    ret_dict["has_wgs"] = random.randint(0, 1)
    ret_dict["has_singlecell"] = random.randint(0, 1)
    ret_dict["has_germline_control"] = random.randint(0, 1)
    ret_dict["has_paired_freshsample"] = random.randint(0, 1)
    ret_dict["has_brca_mutation"] = random.randint(0, 1)
    ret_dict["has_hrd"] = random.randint(0, 1)

    ret_dict["age"] = random.randint(30, 100)
    ret_dict["height"] = random.randint(130, 200)
    ret_dict["weight"] = random.uniform(45.0, 130.0)

    return ret_dict
