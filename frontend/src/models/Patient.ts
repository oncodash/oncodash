import { PatientDTO } from "./PatientDTO"

export type PatientID = number

/**
 * The main class representing a single Patient with
 * all their specific data.
 */
export class Patient {
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
  patient_id: PatientID
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

  constructor(patientDTO: PatientDTO) {
    this.age_at_diagnosis = patientDTO.age_at_diagnosis
    this.bmi_at_diagnosis = patientDTO.bmi_at_diagnosis
    this.brca_mutation_status = patientDTO.brca_mutation_status
    this.chronic_illnesses_at_dg = patientDTO.chronic_illnesses_at_dg
    this.chronic_illnesses_type = patientDTO.chronic_illnesses_type
    this.clinical_trial = patientDTO.clinical_trial
    this.cohort_code = patientDTO.cohort_code
    this.current_treatment_phase = patientDTO.current_treatment_phase
    this.days_from_beva_maintenance_end_to_progression = patientDTO.days_from_beva_maintenance_end_to_progression
    this.days_to_death = patientDTO.days_to_death
    this.days_to_progression = patientDTO.days_to_progression
    this.debulking_surgery_ids = patientDTO.debulking_surgery_ids
    this.drug_trial_name = patientDTO.drug_trial_name
    this.drug_trial_unblinded = patientDTO.drug_trial_unblinded
    this.event_series = patientDTO.event_series
    this.followup_time = patientDTO.followup_time
    this.germline_pathogenic_variant = patientDTO.germline_pathogenic_variant
    this.height_at_diagnosis = patientDTO.height_at_diagnosis
    this.histology = patientDTO.histology
    this.hr_signature_per_patient = patientDTO.hr_signature_per_patient
    this.hr_signature_pretreatment_wgs = patientDTO.hr_signature_pretreatment_wgs
    this.hrd_myriad_status = patientDTO.hrd_myriad_status
    this.maintenance_therapy = patientDTO.maintenance_therapy
    this.operation1_cancelled = patientDTO.operation1_cancelled
    this.operation2_cancelled = patientDTO.operation2_cancelled
    this.paired_fresh_samples_available = patientDTO.paired_fresh_samples_available
    this.patient_id = patientDTO.patient_id
    this.platinum_free_interval = patientDTO.platinum_free_interval
    this.platinum_free_interval_at_update = patientDTO.platinum_free_interval_at_update
    this.previous_cancer = patientDTO.previous_cancer
    this.previous_cancer_diagnosis = patientDTO.previous_cancer_diagnosis
    this.primary_therapy_outcome = patientDTO.primary_therapy_outcome
    this.progression = patientDTO.progression
    this.residual_tumor_ids = patientDTO.residual_tumor_ids
    this.residual_tumor_pds = patientDTO.residual_tumor_pds
    this.sequencing_available = patientDTO.sequencing_available
    this.stage = patientDTO.stage
    this.survival = patientDTO.survival
    this.time_series = patientDTO.time_series
    this.treatment_strategy = patientDTO.treatment_strategy
    this.weight_at_diagnosis = patientDTO.weight_at_diagnosis
    this.wgs_available = patientDTO.wgs_available
  }
}
