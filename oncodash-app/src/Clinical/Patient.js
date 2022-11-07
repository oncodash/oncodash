function Patient(   
    patient_id,
    cohort_code,
    chronic_illnesses_at_dg,
    chronic_illnesses_type,
    time_series,
    event_series,
    histology,
    stage,
    primary_therapy_outcome,
    survival,
    treatment_strategy,
    followup_time,
    platinum_free_interval_at_update,
    platinum_free_interval,
    days_to_progression,
    days_from_beva_maintenance_end_to_progression,
    days_to_death,
    age_at_diagnosis,
    height_at_diagnosis,
    weight_at_diagnosis,
    bmi_at_diagnosis,
    previous_cancer,
    previous_cancer_diagnosis,
    progression,
    operation1_cancelled,
    residual_tumor_pds,
    wgs_available,
    operation2_cancelled,
    residual_tumor_ids,
    debulking_surgery_ids,
    brca_mutation_status,
    hr_signature_pretreatment_wgs,
    hr_signature_per_patient,
    hrd_myriad_status,
    sequencing_available,
    paired_fresh_samples_available,
){
    this.patient_id                                     = patient_id
    this.cohort_code                                    = cohort_code    
    this.chronic_illnesses_at_dg                        = chronic_illnesses_at_dg                
    this.chronic_illnesses_type                         = chronic_illnesses_type            
    this.time_series                                    = time_series    
    this.event_series                                   = event_series    
    this.histology                                      = histology
    this.stage                                          = stage
    this.primary_therapy_outcome                        = primary_therapy_outcome                
    this.survival                                       = survival
    this.treatment_strategy                             = treatment_strategy        
    this.followup_time                                  = followup_time    
    this.platinum_free_interval_at_update               = platinum_free_interval_at_update                        
    this.platinum_free_interval                         = platinum_free_interval            
    this.days_to_progression                            = days_to_progression            
    this.days_from_beva_maintenance_end_to_progression  = days_from_beva_maintenance_end_to_progression                                    
    this.days_to_death                                  = days_to_death    
    this.age_at_diagnosis                               = age_at_diagnosis        
    this.height_at_diagnosis                            = height_at_diagnosis            
    this.weight_at_diagnosis                            = weight_at_diagnosis            
    this.bmi_at_diagnosis                               = bmi_at_diagnosis        
    this.previous_cancer                                = previous_cancer        
    this.previous_cancer_diagnosis                      = previous_cancer_diagnosis                
    this.progression                                    = progression    
    this.operation1_cancelled                           = operation1_cancelled            
    this.residual_tumor_pds                             = residual_tumor_pds        
    this.wgs_available                                  = wgs_available    
    this.operation2_cancelled                           = operation2_cancelled            
    this.residual_tumor_ids                             = residual_tumor_ids        
    this.debulking_surgery_ids                          = debulking_surgery_ids            
    this.brca_mutation_status                           = brca_mutation_status            
    this.hr_signature_pretreatment_wgs                  = hr_signature_pretreatment_wgs                    
    this.hr_signature_per_patient                       = hr_signature_per_patient                
    this.hrd_myriad_status                              = hrd_myriad_status        
    this.sequencing_available                           = sequencing_available            
    this.paired_fresh_samples_available                 = paired_fresh_samples_available                    

this.toString = ()=>{
return `id: ${this.patient_id}, age: ${this.age_at_diagnosis}, survival: ${this.survival}, histology: ${this.histology}, stage: ${this.stage}`;
};
}

export {Patient};