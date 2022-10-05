// import of the Objects declarations
import {Patient} from './Clinical/Patient.js';

/**
 * All the API calls
 */
 const BASEURL =  `http://localhost:8888/api/`;
 const CLIN_OVERVIEW = `clinical-overview/data/`;

 
 function getJson(httpResponsePromise) {
    return new Promise((resolve, reject) => {
      httpResponsePromise
        .then((response) => {
          if (response.ok) {
  
           // always return {} from server, never null or non json, otherwise it will fail
           response.json()
              .then( json => resolve(json) )
              .catch( err => reject({ error: "Cannot parse server response" }))
  
          } else {
            // analyze the cause of error
            response.json()
              .then(obj => reject(obj)) // error msg in the response body
              .catch(err => reject({ error: "Cannot parse server response" })) // something else
          }
        })
        .catch(err => reject({ error: "Cannot communicate"  })) // connection error
    });
  }

  async function getPatients() {
    // call: GET /api/surveys
    return getJson(
      fetch(BASEURL + CLIN_OVERVIEW)
    ).then(patients => {
      return patients.map((s)=> new Patient(  s.id, 
                                              s.age, 
                                              s.cud_survival, 
                                              s.cud_histology, 
                                              s.cud_stage, 
                                              s.cud_treatment_strategy,
                                              s.cud_primary_therapy_outcome,
                                              s.cud_current_treatment_phase,
                                              s.maintenance_therapy,
                                              s.extra_patient_info,
                                              s.other_diagnosis,
                                              s.cancer_in_family,
                                              s.chronic_illness,
                                              s.other_medication,  
                                              s.time_series,                                            
                                            ));
    });
  
  }

  async function getSelectedPatient(patient_id) {
    // call: GET /api/surveys
    return getJson(
      fetch(BASEURL + CLIN_OVERVIEW + patient_id + `/`)
    ).then(patient => {
      return new Patient(                     
                          patient.id, 
                          patient.age, 
                          patient.cud_survival, 
                          patient.cud_histology, 
                          patient.cud_stage, 
                          patient.cud_treatment_strategy,
                          patient.cud_primary_therapy_outcome,
                          patient.cud_current_treatment_phase,
                          patient.maintenance_therapy,
                          patient.extra_patient_info,
                          patient.other_diagnosis,
                          patient.cancer_in_family,
                          patient.chronic_illness,
                          patient.other_medication,   
                          JSON.parse(patient.time_series),   
                          patient.height,
                          patient.weight,
                          patient.has_brca_mutation,                
                        );
    });
  
  }  

const API = {getPatients, getSelectedPatient};
export default API;