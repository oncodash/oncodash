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

  async function getPatients(token) {
    // call: GET /api/surveys
    return getJson(
      fetch(BASEURL + CLIN_OVERVIEW, {
        method: 'GET',
        headers: {
          'Authorization': 'Token '+token,
        },
      })
    ).then(patients => {
      // console.log(patients);
      return patients.map((s)=> new Patient(  
                      s.patient_id,
                      s.cohort_code,
                      s.chronic_illnesses_at_dg,
                      s.chronic_illnesses_type,
                      s.time_series,
                      s.event_series,
                      s.histology,
                      s.stage,
                      s.primary_therapy_outcome,
                      s.survival,
                      s.treatment_strategy,
                      s.followup_time,
                      s.platinum_free_interval_at_update,
                      s.platinum_free_interval,
                      s.days_to_progression,
                      s.days_from_beva_maintenance_end_to_progression,
                      s.days_to_death,
                      s.age_at_diagnosis,
                      s.height_at_diagnosis,
                      s.weight_at_diagnosis,
                      s.bmi_at_diagnosis,
                      s.previous_cancer,
                      s.previous_cancer_diagnosis,
                      s.progression,
                      s.operation1_cancelled,
                      s.residual_tumor_pds,
                      s.wgs_available,
                      s.operation2_cancelled,
                      s.residual_tumor_ids,
                      s.debulking_surgery_ids,
                      s.brca_mutation_status,
                      s.hr_signature_pretreatment_wgs,
                      s.hr_signature_per_patient,
                      s.hrd_myriad_status,
                      s.sequencing_available,
                      s.paired_fresh_samples_available,
                                            ));
    });
  
  }

  async function getSelectedPatient(token, patient_id) {
    // call: GET /api/surveys
    return getJson(
      fetch(BASEURL + CLIN_OVERVIEW + patient_id + `/`, {
        method: 'GET',
        headers: {
          'Authorization': 'Token '+token,
        },
      })
    ).then(patient => {
      // console.log(patient.time_series);
      return new Patient(                     
              patient.patient_id,
              patient.cohort_code,
              patient.chronic_illnesses_at_dg,
              patient.chronic_illnesses_type,
              JSON.parse(patient.time_series),
              JSON.parse(patient.event_series),
              patient.histology,
              patient.stage,
              patient.primary_therapy_outcome,
              patient.survival,
              patient.treatment_strategy,
              patient.followup_time,
              patient.platinum_free_interval_at_update,
              patient.platinum_free_interval,
              patient.days_to_progression,
              patient.days_from_beva_maintenance_end_to_progression,
              patient.days_to_death,
              patient.age_at_diagnosis,
              patient.height_at_diagnosis,
              patient.weight_at_diagnosis,
              patient.bmi_at_diagnosis,
              patient.previous_cancer,
              patient.previous_cancer_diagnosis,
              patient.progression,
              patient.operation1_cancelled,
              patient.residual_tumor_pds,
              patient.wgs_available,
              patient.operation2_cancelled,
              patient.residual_tumor_ids,
              patient.debulking_surgery_ids,
              patient.brca_mutation_status,
              patient.hr_signature_pretreatment_wgs,
              patient.hr_signature_per_patient,
              patient.hrd_myriad_status,
              patient.sequencing_available,
              patient.paired_fresh_samples_available,               
                        );
    });
  
  }  

  async function logIn(username, password) {
    let response = await fetch('http://127.0.0.1:8888/api-token-auth/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({username, password}),
    });
    if(response.ok) {
      
      const res = await response.json();
      return res;
    }
    else {
      try {
        const errDetail = await response.json();
        throw errDetail.message;
      }
      catch(err) {
        throw err;
      }
    }
  }
  
  async function logOut(token) {
    await fetch('http://127.0.0.1:8888/logout/', {
      method: 'GET',
      headers: {
        'Authorization': 'Token '+token,
      },
    });
  }
  
  async function getUserInfo() {
    const response = await fetch(BASEURL + '/sessions/current');
    const userInfo = await response.json();
    if (response.ok) {
      return userInfo;
    } else {
      throw userInfo;  // an object with the error coming from the server
    }
  }  

const API = {getPatients, getSelectedPatient, logIn, logOut, getUserInfo};
export default API;