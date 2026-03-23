import axios from 'axios'
import { supabase } from './supabase'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })

api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const getJobs   = ()        => api.get('/jobs').then(r => r.data)
export const createJob = (job)     => api.post('/jobs', job).then(r => r.data)
export const updateJob = (id, job) => api.put(`/jobs/${id}`, job).then(r => r.data)
export const deleteJob = (id)      => api.delete(`/jobs/${id}`)