import axios from 'axios'
import { useAuth } from '../auth/authStore'
import router from '../router'



const apiClient = axios.create({
  baseURL: 'http://localhost:8000'
})
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// NEW: Response Interceptor for Auto-Logout

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const { clearToken } = useAuth()
    if (!error.response) {
      alert("Server is currently unreachable. Please try again later.")
    } else if (error.response && error.response.status === 401) {
      clearToken()
      router.push('/login')
      console.warn("Session expired. Logout ...")
    }
    return Promise.reject(error)
  }
)

export default apiClient
