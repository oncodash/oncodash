from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q
import random
import json

# Enums for model
class StageFIGO2014(models.TextChoices):
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


class TreatmentPhase(models.TextChoices):
    NEOADJUVANT = "NEOADJUVANT", _("Neoadjuvant")
    PRIMARY_CHEMOTHERAPY = "PRIMARY_CHEMOTHERAPY", _("Primary chemotherapy")
    BMAPTPARPMAPT = "BMAPTPARPMAPT", _("Bev maintenance after primary therapyPARP maintenance after prim therapy")
    IN_DRUG_TRIALIN_DRUG_TRIAL = "IN_DRUG_TRIAL", _("Currently in drug trial")
    HORMONAL_TREATMENT = "HORMONAL_TREATMENT", _("Hormonal treatment")
    FOLLOW_UP = "FOLLOW_UP", _("Follow-up")
    REGULAR_FOLLOWUP_VISITS_ENDED = "REGULAR_FOLLOWUP_VISITS_ENDED", _("Regular follow up visits ended")
    PROGRESSION = "PROGRESSION", _("Progression")
    PARP_MAINTENANCE_AFTER_PROG = "PARP_MAINTENANCE_AFTER_PROG", _("Parp maintenance after prog")
    FOLLOWUP_AFTER_PROG_TREATMENT = "FOLLOWUP_AFTER_PROG_TREATMENT", _("Follow-up after prog treatment")
    PROGRESSION_ACTIVE_TREATMENT_ENDED = "PROGRESSION_ACTIVE_TREATMENT_ENDED", _("Progression, active treatment ended")
    OTHER = "OTHER", _("Other")


class TreatmentStrategy(models.TextChoices):
    NACT = "NACT", _("Neo-adjuvant chemotherapy")
    PDS = "PDS", _("Primary debulking surgery")
    Other = "Other", _("Other")


class TissueType(models.TextChoices):
    OVARY = "OVARY", _("Ovary")
    OMENTUM = "OMENTUM", _("Omentum")
    PERITONEUM = "PERITONEUM", _("Peritoneum")
    LYMPHNODE = "LYMPHNODE", _("lymph node")
    MESOTHELIUM = "MESOTHELIUM", _("Mesothelium")
    ASCITES = "ASCITES", _("Ascites")


class Histology(models.TextChoices):
    HGSOC = "HGSOC", _("High grade serous ovarian cancer")
    MUCINOUS = "MUCINOUS", _("Mucinous ovarian cancer")
    ENDOMETRIOID = "ENDOMETRIOID", _("Endometrioid")


class Survival(models.TextChoices):
    DEATH_UNKNOWN = "DEATHUNKNOWN", _("Death due to unknown reason")
    DEATH_OTHER = "DEATHOTHER", _("Death due to other reason")
    DEATH_CANCER = "DEATHCANCER", _("Death due to cancer")
    ALIVE = "ALIVE", _("Alive")


class PrimaryTherapyOutcome(models.TextChoices):
    PARTIAL = "PARTIAL", _("Partial response")
    COMPLETE = "COMPLETE", _("Complete response")
    PROGRESSIVE = "PROGRESSIVE", _("Progressive disease")
    DEATH = "DEATH", _("Died during chemotherapy")
    PROGRESSIVENACT = "PROGRESSIVENACT", _("Progressive disease after nact")
    STOPPED_SIDEFFECTS = "SIDEEFFECTSTOP", _("Stopped due to side effects")
    STABLENACT = "STABLENACT", _("Stable disease after nact")
    NOCHEMO = "NOCHEMO", _("No chemotherapy")
    STABLE = "STABLE", _("Stable disease")


class MainetenaceTherapy(models.TextChoices):
    NOMAINTENANCE = "NOMAINTENANCE", _("No maintenance therapy")
    BEVACIZUMAB = "BEVACIZUMAB", _("Bevacizumab")
    PARPI = "PARPI", _("PARP inhibition therapy")


class ChronicIllnesses(models.TextChoices):
    ASTMA = "ASTMA", _("Asma")
    ARTHRORISARTRITIS = "ARTHRORISARTRITIS", _("Arthroris/artritis")
    PARPI = "PARPI", _("Flimmer")
    COPD = "COPD", _("COPD")
    COLITISULSEROSA =  "COLITIS ULSEROSA", _("Colitis ulserosa")
    DEPRESSION = "DEPRESSION", _("Depression")
    DIABETESTYPE2 = "DIABETES TYPE2", _("Diabetes type2")
    EPILEPSY ="EPILEPSY", _("Epilepsy")
    FIBROMYALGIA = "FIBROMYALGIA", _("Fibromyalgia")
    GLAUCOMA = "GLAUCOMA", _("Glaucoma")
    HYPERCHOLESTEROLEMIA =  "HYPERCHOLESTEROLEMIA", _("Hypercholesterolemia")
    HYPERTENSION = "HYPERTENSION", _("Hypertension")
    HYPOTHYREOSIS = "HYPOTHYREOSIS", _("Hypothyreosis")
    MCC =  "MCC", _("MCC")
    MYOCARDIALINFARCT = "MYOCARDIAL INFARCT", _("Myocardial infarct")
    OSTEOPOROSIS = "OSTEOPOROSIS", _("Osteoporosis")
    PULMONARYEMBO = "PULMONARY EMBO", _("Pulmonary Embo")
    STROKE = "STROKE", _("Stroke")
    REFLUX = "REFLUX", _("Reflux")
    RENALINSUFFIENCY = "RENAL INSUFFIENCY", _("Renal insuffiency")
    REUMATOIDARTRITIS = "REUMATOID ARTRITIS", _("Reumatoid artritis")
    SCHITZOPHRENIA = "SCHITZOPHRENIA", _("Schitzophrenia")
    VENOUSTROMB = "VENOUS TROMB", _("Venous tromb")
    OTHER = "OTHER", _("Other")


class ResidualTumorPDS(models.TextChoices):
    ZERO = "ZERO", _("0")
    ZEROTEN = "ZEROTEN", _("1 to 10mm")
    OVERTEN = "OVERTEN", _("more than 10mm")


class ResidualTumorIDS(models.TextChoices):
    ZERO = "ZERO", _("0")
    ZEROTEN = "ZEROTEN", _("1 to 10mm")
    OVERTEN = "OVERTEN", _("more than 10mm")


class BRCAMutation(models.TextChoices):
    NOBRCA = "NOBRCA", _("No BRCA mut")
    BRCA1TUMOR = "BRCA1TUMOR", _("BRCA1 in tumor")
    BRCA1BLOOD = "BRCA1BLOOD", _("BRCA1 in blood")
    BRCA2TUMOR = "BRCA2TUMOR", _("BRCA2 in tumor")
    BRCA2BLOOD = "BRCA2BLOOD", _("BRCA2 in blood")


class HRPretreatmentWGS(models.TextChoices):
    HRD = "HRD", _("HRD")
    HRP = "HRP", _("HRP")


class HRPerPatient(models.TextChoices):
    HRD = "HRD", _("HRD")
    HRP = "HRP", _("HRP")


class HRDMyriadStatus(models.TextChoices):
    HRDPOSITIVE = "HRDPOSITIVE", _("HRD positive")
    HRDNEGATIVE = "HRDNEGATIVE", _("HRD negative")


class DrugTrialName(models.TextChoices):
    AVANOVA = "AVANOVA", _("AVANOVA")
    MK3475 = "MK3475", _("MK3475")
    PAOLA = "PAOLA", _("PAOLA")
    PRIMA = "PRIMA", _("PRIMA")
    IMAGYN = "IMAGYN", _("IMAGYN")
    DUOO = "DUOO", _("DUO-O")
    FIRST = "FIRST", _("FIRST")
    EPIKO = "EPIKO", _("EPIK-O")


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
        # "Temperature_[°C]": {
        #     'x': getXOfLength(n),
        #     'y': randomVector(n, 6, 36),
        #     'colors': [
        #         "rgba(198, 198, 45, 1)",
                
        #         "rgba(255, 255, 255, 1)",
        #         "rgba(250, 255, 0, 1)",
        #     ],
        #     'thresholds': [35, 37],
        # },
        # "Blood_Pressure_[mmHg]": {
        #     'x': getXOfLength(n),
        #     'y': randomVector(n, 50, 100),
        #     'colors': [
        #         "rgba(165, 128, 54, 1)",
                
        #         "rgba(255, 255, 255, 1)",
        #         "rgba(255, 131, 0, 1)",
        #     ],
        #     'thresholds': [80, 120],
        # },
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
    patient_id = models.IntegerField(unique=True)
    '''
    "patient_id": {
        "category": "identifier",
        "dataType": "integer",
        "unit": null,
        "notNull": true,
        "listVariable": false,
        "importance": 1,
        "description": "Unique patient identifier",
        "comment": "",
        "originalOvcabaseColumn": "Patient ID",
        "alreadyVisualized": true
    },
    '''

    cohort_code = models.CharField(max_length=255)
    '''
    "cohort_code": {
        "category": "identifier",
        "dataType": "string",
        "unit": null,
        "notNull": true,
        "listVariable": false,
        "importance": 1,
        "description": "Alternative patient identifier",
        "comment": "",
        "originalOvcabaseColumn": "Patient card::Patient cohort code_Patient Card",
        "alreadyVisualized": false
    },
    '''

    # extra_patient_info = models.CharField(max_length=400, blank=True)
    # other_diagnosis = models.CharField(max_length=100, blank=True)

    chronic_illnesses_at_dg = models.BooleanField(null=True)
    '''
    "chronic_illnesses_at_dg": {
            "category": "additional baseline",
            "dataType": "boolean",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 2,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Chronic illnesses at Dg",
            "alreadyVisualized": false
        },
    '''
    chronic_illnesses_type = models.CharField(max_length=100, null=True, choices=ChronicIllnesses.choices)
    '''"chronic_illnesses_type": {
            "category": "additional baseline",
            "dataType": "string",
            "unit": null,
            "notNull": false,
            "listVariable": true,
            "importance": 2,
            "description": "What illnesses patient had at time of diagnosis (from value list)",
            "comment": "",
            "originalOvcabaseColumn": "Chronic illnesses type",
            "alreadyVisualized": false,
            "valueSpace": [
                "Astma",
                "Arthroris/artritis",
                "Flimmer",
                "COPD",
                "Colitis ulserosa",
                "Depression",
                "Diabetes type2",
                "Epilepsy",
                "Fibromyalgia",
                "Glaucoma",
                "Hypercholesterolemia",
                "Hypertension",
                "Hypothyreosis",
                "MCC",
                "Myocardial infarct",
                "Osteoporosis",
                "Pulmonary Embo",
                "Stroke",
                "Reflux",
                "Renal insuffiency",
                "Reumatoid artritis",
                "Schitzophrenia",
                "Venous tromb",
                "Other"
            ]
        },
    '''
    # other_medication = models.CharField(max_length=100, blank=True)
    # cancer_in_family = models.CharField(max_length=100, blank=True)
    time_series = models.CharField(max_length=255*20, blank=True, null= True)
    event_series = models.CharField(max_length=255*20, blank=True, null= True)

    # enums
    histology = models.CharField(max_length=20, choices=Histology.choices)
    '''
    "histology": {
        "category": "baseline",
        "dataType": "string",
        "unit": null,
        "notNull": true,
        "listVariable": false,
        "importance": 1,
        "description": "",
        "comment": "Are other values than high-grade serous even needed here or should they be filtered out?: Let\u00b4s filter them out",
        "originalOvcabaseColumn": "CUD_Histology",
        "alreadyVisualized": true,
        "valueSpace": [
            "high grade serous"
        ]
    },
    '''

    #disease_origin = models.CharField(max_length=20, choices=TissueType.choices, blank=True)

    stage = models.CharField(max_length=20, null=True, choices=StageFIGO2014.choices)
    ''' 
        "stage": {
            "category": "baseline",
            "dataType": "string",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "FIGO2014 classification of disease spread at diagnosis",
            "comment": "",
            "originalOvcabaseColumn": "CUD_Stage_FIGO2014",
            "alreadyVisualized": true,
            "valueSpace": [
                "IA",
                "IB",
                "IC1",
                "IC2",
                "IC3",
                "IIA",
                "IIB",
                "IIIA1",
                "IIIA2",
                "IIIB",
                "IIIC",
                "IVA",
                "IVB"
            ]
        },
        '''

    primary_therapy_outcome = models.CharField(max_length=20, null=True, choices=PrimaryTherapyOutcome.choices) # The field is missing sometimes
    '''
    "primary_therapy_outcome": {
            "category": "outcome",
            "dataType": "string",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "RECIST class of primary therapy outcome",
            "comment": "",
            "originalOvcabaseColumn": "CUD_Primary therapy outcome",
            "alreadyVisualized": true,
            "valueSpace": [
                "progressive disease",
                "complete response",
                "partial response",
                "progressive disease after nact",
                "stable disease after nact",
                "died during chemotherapy",
                "stopped due to side effects",
                "no chemotherapy",
                "stable disease"
            ]
        },
    '''
    survival = models.CharField(max_length=20, choices=Survival.choices)
    '''
        "survival": {
            "category": "outcome",
            "dataType": "string",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "CUD_Survival",
            "alreadyVisualized": true,
            "valueSpace": [
                "alive",
                "death due to cancer",
                "death due to other reason",
                "death reason unknown"
            ]
        },
        '''

    treatment_strategy = models.CharField(max_length=20, choices=TreatmentStrategy.choices)
    '''
    "treatment_strategy": {
            "category": "baseline",
            "dataType": "string",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "",
            "comment": "Other means either palliative or atypical. Mostly PDS or NACT",
            "originalOvcabaseColumn": "CUD_Treatment strategy",
            "alreadyVisualized": true,
            "valueSpace": [
                "PDS",
                "NACT",
                "Other"
            ]
        },
        '''

    '''
    "current_phase_of_treatment": {
        "category": "treatment",
        "dataType": "string",
        "unit": NaN,
        "notNull": false,
        "listVariable": false,
        "importance": 2,
        "description": NaN,
        "comment": "String of free-text treatment info",
        "originalOvcabaseColumn": "Current phase of treatment",
        "alreadyVisualized": false,
        "valueSpace": "['Neoadjuvant','Primary chemotherapy','Bev maintenance after primary therapy','PARP maintenance after prim therapy','Currently in drug trial','Hormonal treatment','Follow-up','Regular follow up visits ended','Progression','Parp maintenance after prog','Follow-up after prog treatment','Progression, active treatment ended','Other']"
    }
    '''
    current_treatment_phase = models.CharField(max_length=100, null=True, blank=True, choices=TreatmentPhase.choices)

    '''
    "maintenance_therapy_after_1st_line": {
        "category": "treatment",
        "dataType": "string",
        "unit": NaN,
        "notNull": false,
        "listVariable": false,
        "importance": 3,
        "description": "String of free-text treatment info",
        "comment": NaN,
        "originalOvcabaseColumn": "Maintenance therary after 1st line",
        "alreadyVisualized": false,
        "valueSpace": NaN
    },
    '''
    maintenance_therapy = models.CharField(max_length=2000, null=True, blank=True)
    '''
    "clinical_trials_participation": {
        "category": "clinical_trial",
        "dataType": "boolean",
        "unit": NaN,
        "notNull": false,
        "listVariable": false,
        "importance": 3,
        "description": "Participation in any clinical trials",
        "comment": NaN,
        "originalOvcabaseColumn": "DrugTr Participation in clinical trials",
        "alreadyVisualized": false,
        "valueSpace": NaN
    }
    '''
    clinical_trial = models.BooleanField(null=True)

    '''
    "drug_trial_unblinded": {
        "category": "clinical_trial",
        "dataType": "boolean",
        "unit": NaN,
        "notNull": false,
        "listVariable": false,
        "importance": 3,
        "description": "Drug / placebo unblinding",
        "comment": "True or null",
        "originalOvcabaseColumn": "Drugtrial unblinded",
        "alreadyVisualized": false,
        "valueSpace": NaN
    }
    '''
    drug_trial_unblinded = models.BooleanField(null=True)

    '''
    "drug_trial_name": {
        "category": "clinical_trial",
        "dataType": "string",
        "unit": NaN,
        "notNull": false,
        "listVariable": false,
        "importance": 3,
        "description": "The clinical trial the patient has participated",
        "comment": NaN,
        "originalOvcabaseColumn": "DrugTrial name",
        "alreadyVisualized": false,
        "valueSpace": "['AVANOVA', 'MK 3475', 'PAOLA', 'PRIMA', 'IMAGYN', 'DUO-O', 'FIRST', 'EPIK-O]'"
    }
    '''
    drug_trial_name = models.CharField(max_length=2000, null=True, blank=True, choices=DrugTrialName.choices)


    # extra info related to the enums
    # progression_detection_method = models.CharField(max_length=100, blank=True)

    # chemo cycles info
    # primary_chemo_cycles = models.PositiveIntegerField(null=True)
    # nact_cycles = models.PositiveIntegerField(null=True)
    # post_ids_cycles = models.PositiveIntegerField(null=True)

    # Dates
    followup_time = models.IntegerField(null=True)
    '''
    "followup_time": {
            "category": "outcome",
            "dataType": "integer",
            "unit": "day",
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "CUD_Follow up time_months from Dg alive",
            "alreadyVisualized": false
        },
    '''

    platinum_free_interval_at_update = models.IntegerField(null=True)
    '''
            "platinum_free_interval_at_update": {
            "category": "outcome",
            "dataType": "integer",
            "unit": "day",
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "Lower limit of platinum free interval, which is equal to time from last day of primary therapy to followup, if not relapsed",
            "comment": "Null, if progressed",
            "originalOvcabaseColumn": "PFI at outcome update when no prog",
            "alreadyVisualized": false
        },
    '''

    platinum_free_interval = models.IntegerField(null=True)
    '''
    "platinum_free_interval": {
            "category": "outcome",
            "dataType": "integer",
            "unit": "day",
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "Time from last day of primary therapy to progression",
            "comment": "Null, if not progressed",
            "originalOvcabaseColumn": "CUD_Platinum free interval days if Prog",
            "alreadyVisualized": false
        },
    '''

    days_to_progression = models.IntegerField(null=True)
    '''
    "days_to_progression": {
            "category": "outcome",
            "dataType": "integer",
            "unit": "day",
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "Days from diagnosis to first progression",
            "comment": "Also in timeline dataset, event \"primary_progression\", is this needed here?",
            "originalOvcabaseColumn": "CUD_Time to progression_days",
            "alreadyVisualized": false
        },
    '''

    days_from_beva_maintenance_end_to_progression = models.IntegerField(null=True)
    '''
    "days_from_beva_maintenance_end_to_progression": {
            "category": "outcome",
            "dataType": "integer",
            "unit": "day",
            "notNull": false,
            "listVariable": false,
            "importance": 2,
            "description": "Days from end of bevacizumab maintenance end to progression",
            "comment": "",
            "originalOvcabaseColumn": "TFIbev Time from end of beva maintenance to prog",
            "alreadyVisualized": false
        },
    '''

    days_to_death = models.IntegerField(null=True)
    '''
    "days_to_death": {
                "category": "outcome",
                "dataType": "integer",
                "unit": "day",
                "notNull": false,
                "listVariable": false,
                "importance": 1,
                "description": "Days from diagnosis to death",
                "comment": "Also in timeline dataset, event \"death\", is this needed here?",
                "originalOvcabaseColumn": "CUD_Time to death_days",
                "alreadyVisualized": false
            },    
    '''

    # time_of_diagnosis = models.DateTimeField(blank=True, null=True)
    # primary_operation_date = models.DateTimeField(blank=True, null=True)
    # primary_laprascopy_date = models.DateTimeField(blank=True, null=True)
    # secondary_operation_date = models.DateTimeField(blank=True, null=True)
    # last_followup_visit = models.DateTimeField(blank=True, null=True)
    # next_followup_visit = models.DateTimeField(blank=True, null=True)
    # progression_date = models.DateTimeField(blank=True, null=True)
    # last_primary_chemo = models.DateTimeField(blank=True, null=True)
    # date_of_outcome = models.DateTimeField(blank=True, null=True)
    # date_of_death = models.DateTimeField(blank=True, null=True)
    # maintenance_therapy_end = models.DateTimeField(blank=True, null=True)
    # response_ct_date = models.DateTimeField(blank=True, null=True)

    # Basic patient info
    age_at_diagnosis = models.PositiveIntegerField(validators=[MaxValueValidator(150)])
    '''
    "age_at_diagnosis": {
            "category": "baseline",
            "dataType": "float",
            "unit": "year",
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Age at Diagnosis",
            "alreadyVisualized": true
        },
    '''
    height_at_diagnosis = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(300.0)])
    '''
    "height_at_diagnosis": {
            "category": "baseline",
            "dataType": "float",
            "unit": "meter",
            "notNull": true,
            "listVariable": false,
            "importance": 2,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Height at dg",
            "alreadyVisualized": false
        },
    '''
    weight_at_diagnosis = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(500.0)])
    '''
    "weight_at_diagnosis": {
            "category": "baseline",
            "dataType": "float",
            "unit": "kilogram",
            "notNull": true,
            "listVariable": false,
            "importance": 2,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Weight at dg",
            "alreadyVisualized": false
        },
    '''
    bmi_at_diagnosis = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    '''
    "bmi_at_diagnosis": {
        "category": "baseline",
        "dataType": "float",
        "unit": "kilogram / meter / meter",
        "notNull": true,
        "listVariable": false,
        "importance": 2,
        "description": "Body mass index at diagnosis",
        "comment": "",
        "originalOvcabaseColumn": "BMI at Dg",
        "alreadyVisualized": true
    },
    '''

    # Acquired data from patient
    previous_cancer = models.BooleanField(null=True)
    '''
    "previous_cancer": {
            "category": "additional baseline",
            "dataType": "boolean",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 2,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Previous cancer yes no",
            "alreadyVisualized": false
        },
    '''
    previous_cancer_diagnosis = models.CharField(max_length=1000, null=True)
    '''
    "previous_cancer_diagnosis": {
            "category": "additional baseline",
            "dataType": "string",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "Previous cancer as free text, no ICD-10 code",
            "comment": "",
            "originalOvcabaseColumn": "Previous cancer dg",
            "alreadyVisualized": false
        },
    '''

    progression = models.BooleanField()
    '''
    "progression": {
            "category": "outcome",
            "dataType": "boolean",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "Whether or not the disease has progressed",
            "comment": "",
            "originalOvcabaseColumn": "CUD_Progression",
            "alreadyVisualized": false
        },
    '''

    operation1_cancelled = models.BooleanField(null=True)
    '''
    "operation1_cancelled": {
            "category": "operation",
            "dataType": "boolean",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 2,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Oper1_cancelled",
            "alreadyVisualized": false
        },
    '''

    residual_tumor_pds = models.CharField(max_length=100, null=True, choices=ResidualTumorPDS.choices)
    '''
    "residual_tumor_pds": {
            "category": "operation",
            "dataType": "string",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "How much tumor is left in patient after primary debulking surgery (PDS)",
            "comment": "",
            "originalOvcabaseColumn": "Residual tumor PDS",
            "alreadyVisualized": false,
            "valueSpace": [
                "0",
                "1 to 10mm",
                "more than 10mm"
            ]
        },
    '''

    wgs_available = models.BooleanField()
    '''
    "wgs_available": {
            "category": "subset",
            "dataType": "boolean",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "Any sample in any time point where WGS is flagged OK",
            "comment": "maybe some other source more reliable for this than Ovcabase?",
            "originalOvcabaseColumn": "Patient card::Patient with any WGS samples",
            "alreadyVisualized": false
        },
    '''

    operation2_cancelled = models.BooleanField(null=True)
    '''
    "operation2_cancelled": {
            "category": "operation",
            "dataType": "boolean",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "",
            "comment": "",
            "originalOvcabaseColumn": "Oper2_cancelled",
            "alreadyVisualized": false
        },
    '''

    residual_tumor_ids = models.CharField(max_length=100, null=True, choices=ResidualTumorIDS.choices)
    '''
    "residual_tumor_ids": {
            "category": "operation",
            "dataType": "string",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "How much tumor is left in patient after interval debulking surgery (IDS)",
            "comment": "",
            "originalOvcabaseColumn": "Residual tumor IDS",
            "alreadyVisualized": false,
            "valueSpace": [
                "0",
                "1 to 10mm",
                "more than 10mm"
            ]
        },
    '''

    debulking_surgery_ids = models.BooleanField(null=True)
    '''
    "debulking_surgery_ids": {
            "category": "operation",
            "dataType": "boolean",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "Is tumor mass surgically removed in IDS or not",
            "comment": "",
            "originalOvcabaseColumn": "Oper2_debulking surgery",
            "alreadyVisualized": false
        },
    '''

    brca_mutation_status = models.CharField(max_length=100, null=True, choices=BRCAMutation.choices)
    '''
    "brca_mutation_status": {
        "category": "basic genetic info",
        "dataType": "string",
        "unit": null,
        "notNull": false,
        "listVariable": true,
        "importance": 1,
        "description": "Sources both clinical test (Ovcabase) and Decider",
        "comment": "",
        "originalOvcabaseColumn": "BRCA mutation status",
        "alreadyVisualized": true,
        "valueSpace": [
            "No BRCA mut",
            "BRCA1 in tumor",
            "BRCA1 in blood",
            "BRCA2 in tumor",
            "BRCA2 in blood"
        ]
    },
    '''

    hr_signature_pretreatment_wgs = models.CharField(max_length=100, null=True, choices=HRPretreatmentWGS.choices)
    '''
    "hr_signature_pretreatment_wgs": {
            "category": "basic genetic info",
            "dataType": "string",
            "unit": null,
            "notNull": false,
            "listVariable": false,
            "importance": 1,
            "description": "HRsignature patient level HautaniemiLab",
            "comment": "only pretreatment WGS samples included",
            "originalOvcabaseColumn": "HR signature SBS3 pretreatment WGS",
            "alreadyVisualized": false,
            "valueSpace": [
                "HRD",
                "HRP"
            ]
        },
    '''

    hr_signature_per_patient = models.CharField(max_length=100, null=True, choices=HRPerPatient.choices)
    '''
    "hr_signature_per_patient": {
        "category": "basic genetic info",
        "dataType": "string",
        "unit": null,
        "notNull": false,
        "listVariable": false,
        "importance": 1,
        "description": "HRsignature HautaniemiLab",
        "comment": "WEG, WES, pretreatment/postNACT",
        "originalOvcabaseColumn": "HR signature SBS3 per patient",
        "alreadyVisualized": false,
        "valueSpace": [
            "HRD",
            "HRP"
        ]
    },
    '''

    hrd_myriad_status = models.CharField(max_length=100, null=True, choices=HRDMyriadStatus.choices)
    '''
    "hrd_myriad_status": {
        "category": "basic genetic info",
        "dataType": "string",
        "unit": null,
        "notNull": false,
        "listVariable": false,
        "importance": 1,
        "description": "Commercial validated HRD test",
        "comment": "",
        "originalOvcabaseColumn": "HRD Myriad status",
        "alreadyVisualized": false,
        "valueSpace": [
            "HRD positive",
            "HRD negative"
        ]
    }
    '''

    sequencing_available = models.BooleanField()
    '''
    "sequencing_available": {
            "category": "subset",
            "dataType": "boolean",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "If there are at least one WGS or RNASeq done from patient's fresh tissue samples",
            "comment": "maybe some other source more reliable for this than Ovcabase?",
            "originalOvcabaseColumn": "Patient card::Patient with any sequenced tissue",
            "alreadyVisualized": false
        },```
    '''

    paired_fresh_samples_available = models.BooleanField()
    '''
    "paired_fresh_samples_available": {
            "category": "subset",
            "dataType": "boolean",
            "unit": null,
            "notNull": true,
            "listVariable": false,
            "importance": 1,
            "description": "any fresh sample pair available: primary+IDS, primary+residive or IDS+residive",
            "comment": "This in manually filled info in Ovcabase, not always up to date?",
            "originalOvcabaseColumn": "Patient card::Patient with paired fresh samples",
            "alreadyVisualized": false
        },
        '''



    # has_response_ct = models.BooleanField(default=False)
    # has_ctdna = models.BooleanField(default=False)
    # has_petct = models.BooleanField(default=False)

    # has_singlecell = models.BooleanField(default=False)

    '''
    "germline_pathogenic_variant": {
        "category": "baseline",
        "dataType": "string",
        "unit": NaN,
        "notNull": false,
        "listVariable": false,
        "importance": 3,
        "description": "Gene site",
        "comment": "'NotDetected', if no pathogenic variant is detected, can also be null if no testing is done",
        "originalOvcabaseColumn": "Gene Germ line pathogenic variant",
        "alreadyVisualized": false,
        "valueSpace": NaN
    }
    '''
    germline_pathogenic_variant = models.CharField(max_length=2000, null=True, blank=True)

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
            # models.CheckConstraint(
            #     check=Q(primary_laprascopy_date__lt=F("time_of_diagnosis")),
            #     name="lapra-constraint1",
            # ),
            # models.CheckConstraint(
            #     check=Q(time_of_diagnosis__lt=F("primary_operation_date")),
            #     name="diagnosis-constraint1",
            # ),
            # models.CheckConstraint(
            #     check=Q(primary_operation_date__lt=F("last_primary_chemo")),
            #     name="operation-constraint1",
            # ),
            # models.CheckConstraint(
            #     check=Q(primary_operation_date__lt=F("secondary_operation_date")),
            #     name="operation-constraint2",
            # ),
            # models.CheckConstraint(
            #     check=Q(primary_operation_date__lt=F("last_followup_visit")),
            #     name="followup-constraint1",
            # ),
            # models.CheckConstraint(
            #     check=Q(last_followup_visit__lt=F("next_followup_visit")),
            #     name="followup-constraint2",
            # ),
            # models.CheckConstraint(
            #     check=Q(last_primary_chemo__lt=F("maintenance_therapy_end")),
            #     name="maintenance-constraint1",
            # ),
            # # models.CheckConstraint(
            #     check=Q(maintenance_therapy_end__lt=F("progression_date")),
            #     name="progression-constraint1",
            # ),
            # models.CheckConstraint(
            #     check=Q(progression_date__lt=F("date_of_death")),
            #     name="outcome-constraint1",
            # ),
            # models.CheckConstraint(
            #     check=Q(date_of_outcome__lt=F("date_of_death")),
            #     name="outcome-constraint2",
            # ),
        ]

# class RecordEvent(models.TextChoices):
#     LABORATORY = "LABORATORY", _("laboratory")
#
# class RecordName(models.TextChoices):
#     NAME = "NAME", _("name")

# external means the identifier is from the external database


class TimelineRecord(models.Model):
    external_record_id      = models.IntegerField(unique=True)
    patient                 = models.ForeignKey(ClinicalData, on_delete=models.CASCADE)
    event                   = models.CharField(max_length=255)
    interval                = models.BooleanField(blank=True, null=True)
    ongoing                 = models.BooleanField(blank=True, null=True)
    interval_length         = models.IntegerField(blank=True, null=True)
    date_relative           = models.IntegerField(blank=True, null=True)
    interval_end_relative   = models.IntegerField(blank=True, null=True)
    name                    = models.CharField(max_length=255)
    result                  = models.FloatField(blank=True, null=True)
    aux_id                  = models.CharField(max_length=255, blank=True, null=True)
    source_system           = models.CharField(max_length=255)

    def __str__(self):
        return self.external_record_id

    class Meta:
        constraints = []

