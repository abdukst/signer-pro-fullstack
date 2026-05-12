import axios from 'axios'
import { useAuth } from '../auth/authStore'
import router from '../router'
import { useToast } from 'vue-toastification'

const toast = useToast()

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
      toast.error("Network Error: Server is unreachable.");
    } else if (error.response  ) {
      const status = error.response.status
      const detail = error.response.data?.detail || "An unexpected error occurred."
      if (status === 401 ) {
        console.log(error.response)
        clearToken()
        router.push('/login')
        toast.warning(status+": " +detail)
      } else if (status >= 400 && status < 500) {
        toast.error(status+": " +detail);
      } else if (status >= 500) {
        // Server errors (Database crash, etc.)
        toast.error("Server Error: Please contact support.");
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
