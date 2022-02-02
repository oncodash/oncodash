from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator


# Enums for model
class CudStageFIGO2014(models.TextChoices):
    IA = "IA"
    IB = "IB"
    IC1 = "IC1"
    IC2 = "IC2"
    IC3 = "IC3"
    IIA = "IIA"
    IIB = "IIB"
    IIIA1i = "IIIA1i"
    IIIA1ii = "IIIA1ii"
    IIIA2 = "IIIA2"
    IIIB = "IIIB"
    IIIC = "IIIC"
    IVA = "IVA"
    IVB = "IVB"


class CudTreatmentPhase(models.TextChoices):
    PROGRESSION = "PROG", _("Progression")
    FOLLOWUP = "FOLLOWUP", _("Follow.-up")
    PRIMARYCHEMO = "PCHEMO", _("Primary chemotherapy")
    DRUGTRIAL = "DTRIAL", _("Drug trial")
    HORMONAL = "HORMONAL", _("Hormonal treatment")


class CudTreatmentStrategy(models.TextChoices):
    NACT = "NACT", _("Neo-adjuvant chemotherapy")
    PDS = "PDS", _("Primary debulking surgery")


class TissueType(models.TextChoices):
    OVARY = "OVARY", _("Ovary")
    OMENTUM = "OMENTUM", _("Omentum")
    PERITONEUM = "PERITONEUM", _("Peritoneum")
    LYMPHNODE = "LYMPHNODE", _("lymph node")
    MESOTHELIUM = "MESOTHELIUM", _("Mesothelium")
    ASCITES = "ASCITES", _("Ascites")


class CudHistology(models.TextChoices):
    HGSOC = "HGSOC", _("High grade serous ovarian cancer")
    MUCINOUS = "MUCINOUS", _("Mucinous ovarian cancer")
    ENDOMETRIOID = "ENDOMETRIOID", _("Endometrioid")


class CudSurvival(models.TextChoices):
    DEATH_UNKNOWN = "DEATHUNKNOWN", _("Death due to unknown reason")
    DEATH_CANCER = "DEATHCANCER", _("Death due to cancer")
    ALIVE = "ALIVE", _("Alive")


class CudPrimaryTherapyOutcome(models.TextChoices):
    PARTIAL = "PARTIAL", _("Partial response")
    COMPLETE = "COMPLETE", _("Complete response")
    PROGRESSIVE = "PROGRESSIVE", _("Progressive disease")
    DEATH = "DEATH", _("Death during therapy")
    UNKNOWN = "UNKNOWN", _("Unknown response")
    STOPPED = "STOPPED", _("Stopped")
    STOPPED_SIDEFFECTS = "SIDEEFFECTSTOP", _("Stopped due to side effects")


class MainetenaceTherapy(models.TextChoices):
    NOMAINTENANCE = "NOMAINTENCANCE", _("No maintenance therapy")
    BEVACIZUMAB = "BEVACIZUMAB", _("Bevacizumab")
    PARPI = "PARPI", _("PARP inhibition therapy")


class ClinicalData(models.Model):
    patient = models.CharField(max_length=100, unique=True)
    extra_patient_info = models.CharField(max_length=400, blank=True)
    other_diagnosis = models.CharField(max_length=100, blank=True)
    chronic_illnesses = models.CharField(max_length=100, blank=True)
    other_medication = models.CharField(max_length=100, blank=True)
    cancer_in_family = models.CharField(max_length=100, blank=True)

    # enums
    cud_histology = models.CharField(
        max_length=20, choices=CudHistology.choices, blank=False
    )

    disease_origin = models.CharField(
        max_length=20, choices=TissueType.choices, blank=True
    )

    cud_stage = models.CharField(
        max_length=7, choices=CudStageFIGO2014.choices, blank=True
    )

    cud_primary_therapy_outcome = models.CharField(
        max_length=20, choices=CudPrimaryTherapyOutcome.choices, blank=True
    )

    cud_survival = models.CharField(
        max_length=15, choices=CudSurvival.choices, blank=False
    )

    cud_treatment_strategy = models.CharField(
        max_length=4, choices=CudTreatmentStrategy.choices
    )

    cud_current_treatment_phase = models.CharField(
        max_length=10, choices=CudTreatmentPhase.choices, blank=True
    )

    maintenace_therapy = models.CharField(
        max_length=25, choices=MainetenaceTherapy.choices, blank=True
    )

    # extra info related to the enums
    cud_stage_info = models.CharField(max_length=200, blank=True)
    progression_detection_method = models.CharField(max_length=100, blank=True)

    # chemo cycles info
    primary_chemo_cycles = models.PositiveIntegerField(null=True)
    nact_cycles = models.PositiveIntegerField(null=True)
    post_ids_cycles = models.PositiveIntegerField(null=True)

    # Dates
    primary_laprascopy_date = models.DateTimeField(auto_now_add=False, blank=True)
    primary_operation_date = models.DateTimeField(auto_now_add=False, blank=True)
    secondary_operation_date = models.DateTimeField(auto_now_add=False, blank=True)
    last_followup_visit = models.DateTimeField(auto_now_add=False, blank=True)
    next_followup_visit = models.DateTimeField(auto_now_add=False, blank=True)
    cud_time_of_diagnosis = models.DateTimeField(auto_now_add=False)
    cud_progression_date = models.DateTimeField(auto_now_add=False, blank=True)
    cud_last_primary_chemo = models.DateTimeField(auto_now_add=False, blank=True)
    cud_date_of_outcome = models.DateTimeField(auto_now_add=False)
    cud_date_of_death = models.DateTimeField(auto_now_add=False, blank=True)
    maintenance_therapy_end = models.DateTimeField(auto_now_add=False, blank=True)
    response_ct_date = models.DateTimeField(auto_now_add=False, blank=True)

    # Basic patient info
    age = models.PositiveIntegerField(validators=[MaxValueValidator(150)])
    height = models.PositiveIntegerField(validators=[MaxValueValidator(250)])  # cm
    weight = models.FloatField(validators=[MinValueValidator(0)])
    bmi = models.FloatField(validators=[MinValueValidator(0)])

    # aqcuired data from patient
    has_response_ct = models.BooleanField(default=False)
    has_ctdna = models.BooleanField(default=False)
    has_petct = models.BooleanField(default=False)
    has_wgs = models.BooleanField(default=False)
    has_singlecell = models.BooleanField(default=False)
    has_germline_control = models.BooleanField(default=False)
    has_paired_freshsample = models.BooleanField(default=False)
    has_brca_mutation = models.BooleanField(default=False)
    has_hrd = models.BooleanField(default=False)
