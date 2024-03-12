import axios, { AxiosResponse } from 'axios'
import Cookies from 'universal-cookie'
import { PatientID } from './models/Patient'
import { PatientDTO } from './models/PatientDTO'

// Initialize Axios instance
// =========================================================================

const apiURL = import.meta.env.ONCODASH_API_URL
const api = axios.create({ baseURL: apiURL })
const cookies = new Cookies()

// Interceptors
// =========================================================================

api.interceptors.response.use(response => {
  return response
}, (error) => {
  if (error.response.status === 401) window.location.assign('/login')
  else return Promise.reject(error)
})

// API
// =========================================================================

export default {
  getPatientsList: async function (): Promise<AxiosResponse<Array<PatientDTO>>> {
    return await api.get('/api/clinical-overview/data/', {
      headers: {
        Authorization: `Token ${cookies.get('token')}`
      }
    })
  },
  getPatientClinical: async function (patientID: PatientID): Promise<AxiosResponse<PatientDTO>> {
    return await api.get(`/api/clinical-overview/data/${patientID}/`, {
      headers: {
        Authorization: `Token ${cookies.get('token')}`
      }
    })
  },
  getPatientGenomic: async function (patientID: PatientID) {
    return await api.get(`/api/genomic-overview/data/${patientID}/`, {
      headers: {
        Authorization: `Token ${cookies.get('token')}`
      }
    })
  },
  login: async function (email: string, password: string) {
    return await api.post('/api-token-auth/', {
      username: email,
      password
    })
  },
  logout: async function () {
    return await api.get('/token/', {
      headers: {
        'Authorization': `Token ${cookies.get('token')}`
      }
    })
  }
}
