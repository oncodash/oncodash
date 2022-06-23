# Timeline data table description

**id** (_int_)

> unique identifier for each row

**patient_id** (_int_)
> unique identifier for each patient

**cohort_code** (_string_)
>alternative identifier for each patient

**interval** (bool)
> true, if row represents an interval, otherwise false (for timepoints)
> If the event is *parpi_treatment*, it can be either ongoing or finished. Only the finished treatments are marked as intervals.

**ongoing** (bool)
> Used with PARPi treatments. If the treatment is still ongoing, but there has been a clinical check, the PARPi interval end denotes the date of last checkup and ongoing is set to *true*.

**date** (_date_)
> date in ISO 8601 format 'YYYY-MM-DD'. For intervals represents the start of the interval.

**date_relative** (_int_)
> difference of timepoint and the date of diagnosis in days.

**interval_end** (_date_)
> date in ISO 8601 format 'YYYY-MM-DD'. Last day of interval.

**interval_end_relative** (_int_)
> difference of interval end date and date of diagnosis in days

**interval_length** (_int_)
> duration of the interval in days. Null for time points.

**event** (_string_)
> one of the following:

> * *diagnosis*: date of initial diagnosis
> * *primary_progression*: date of detection of first disease progression
> * *2nd_progression*: date of detection of 2nd disease progression
> * *3rd_progression*: date of detection of 3rd disease progression
> * *4th_progression*: date of detection of 4th disease progression
> * *5th_progression*: date of detection of 5th disease progression
> * *oper1*: primary operation
> * *oper2ids*: date of interval debulking surgery
> * *operation*: any operation from electronic health records belonging to determined set of operations of interest. Does not include operations stored as ascites events.
> * *death*: date of death
> * *ascites* Ascites draining, either determined from EHR operation data, ovcabase manual clinical data or fresh sample data.
> * *fresh_sample*: tissue/ascites sample which is not sent to sequencing
> * *fresh_sample_sequenced*: tissue/ascites sample which is sequenced
> * *tykslab_plasma*: blood plasma sample
> * *ctdna_sample*: blood plasma sample with ctdna data available
> * *laboratory*: laboratory result from predetermined set of assays (CA125, Hb, platelets, leukocytes)
> * *radiology*: date of radiological imaging, typically CT scan or PET CT
> * *chemotherapy_cycle*: chemo cycle interval
> * *chemotherapy_dose*: single dose of one medicine given in a chemo cycle
> * *parpi_treatment*: PARP inhibitor medication taken at home. Data source: Ovcabase.

**name** (_string_)
> additional information depending on the event:

> * *radiology*: NSCP code for the study
> * *operation*: NSCP code for the operation
> * *laboratory*: Assay in question (ca125, hb, leuk, platelets)
> * *chemotherapy_cycle*: English generic name of the chemotherapy regimen. In case of no English name available, original Finnish name is used.
> * *chemotherapy_dose* or *parpi_treatment*: generic name of the medication administered.

**result** (_float_)
> * Result of the laboratory assay, used when event is 'laboratory'.
> * If the amount of ascites is measured, the amount is in millilitres.

**aux_id** (_string_)
> additional information depending on the event:

> * *chemotherapy_cycle*: Kemokur software ID used for the cycle. Empty for cycles outside TYKS.
> * *chemotherapy_dose*: Kemokur software ID used for the cycle to which the dose belongs. Empty for cycles outside TYKS.
> * *fresh_sample*: Fresh sample ID used in Ovcabase for the sample
> * *fresh_sample_sequenced*: Fresh sample ID used in Ovcabase for the sample
> * *tykslab_plasma*: Tykslab ID for the plasma sample
> * *ctdna_sample*: Tykslab ID for the plasma sample

**source_system** (_string_)
> Either 'auria', if data comes directly from VSSHP's electronic health records or 'ovcabase', if the immediate upstream source of the data is OvcaBase.

# Notes

## Ascites

The information about ascites punctures comes from multiple sources. It is stored either manually to Ovcabase in multiple locations or it is included in operations in Auria EHR data. These data sources are not necessary mutually exclusive, so the data is inserted hierarchially to the timeline dataset.

> 1. Data from Ovcabase's clinical table, if it includes also amount of drained ascites. Ascites amount in millilitres is included in 'result' column.
> 2. Data from Ovcabase's fresh sample table, omitting already included (patient, date) tuples
> 3. Data from Ovcabase's clinical table, omitting already included (patient, date) tuples
> 4. Data from Auria's operations, omitting already included (patient, date) tuples. Includes also the operation code in 'name' column.

# Changelog

## 2022-04-04

* Included 'ascites' as a type of events
* Included column 'source_system' to denote data origins
* Added manually inserted CA-125 samples from Ovcabase
* Added column 'ongoing' to PARPi treatments

## 2022-02-11

* Included also 2nd, 3rd, 4th and 5th progression events

