/**
 * Patient Data Transfer Object.
 * The object directly fetched from the API.
 */
export interface PatientDTO {
  age_at_diagnosis: number | null
  bmi_at_diagnosis: number | null
  brca_mutation_status: string | null
  chronic_illnesses_at_dg: boolean | null
  chronic_illnesses_type: string | null
  clinical_trial: boolean | null
  cohort_code: string | null
  current_treatment_phase: string | null
  days_from_beva_maintenance_end_to_progression: number | null
  days_to_death: number | null
  days_to_progression: number | null
  debulking_surgery_ids: boolean | null
  drug_trial_name: string | null
  drug_trial_unblinded: boolean | null
  event_series: string | null
  followup_time: number | null
  germline_pathogenic_variant: string | null
  height_at_diagnosis: number | null
  histology: string | null
  hr_signature_per_patient: string | null
  hr_signature_pretreatment_wgs: string | null
  hrd_myriad_status: string | null
  maintenance_therapy: string | null
  operation1_cancelled: boolean | null
  operation2_cancelled: boolean | null
  paired_fresh_samples_available: boolean | null
  patient_id: number
  platinum_free_interval: number | null
  platinum_free_interval_at_update: number | null
  previous_cancer: boolean | null
  previous_cancer_diagnosis: string | null
  primary_therapy_outcome: string | null
  progression: boolean | null
  residual_tumor_ids: string | null
  residual_tumor_pds: string | null
  sequencing_available: boolean | null
  stage: string | null
  survival: string | null
  time_series: string | null
  treatment_strategy: string | null
  weight_at_diagnosis: number | null
  wgs_available: boolean | null
}
