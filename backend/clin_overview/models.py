from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q
import random
import json

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
    PROGRESSION = "PROGRESSION", _("Progression")
    FOLLOWUP = "FOLLOWUP", _("Follow-up")
    PRIMARYCHEMO = "PRIMARYCHEMO", _("Primary chemotherapy")
    DRUGTRIAL = "DRUGTRIAL", _("Drug trial")
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
    STOPPED = "STOPPED", _("Stopped")
    STOPPED_SIDEFFECTS = "SIDEEFFECTSTOP", _("Stopped due to side effects")
    UNKNOWN = "UNKNOWN", _("Unknown response")


class MainetenaceTherapy(models.TextChoices):
    NOMAINTENANCE = "NOMAINTENANCE", _("No maintenance therapy")
    BEVACIZUMAB = "BEVACIZUMAB", _("Bevacizumab")
    PARPI = "PARPI", _("PARP inhibition therapy")

def randomVector(n, a = 10, b = 0):
    vec = []
    for i in range(n):
        rand = random.random() * a + b - a / 2
        rand = round(rand)
        if (rand < 0):
            rand = 0
        vec.append(rand)
    
    return vec


    # /** Create a vector of incremental integers of length n
    #  *
    #  * @param n length
    #  * @returns vector
    #  */
def getXOfLength(n):
    return [i for i in range(n)]

    # /** Create fake time series
    #  *
    #  * @returns Object{'name': [...]}
    #  */
def fetchTimeSeries(): 
    n = 100
    time_series = {
        "Temperature_[°C]": {
            'x': getXOfLength(n),
            'y': randomVector(n, 6, 36),
            'colors': [
                "rgba(198, 198, 45, 1)",
                
                "rgba(255, 255, 255, 1)",
                "rgba(250, 255, 0, 1)",
            ],
            'thresholds': [35, 37],
        },
        "Blood_Pressure_[mmHg]": {
            'x': getXOfLength(n),
            'y': randomVector(n, 50, 100),
            'colors': [
                "rgba(165, 128, 54, 1)",
                
                "rgba(255, 255, 255, 1)",
                "rgba(255, 131, 0, 1)",
            ],
            'thresholds': [80, 120],
        },
        "CA12-5_[units/mL]": {
            'x': getXOfLength(n),
            'y': randomVector(n, 16000, 7500),
            'colors': [
                "rgba(54, 150, 165, 1)",
                
                "rgba(255, 255, 255, 1)",
                "rgba(0, 242, 255, 1)",
            ],
            'thresholds': [35, 15000],
        },
        "Hemoglobin_[g/L]": {
            'x': getXOfLength(n),
            'y': randomVector(n, 90, 155),
            'colors': [
                "rgba(165, 54, 134, 1)",
                
                "rgba(255, 255, 255, 1)",
                "rgba(255, 0, 106, 1)",
            ],
            'thresholds': [117, 155],
        },
        'Platelets': {
            'x': getXOfLength(n),
            'y': randomVector(n, 300, 225),
            'colors': [
                "rgba(165, 121, 54, 1)",
                
                "rgba(255, 255, 255, 1)",
                "rgba(255, 123, 0,1)",
            ],
            'thresholds': [150, 350],
        }
    }    
    return json.dumps(time_series)


class ClinicalData(models.Model):
    patient = models.CharField(max_length=100, unique=True)
    extra_patient_info = models.CharField(max_length=400, blank=True)
    other_diagnosis = models.CharField(max_length=100, blank=True)
    chronic_illnesses = models.CharField(max_length=100, blank=True)
    other_medication = models.CharField(max_length=100, blank=True)
    cancer_in_family = models.CharField(max_length=100, blank=True)
    time_series = models.TextField(default=fetchTimeSeries)

    # enums
    cud_histology = models.CharField(max_length=20, choices=CudHistology.choices)

    disease_origin = models.CharField(
        max_length=20, choices=TissueType.choices, blank=True
    )

    cud_stage = models.CharField(max_length=20, choices=CudStageFIGO2014.choices)

    cud_primary_therapy_outcome = models.CharField(
        max_length=20, choices=CudPrimaryTherapyOutcome.choices, blank=True
    )

    cud_survival = models.CharField(max_length=20, choices=CudSurvival.choices)

    cud_treatment_strategy = models.CharField(
        max_length=20, choices=CudTreatmentStrategy.choices
    )

    cud_current_treatment_phase = models.CharField(
        max_length=20, choices=CudTreatmentPhase.choices
    )

    maintenance_therapy = models.CharField(
        max_length=25, choices=MainetenaceTherapy.choices
    )

    # extra info related to the enums
    cud_stage_info = models.CharField(max_length=200, blank=True)
    progression_detection_method = models.CharField(max_length=100, blank=True)

    # chemo cycles info
    primary_chemo_cycles = models.PositiveIntegerField(null=True)
    nact_cycles = models.PositiveIntegerField(null=True)
    post_ids_cycles = models.PositiveIntegerField(null=True)

    # Dates
    cud_time_of_diagnosis = models.DateTimeField(blank=True, null=True)
    primary_operation_date = models.DateTimeField(blank=True, null=True)
    primary_laprascopy_date = models.DateTimeField(blank=True, null=True)
    secondary_operation_date = models.DateTimeField(blank=True, null=True)
    last_followup_visit = models.DateTimeField(blank=True, null=True)
    next_followup_visit = models.DateTimeField(blank=True, null=True)
    cud_progression_date = models.DateTimeField(blank=True, null=True)
    cud_last_primary_chemo = models.DateTimeField(blank=True, null=True)
    cud_date_of_outcome = models.DateTimeField(blank=True, null=True)
    cud_date_of_death = models.DateTimeField(blank=True, null=True)
    maintenance_therapy_end = models.DateTimeField(blank=True, null=True)
    response_ct_date = models.DateTimeField(blank=True, null=True)

    # Basic patient info
    age = models.PositiveIntegerField(validators=[MaxValueValidator(150)])
    height = models.PositiveIntegerField(validators=[MaxValueValidator(250)])  # cm
    weight = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(300.0)]
    )

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

    @property
    def bmi(self):
        return self.weight / (self.height**2)

    def __str__(self):
        return self.patient

    # timeline:
    # 1.lapra, 2.diag, 3.oper1, 4.last-pchemo, 5. maintenance
    #                           4.last-follow, 5. next-followup
    #                                          5. oper2 6.prog, 7.out, 8.death
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(primary_laprascopy_date__lt=F("cud_time_of_diagnosis")),
                name="lapra-constraint1",
            ),
            models.CheckConstraint(
                check=Q(cud_time_of_diagnosis__lt=F("primary_operation_date")),
                name="diagnosis-constraint1",
            ),
            models.CheckConstraint(
                check=Q(primary_operation_date__lt=F("cud_last_primary_chemo")),
                name="operation-constraint1",
            ),
            models.CheckConstraint(
                check=Q(primary_operation_date__lt=F("secondary_operation_date")),
                name="operation-constraint2",
            ),
            models.CheckConstraint(
                check=Q(primary_operation_date__lt=F("last_followup_visit")),
                name="followup-constraint1",
            ),
            models.CheckConstraint(
                check=Q(last_followup_visit__lt=F("next_followup_visit")),
                name="followup-constraint2",
            ),
            models.CheckConstraint(
                check=Q(cud_last_primary_chemo__lt=F("maintenance_therapy_end")),
                name="maintenance-constraint1",
            ),
            models.CheckConstraint(
                check=Q(maintenance_therapy_end__lt=F("cud_progression_date")),
                name="progression-constraint1",
            ),
            models.CheckConstraint(
                check=Q(cud_progression_date__lt=F("cud_date_of_death")),
                name="outcome-constraint1",
            ),
            models.CheckConstraint(
                check=Q(cud_date_of_outcome__lt=F("cud_date_of_death")),
                name="outcome-constraint2",
            ),
        ]
