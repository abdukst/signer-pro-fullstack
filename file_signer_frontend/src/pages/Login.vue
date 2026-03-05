<template>

  <div class="min-h-screen bg-gray-50 pt-40 pb-12 px-4">
    <nav class="border-b border-gray-200 w-full fixed top-0 left-0  z-50 ">
      <div class="max-w-screen-2xl flex flex-wrap items-center justify-between mx-auto p-4 ">
        <span class="text-2xl font-bold text-green-600">SignerPro</span>
      <router-link to="/verification" class="bg-green-600 hover:bg-green-700 rounded text-white font-medium px-5 py-2 shadow-sm transition-all duration-150">
        verification
      </router-link>
      </div>
    </nav>
    
    <div class="w-full mx-auto max-w-md p-6   bg-white rounded shadow-xl border border-gray-100">
      <h2 class="text-xl font-bold mb-4 text-center text-gray-700">
        Login
      </h2>
      <form class="space-y-4" @submit.prevent="handleLogin">

        <div>
          <div v-if="errorMessage"
            class="bg-red-100 text-red-700 p-2 mb-4 rounded text-sm border border-red-200 text-center ">
            {{ errorMessage }}
          </div>

          <label class="block text-sm font-medium text-gray-700">
            Email
          </label>

          <input type="email" v-model="email" required
            class="mt-1 w-full border rounded px-3 py-2 outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200"
            placeholder="amir@example" />

        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input type="password" v-model="password" required
            class="mt-1 w-full border rounded px-3 py-2 outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200"
            placeholder="••••••••" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full bg-green-500 text-white  py-2 hover:bg-green-600 rounded disabled:opacity-50">
          {{ loading ? 'Signing in...' : 'Login' }}
        </button>
      </form>
      <p class="mt-6 text-center text-sm text-gray-600 ">
        Don't have an account?
        <router-link to="/register" class="text-blue-600 hover:underline ml-1 font-medium hover:text-blue-800 ">
          Register
        </router-link>
      </p>

    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '../api/auth'
import { useAuth } from '../auth/authStore'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const { setToken, setUsername } = useAuth()
const router = useRouter()
//Track waiting the server
const loading = ref(false)
//Hold error messege
const errorMessage = ref("")

async function handleLogin() {
  errorMessage.value = "" // clean old error
  loading.value = true // start waiting the server.
  try {
    const data = await login(email.value, password.value)
    setToken(data.access_token)
    setUsername(data.user.username)
    router.push('/home')
  } catch (error) {
    console.log(error)
    errorMessage.value = error.response?.data?.detail || "Something went wrong. Please try again."
  } finally {
    loading.value = false // Stop waiting
  }
}
</script>
