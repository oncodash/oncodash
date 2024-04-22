
Clinical
========

Clinical data sources
---------------------

The clinical data is sourced from an outside clinical database. The data is divided into two datasets:

1. Clinical export: this file consists of patient-level state data without any time series or history, such as age at diagnosis, disease histology, treatment strategy and variables like overall survival and progression-free survival. Some variables may change over time, mostly from undefined to defind. Only the current state of the variables in this file is of importance, not their history.

2. Time series data set: this data set contains information such as laboratory test results, chemotherapy information, sampling timepoints and operations. Timeline plots can be constructed from this data to visualise the whole treatment and disease progression from initial diagnosis.

In the current DECIDER setting, the source system does not allow for automatic retrieval of data via API connection. The data is provided in two separate CSV files.

Clinical export data description
--------------------------------

Variable parameters
___________________

- **category:** Relevant category where the column should be in visualisation
- **unit:** Null if unitless
- **listVariable:** If the variable is a list of Strings, represented as comma-separated list
- **valueSpace:** If there is a define value space (list of strings), it is defined here
- **importance:** From 1 to n, where 1 is the most important.
- **comment:** Various comments from the clinicians about the data

Only non-null variable parameters are described below.

Exported variables
__________________

- **age_at_diagnosis** (float, not nullable)

   - category: baseline
   - unit: year
   - listVariable: False
   - importance: 1
- **bmi_at_diagnosis** (float, not nullable). Body mass index at diagnosis

   - category: baseline
   - unit: kilogram / meter / meter
   - listVariable: False
   - importance: 2
- **brca_mutation_status** (string, nullable). Sources both clinical test (Ovcabase) and Decider

   - category: basic genetic info
   - listVariable: True
   - importance: 1
   - valueSpace: ['BRCA1 in blood', 'BRCA1 in tumor', 'BRCA1 somatic', 'BRCA2 in blood', 'BRCA2 in tumor', 'No BRCA mut']
- **cause_of_death** (string, not nullable)

   - category: outcome
   - listVariable: False
   - importance: 1
   - valueSpace: ['death due to cancer', 'death due to other reason', 'death due to other reason (sepsis, heart failure)', 'death reason unknown']
- **chronic_illnesses_at_dg** (boolean, nullable)

   - category: additional baseline
   - listVariable: False
   - importance: 2
- **chronic_illnesses_type** (string, nullable). What illnesses patient had at time of diagnosis (from value list)

   - category: additional baseline
   - listVariable: True
   - importance: 2
   - valueSpace: ['Acid reflux', 'Arthrosis/arthritis', 'Asthma', 'Atrial fibrillation', 'COPD', 'Colitis ulcerosa', 'Depression', 'Epilepsy', 'Fibromyalgia', 'Glaucoma', 'Hypercholesterolemia', 'Hypertension', 'Hypothyroidism', 'MCC', 'Myocardial infarction', 'Osteoporosis', 'Other', 'Pulmonary embolism', 'Renal insufficiency', 'Rheumatoid arthritis', 'Schizophrenia', 'Stroke', 'Type 2 diabetes', 'Venous thrombosis']
- **clinical_trials_participation** (boolean, nullable). Participation in any clinical trials

   - category: clinical_trial
   - listVariable: False
   - importance: 3
- **cohort_code** (string, not nullable). Alternative patient identifier

   - category: identifier
   - listVariable: False
   - importance: 1
- **current_phase_of_treatment** (string, nullable)

   - category: treatment
   - listVariable: False
   - importance: 2
   - comment: String of free-text treatment info
   - valueSpace: ['bevacizumab maintenance after primary therapy', 'currently in drug trial', 'follow-up', 'follow-up after progression treatment', 'hormonal treatment', 'neoadjuvant', 'parpi maintenance after primary therapy', 'parpi maintenance after progression', 'primary chemotherapy', 'progression', 'progression, active treatment ended', 'regular follow-up visits ended']
- **days_from_beva_maintenance_end_to_progression** (integer, nullable). Days from end of bevacizumab maintenance end to progression

   - category: outcome
   - unit: day
   - listVariable: False
   - importance: 2
- **days_to_death** (integer, nullable). Days from diagnosis to death

   - category: outcome
   - unit: day
   - listVariable: False
   - importance: 1
   - comment: Also in timeline dataset, event "death", is this needed here?
- **days_to_progression** (integer, nullable). Days from diagnosis to first progression

   - category: outcome
   - unit: day
   - listVariable: False
   - importance: 1
   - comment: Also in timeline dataset, event "primary_progression", is this needed here?
- **debulking_surgery_ids** (boolean, nullable). Is tumor mass surgically removed in IDS or not

   - category: operation
   - listVariable: False
   - importance: 1
- **drug_trial_name** (string, nullable). The clinical trial the patient has participated

   - category: clinical_trial
   - listVariable: False
   - importance: 3
   - valueSpace: ['AVANOVA', 'B96', 'DOVACC', 'DUO-O', 'EPIK-O', 'FIRST', 'IMAGYN', 'MK 3475', 'PAOLA', 'PRIMA']
- **drug_trial_unblinded** (boolean, nullable). Drug / placebo unblinding

   - category: clinical_trial
   - listVariable: False
   - importance: 3
   - comment: True or null
- **followup_time** (integer, nullable)

   - category: outcome
   - unit: day
   - listVariable: False
   - importance: 1
- **germline_pathogenic_variant** (string, nullable). Gene site

   - category: baseline
   - listVariable: False
   - importance: 3
   - comment: 'NotDetected', if no pathogenic variant is detected, can also be null if no testing is done
- **height_at_diagnosis** (float, not nullable)

   - category: baseline
   - unit: meter
   - listVariable: False
   - importance: 2
- **histology** (string, not nullable)

   - category: baseline
   - listVariable: False
   - importance: 1
   - comment: Are other values than high-grade serous even needed here or should they be filtered out?: Let´s filter them out
   - valueSpace: ['high grade serous']
- **hr_signature_per_patient** (string, nullable). HRsignature HautaniemiLab

   - category: basic genetic info
   - listVariable: False
   - importance: 1
   - comment: WEG, WES, pretreatment/postNACT
   - valueSpace: ['HRD', 'HRP']
- **hr_signature_pretreatment_wgs** (string, nullable). HRsignature patient level HautaniemiLab

   - category: basic genetic info
   - listVariable: False
   - importance: 1
   - comment: only pretreatment WGS samples included
   - valueSpace: ['HRD', 'HRP']
- **hrd_clinical_test_result** (string, nullable). Commercial validated HRD test

   - category: basic genetic info
   - listVariable: False
   - importance: 1
   - valueSpace: ['HRD positive', 'HRD negative']
- **maintenance_therapy_after_1st_line** (string, nullable). String of free-text treatment info

   - category: treatment
   - listVariable: False
   - importance: 3
- **operation1_cancelled** (boolean, nullable)

   - category: operation
   - listVariable: False
   - importance: 2
- **operation2_cancelled** (boolean, nullable)

   - category: operation
   - listVariable: False
   - importance: 1
- **paired_fresh_samples_available** (boolean, not nullable). any fresh sample pair available: primary+IDS, primary+residive or IDS+residive

   - category: subset
   - listVariable: False
   - importance: 1
   - comment: This in manually filled info in Ovcabase, not always up to date?
- **patient_id** (integer, not nullable). Unique patient identifier

   - category: identifier
   - listVariable: False
   - importance: 1
- **platinum_free_interval** (integer, nullable). Time from last day of primary therapy to progression

   - category: outcome
   - unit: day
   - listVariable: False
   - importance: 1
   - comment: Null, if not progressed
- **platinum_free_interval_at_update** (integer, nullable). Lower limit of platinum free interval, which is equal to time from last day of primary therapy to followup, if not relapsed

   - category: outcome
   - unit: day
   - listVariable: False
   - importance: 1
   - comment: Null, if progressed
- **previous_cancer** (boolean, nullable)

   - category: additional baseline
   - listVariable: False
   - importance: 2
- **previous_cancer_diagnosis** (string, nullable). Previous cancer as free text, no ICD-10 code

   - category: additional baseline
   - listVariable: False
   - importance: 1
- **previous_cancer_year** (integer, nullable)

   - category: additional baseline
   - listVariable: False
   - importance: 1
- **primary_therapy_outcome** (string, nullable). RECIST class of primary therapy outcome

   - category: outcome
   - listVariable: False
   - importance: 1
   - valueSpace: ['complete response', 'progressive disease', 'partial response', 'stable disease', 'no chemotherapy', 'ND', 'died during chemotherapy']
- **primary_therapy_outcome_comment** (string, nullable). Additional info about why primary therapy outcome is not defined

   - category: outcome
   - listVariable: False
   - importance: 2
- **progression** (boolean, nullable). Whether or not the disease has progressed

   - category: outcome
   - listVariable: False
   - importance: 1
- **residual_tumor_ids** (string, nullable). How much tumor is left in patient after interval debulking surgery (IDS)

   - category: operation
   - listVariable: False
   - importance: 1
   - valueSpace: ['0', '1 to 10mm', 'more than 10mm']
- **residual_tumor_pds** (string, nullable). How much tumor is left in patient after primary debulking surgery (PDS)

   - category: operation
   - listVariable: False
   - importance: 1
   - valueSpace: ['0', '1 to 10mm', 'more than 10mm']
- **sequencing_available** (boolean, not nullable). If there are at least one WGS or RNASeq done from patient's fresh tissue samples

   - category: subset
   - listVariable: False
   - importance: 1
   - comment: maybe some other source more reliable for this than Ovcabase?
- **stage** (string, nullable). FIGO2014 classification of disease spread at diagnosis

   - category: baseline
   - listVariable: False
   - importance: 1
   - valueSpace: ['IVB', 'IIIB', 'IIIC', 'IVA', 'IIB', 'IC', 'IC2', 'IC1', 'IIIA1', 'IIA', 'IA', 'IB']
- **survival** (boolean, not nullable). Alive or dead

   - category: outcome
   - listVariable: False
   - importance: 1
- **treatment_strategy** (string, not nullable)

   - category: baseline
   - listVariable: False
   - importance: 1
   - comment: Other means either palliative or atypical. Mostly PDS or NACT
   - valueSpace: ['PDS', 'NACT', 'Other']
- **weight_at_diagnosis** (float, not nullable)

   - category: baseline
   - unit: kilogram
   - listVariable: False
   - importance: 2
- **wgs_available** (boolean, not nullable). Any sample in any time point where WGS is flagged OK

   - category: subset
   - listVariable: False
   - importance: 1
   - comment: maybe some other source more reliable for this than Ovcabase?

Time series data description
----------------------------
Note: in this context, date refers to days from diagnosis (integer) and not datestamp.

- **patient_id** (*int*): unique identifier for each patient.
- **cohort_code** (*string*): alternative identifier for each patient.
- **interval** (*bool*): true, if row represents an interval, otherwise false (for timepoints). If the event is *parpi_treatment*, it can be either ongoing or finished. Only the finished treatments are marked as intervals.
- **ongoing** (*bool*): used with PARPi treatments. If the treatment is still ongoing, but there has been a clinical check, the PARPi interval end denotes the date of last checkup and ongoing is set to *true*.
- **date_relative** (*int*): difference of timepoint and the date of diagnosis in days. This is used as the main temporal coordinate.
- **interval_end_relative** (*int*): difference of interval end date and date of diagnosis in days.
- **interval_length** (*int*): duration of the interval in days. Null for time points.
- **event** (*string*): one of the following:

    - *diagnosis*: date of initial diagnosis
    - *primary_progression*: date of detection of first disease progression
    - *2nd_progression*: date of detection of 2nd disease progression
    - *3rd_progression*: date of detection of 3rd disease progression
    - *4th_progression*: date of detection of 4th disease progression
    - *5th_progression*: date of detection of 5th disease progression
    - *oper1*: primary operation
    - *oper2ids*: date of interval debulking surgery
    - *operation*: any operation from electronic health records belonging to determined set of operations of interest. Does not include operations stored as ascites events.
    - *death*: date of death
    - *ascites* ascites draining, either determined from EHR operation data, ovcabase manual clinical data or fresh sample data.
    - *fresh_sample*: tissue/ascites sample which is not sent to sequencing
    - *fresh_sample_sequenced*: tissue/ascites sample which is sequenced
    - *tykslab_plasma*: blood plasma sample
    - *ctdna_sample*: blood plasma sample with ctdna data available
    - *laboratory*: laboratory result from predetermined set of assays (CA125, Hb, platelets, leukocytes, neutrophils)
    - *radiology*: date of radiological imaging, typically CT scan or PET CT
    - *chemotherapy_cycle*: chemo cycle interval
    - *chemotherapy_dose*: single dose of one medicine given in a chemo cycle
    - *parpi_treatment*: PARP inhibitor medication taken at home. Data source: Ovcabase.
- **name** (*string*): additional information depending on the event

    - *radiology*: NSCP code for the study
    - *operation*: NSCP code for the operation
    - *laboratory*: Assay in question (ca125, hb, leuk, platelets, neut)
    - *chemotherapy_cycle*: English generic name of the chemotherapy regimen. In case of no English name available, original Finnish name is used.
    - *chemotherapy_dose* or *parpi_treatment*: generic name of the medication administered.
- **result** (*float*): result of the laboratory assay, used when event is 'laboratory'. If the amount of ascites is measured, the amount is in millilitres.
- **aux_id** (*string*): additional information depending on the event:

    - *chemotherapy_cycle*: Kemokur software ID used for the cycle. Empty for cycles outside TYKS.
    - *chemotherapy_dose*: Kemokur software ID used for the cycle to which the dose belongs. Empty for cycles outside TYKS.
    - *fresh_sample*: Fresh sample ID used in Ovcabase for the sample
    - *fresh_sample_sequenced*: Fresh sample ID used in Ovcabase for the sample
    - *tykslab_plasma*: Tykslab ID for the plasma sample
    - *ctdna_sample*: Tykslab ID for the plasma sample
- **source_system** (*string*): Either 'auria', if data comes directly from VSSHP's electronic health records or 'ovcabase', if the immediate upstream source of the data is OvcaBase.