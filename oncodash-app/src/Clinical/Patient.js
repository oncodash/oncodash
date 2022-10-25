

function Patient(   
                    id, 
                    age, 
                    cud_survival, 
                    cud_histology, 
                    cud_stage, 
                    cud_treatment_strategy,
                    cud_primary_therapy_outcome,
                    cud_current_treatment_phase,
                    maintenance_therapy,
                    extra_patient_info,
                    other_diagnosis,
                    cancer_in_family,
                    chronic_illness,
                    other_medication,    
                    time_series,  
                    event_series,        
                    height,
                    weight,
                    BRCA,
                ){
    this.id                         = id;
    this.age                        = age;
    this.survival                   = cud_survival;
    this.histology                  = cud_histology;
    this.stage                      = cud_stage;
    this.strategy                   = cud_treatment_strategy;
    this.primary_outcome            = cud_primary_therapy_outcome;
    this.current_phase              = cud_current_treatment_phase;
    this.maintenance                = maintenance_therapy;
    this.extra_patient_info         = extra_patient_info;
    this.other_diagnosis            = other_diagnosis;
    this.cancer_in_family           = cancer_in_family;
    this.chronic_illness            = chronic_illness;
    this.other_medication           = other_medication;
    this.time_series                = time_series;
    this.event_series                = event_series;
    this.height                     = height;
    this.weight                     = weight;
    this.bmi                        = Number((weight/((height/100)**2)).toFixed(1));
    this.BRCA                       = BRCA
    // Number((6.688689).toFixed(1))

    this.toString = ()=>{
        return `id: ${this.id}, age: ${this.age}, cud_survival: ${this.cud_survival}, cud_histology: ${this.cud_histology}, cud_stage: ${this.cud_stage}`;
    };
}

export {Patient};