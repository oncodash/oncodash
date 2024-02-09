import axios, { AxiosResponse } from 'axios'
import Cookies from 'universal-cookie'
import { PatientID } from './models/Patient'
import { PatientDTO } from './models/PatientDTO'

// Initialize Axios instance
// =========================================================================

const baseURL = import.meta.env.BASE_URL
const base = axios.create({ baseURL })
const cookies = new Cookies()

// Interceptors
// =========================================================================

base.interceptors.response.use(response => {
  return response
}, (error) => {
  if (error.response.status === 401) window.location.assign('/login')
  else return Promise.reject(error)
})

// API
// =========================================================================

export default {
  getPatientsList: async function (): Promise<AxiosResponse<Array<PatientDTO>>> {
    return await base.get('/api/clinical-overview/data/', {
      headers: {
        Authorization: `Token ${cookies.get('token')}`
      }
    })
  },
  getPatientClinical: async function (patientID: PatientID): Promise<AxiosResponse<PatientDTO>> {
    return await base.get(`/api/clinical-overview/data/${patientID}/`, {
      headers: {
        Authorization: `Token ${cookies.get('token')}`
      }
    })
  },
  getPatientGenomic: async function (patientID: PatientID) {
    return await base.get(`/api/genomic-overview/data/${patientID}/`, {
      headers: {
        Authorization: `Token ${cookies.get('token')}`
      }
    })
  },
  login: async function (email: string, password: string) {
    return await base.post('/api-token-auth/', {
      username: email,
      password
    })
  },
  logout: async function () {
    return await base.get('/token/', {
      headers: {
        'Authorization': `Token ${cookies.get('token')}`
      }
    })
  }
}
