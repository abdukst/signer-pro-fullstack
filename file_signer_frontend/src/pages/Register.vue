<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="w-full max-w-md p-6 bg-white rounded shadow-xl border border-gray-100">
      <h2 class="text-2xl font-medium mb-4 text-center text-gray-700">
        Register
      </h2>

      <form class="space-y-4 " @submit.prevent="handleRegister">

        <div v-if="errorMessage"
          class="bg-red-100 text-center rounded p-2 mb-4 text-sm border border-red-200 text-red-700">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage"
          class="bg-green-100 text-center rounded p-2 mb-4 text-sm border border-green-200 text-green-700">
          {{ successMessage }}
        </div>

        <label class=" block text-sm font-medium text-gray-700 mb-1">
          Email Address
        </label>
        <input required v-model="form.email" type="email" placeholder="Email"
          class="mt-1 w-full border px-3 py-2 rounded outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200" />

        <label class=" block text-sm font-medium text-gray-700 mb-1">
          Username
        </label>
        <input required v-model="form.username" type="text" placeholder="Username"
          class="mt-1 w-full border px-3 py-2 rounded outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200" />

        <label class=" block text-sm font-medium text-gray-700 mb-1">
          Fullname
        </label>
        <input required v-model="form.fullname" type="text" placeholder="Full name"
          class="mt-1 w-full border px-3 py-2 rounded outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200" />

        <label class=" block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input required v-model="form.password" type="password" placeholder="Password"
          class="mt-1 w-full border px-3 py-2 rounded outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200" />

        <label class=" block text-sm font-medium text-gray-700 mb-1">
          Password Confirm
        </label>
        <input required v-model="form.confirmationPassword" type="password" placeholder="Confirm password"
          class="mt-1 w-full border px-3 py-2 rounded outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200" />

        <button type="submit" :disabled="loading || !!successMessage"
          class="w-full bg-green-500 px-2 py-2 border rounded text-white hover:bg-green-600 disabled:opacity-50">
          <span v-if="!!successMessage">Account Created</span>
          <span v-else-if="loading">Creating account...</span>
          <span v-else>Register</span>
        </button>

      </form>
      <p class="mt-6 text-center text-gray-600 text-sm">
        Already have an account?
        <router-link to="/login" class="ml-1 text-blue-600 hover:underline font-medium hover:text-blue-800">
          Login
        </router-link>
      </p>

    </div>
  </div>
</template>
<script setup>
import { reactive, ref } from 'vue';
import { register } from '../api/auth';
import { useRouter } from 'vue-router'

const form = reactive({
  email: '',
  username: '',
  fullname: '',
  password: '',
  confirmationPassword: ''
})


const router = useRouter()
const loading = ref(false)
const errorMessage = ref("")
const successMessage = ref("")


async function handleRegister() {
  if (form.password !== form.confirmationPassword) {
    errorMessage.value = "Password do not match!"
    return
  }
  loading.value = true
  errorMessage.value = ""
  successMessage.value = ""
  try {
    await register(form)
    successMessage.value = "Registration success! Redirection to login..."
    setTimeout(() => { router.push('/login') }, 1000)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || "Registration failed"
  } finally {
    loading.value = false
  }
}
</script>