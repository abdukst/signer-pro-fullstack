import { ref, computed } from "vue";

const token = ref(localStorage.getItem('token'))
const username = ref(localStorage.getItem('username'))

function setToken(newToken) {
  token.value = newToken
  localStorage.setItem('token', newToken)
}

function setUsername(newUsername){
  username.value = newUsername
  localStorage.setItem('username', newUsername)
}

function clearToken() {
  token.value = null
  username.value = null
  localStorage.removeItem('token')
  localStorage.removeItem('username')
}
const isAuthenticated = computed(() => !!token.value) 
export function useAuth() {
  return {
    token,
    setToken,
    clearToken,
    isAuthenticated,
    setUsername,
    username
  }
}