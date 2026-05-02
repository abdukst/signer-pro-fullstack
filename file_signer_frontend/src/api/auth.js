import apiClient from "./client";

export async function login(email, password) {
  try {
    const response = await apiClient.post('/auth/tokens', {
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
    const response = await apiClient.post('/users', userData)
    return response.data
  } catch (error){
    throw  error
  }
}

/**
 * Sends a request to retire the current signing key.
 * Requires the user's password for re-authentication.
 * @param {string} password - The user's current login password
 */
export async function rotateUserKeys(password) {
  try{
    const response = await apiClient.post('/users/me/keys/rotations', 
      {password: password})
      return response.data
  } catch (error) {
    // We extract the 'detail' from FastAPI (e.g., "Invalid password")
    throw new Error(error.response?.data?.detail || 'Rotatoion failed')
  }
}

export async function getUserData() {
  try {
    const response = await apiClient.get('/users/me')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail||'User data can not be fetched')
  }
}