<template>
  <div class="min-h-dvh bg-gray-200 pt-24 pb-12 px-4 ">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 fixed w-full z-50 top-0 left-0">
      <div class="max-w-screen-2xl flex flex-wrap items-center justify-between mx-auto p-4 ">
        <!-- The Branding -->
        <div class="logo font-bold">
          <span class="text-2xl font-bold text-green-600">SignerPro</span>
        </div>

        <!-- The Navigation -->
        <nav>
          <ul class=" flex gap-4">
            <li><router-link to="/"
                class="bg-green-50 hover:bg-green-100 rounded text-gray-600 border border-green-200  font-bold px-4 py-2 text-sm  transition-all duration-150">Home</router-link>
            </li>
          </ul>
        </nav>
      </div>
    </header>

    <main class="bg-white max-w-2xl mx-auto">
      <!-- New Header Section -->
      <div class="space-y-4">

        <div
          class="p-5 bg-white rounded-xl shadow-sm border border-gray-100 flex justify-between items-center hover:shadow-md transition">

          <BaseModel :open-modal="isModalOpen" @closeModal="toggleModal" class="">
            <div class="w-full h-full min-h-60 grow flex flex-col justify-center items-center overflow-hidden">
              <!-- Use mode="out-in" for a seamless swap -->
              <Transition mode="out-in" enter-active-class="transition duration-200 ease-out"
                enter-from-class="opacity-0 translate-y-2 translate-x-0" enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100"
                leave-to-class="opacity-0">

                <!--  Key rotation  Form -->
                <form key="form" v-if="!loading && !result && !errorMessage" class="space-y-4 w-full"
                  @submit.prevent="rotateKey">
                  <!--  THE WARNING BOX -->
                  <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-md">
                    <div class="flex items-start">
                      <div class="shrink-0">
                        <svg class="h-5 w-5 text-amber-500" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd"
                            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                            clip-rule="evenodd" />
                        </svg>
                      </div>
                      <div class="ml-3 ">
                        <p class="text-sm font-medium text-amber-800">
                          Deactivating this key prevents you from signing new documents using it. You can only use it to
                          verify the documents you signed with it.
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- THE PASSWORD SECTION -->
                  <div class="space-y-2">
                    <label class="block text-sm font-bold text-gray-700 uppercase tracking-wide">
                      Confirm Password
                    </label>
                    <input type="password" v-model="password" required class="w-full border-2 border-gray-200 rounded-lg px-4 py-3 
             outline-none transition-all duration-200 hover:border-red-200
             focus:border-red-500 focus:ring-2 focus:ring-red-100" placeholder="Enter password to confirm" />
                    <p class="text-xs text-gray-400">Please enter your key password to proceed.</p>
                  </div>
                  <!--  THE DANGER BUTTON -->
                  <button type="submit" :disabled="loading"
                    class="w-full 
                  bg-red-50 hover:bg-red-100 text-red-800 hover:text-red-600 border border-red-100 hover:border-red-200 px-4 py-2  font-medium transition-all  duration-200 hover:shadow-md rounded-lg active:scale-95 disabled:opacity-50">
                    Deactivate Key
                  </button>
                </form>

                <!--  The Loading Spinner -->
                <div v-else-if="loading" key="loading" class="h-full flex flex-col items-center justify-center">
                  <!-- Simple Tailwind Spinner -->
                  <div class="animate-spin rounded-full h-15 w-15 border-b-3 border-red-500 mb-6"></div>
                  <p class="text-gray-500 animate-pulse font-medium">Deactivating key...</p>
                </div>

                <!-- Option 3: The Error Message -->
                <div v-else-if="errorMessage" key="error"
                  class="h-full flex flex-col items-center justify-center text-center">
                  <p class="text-red-600 font-medium">{{ errorMessage }}</p>
                  <button @click="errorMessage = null" class="mt-4 text-sm text-gray-500 underline hover:text-gray-800">
                    Try again
                  </button>
                </div>

                <!--  Success Result  -->
                <div key="success" v-else-if="result"
                  class="h-full flex flex-col items-center justify-center text-center">
                  <!-- Success Icon -->
                  <div class="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                    <svg class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 class="text-xl font-bold text-gray-900">Success!</h3>
                  <p class="text-green-600 font-medium mt-1">{{ result }}</p>
                </div>
              </Transition>
            </div>
          </BaseModel>


          <div>
            <p class="font-semibold text-gray-900"> Your key : </p>
          </div>
          <button @click="toggleModal"
            class="
             text-green-600 hover:text-green-700 font-medium text-sm border border-green-600 px-3 py-2 rounded-md hover:bg-green-50 transition duration-200">
            Download public key
          </button>
          <button @click="toggleModal"
            class="
             bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 border border-red-100 hover:border-red-200 px-4 py-2 rounded-md text-sm font-medium transition duration-200">
            Deactivate your Key
          </button>
        </div>
      </div>
    </main>
  </div>



</template>
<script setup>
import { ref } from 'vue';
import { rotateUserKeys } from '../api/auth';
import BaseModel from './BaseModel.vue';

//inpute from the modal
const password = ref('')


const result = ref(null)
const errorMessage = ref(null)
const loading = ref(false)



// state of the popup modal
const isModalOpen = ref(false)
function toggleModal() {
  result.value = null
  errorMessage.value = null
  isModalOpen.value = !isModalOpen.value
}

async function rotateKey() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await rotateUserKeys(password.value)
    result.value = response.message
  } catch (e) {
    errorMessage.value = e
  } finally {
    loading.value = false
    password.value = ''
  }
}
</script>