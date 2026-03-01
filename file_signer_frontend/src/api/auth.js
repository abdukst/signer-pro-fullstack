import apiClient from "./client";

export async function login(email, password) {
  try {
    const response = await apiClient.post('/auth/login', {
      email,
      password
    })
    return response.data
  } catch (error) {
    // Just throw the raw error forward to the component
    throw error
  }
  
}

export async function register(userData) {
  try {
    const response = await apiClient.post('/users/register', userData)
    return response.data
  } catch (error){
    throw  error
  }
}