import axios from 'axios'

// Initialize Axios instance
// =========================================================================

const baseURL = import.meta.env.BASE_URL
const base = axios.create({ baseURL })

// API
// =========================================================================

export default {
  getPatientsList: async function () {
    return await base.get('/api/clinical-overview/data/', {
      headers: {
        Authorization: 'Token d2431e327983108f3385369aa4e72f573263ab9d'
      }
    })
  }
}
