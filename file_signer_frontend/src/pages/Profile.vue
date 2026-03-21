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
    <!-- THE PAGE WRAPPER -->
    <main class="max-w-5xl mx-auto px-4">

      <!-- THE BENTO GRID -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">


        <!-- Box 1: Identity (1/3 of the width) -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 ">

          <div v-if="userDataError" class="text-center p-4">
            <div class="text-red-500 mb-2">⚠️</div>
            <p class="text-sm text-red-600 font-medium">{{ userDataError }}</p>

            <button @click="refreshPage" class="mt-4 text-sm text-gray-500 underline hover:text-gray-800">
              Try again
            </button>
          </div>

          <div v-if="userData" class="flex flex-col items-center text-center">
            <!-- 1. The Avatar Circle -->
            <div
              class="w-20 h-20 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-2xl font-bold mb-4 border-2 border-white shadow-sm">
              JD
            </div>
            <!-- 2. Name and Title -->
            <h2 class="text-xl font-bold text-gray-900 leading-tight">
              {{ userData?.fullname }}
            </h2>
            <p class="text-sm font-medium text-gray-500 mt-1">Authorized Signer
            </p>
            <!-- 3. The Detail List -->
            <div class="w-full mt-8 pt-6 border-t border-gray-200 space-y-5 text-left">
              <div>
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-1">
                  Username
                </label>
                <p class="text-sm font-semibold text-gray-700">
                  {{ userData?.username }}
                </p>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-1">
                  Email Address
                </label>
                <p class="text-sm font-semibold text-gray-700">
                  {{ userData?.email }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Box 2: Security Hub (2/3 of the width) -->
        <div v-if="userData" class="md:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <!-- Security content will go here -->
          <div class="flex flex-col h-full">
            <!-- 1. Header with Status Badge -->
            <div class="flex justify-between items-start mb-8">
              <div>
                <h2 class="text-xl font-bold text-gray-900">
                  Security Assets
                </h2>
                <p class="text-sm text-gray-500 mt-1">
                  Manage your cryptographic identity and keys.
                </p>
              </div>

              <!----------- The Active Badge --------->
               <!-- 1. ACTIVE STATE -->
              <span v-if="userData?.key_status"
                class="inline-flex items-center px-3 py-1 bg-green-50 rounded-full text-xs font-bold text-green-700 border border-green-100 shadow-sm">
                <span class="w-2 h-2 bg-green-700 rounded-full mr-1 animate-pulse">
                </span>
                Active
              </span>
              <!-- 2. DEACTIVATED STATE -->
              <span v-else
                class="inline-flex items-center px-3 py-1 bg-red-50 rounded-full text-xs font-bold text-red-700 border border-red-100 shadow-sm">
                <span class="w-2 h-2 bg-red-600 rounded-full mr-2"></span>
                Deactivated
              </span>
            </div>

            <!-- 2. Technical Data Area -->
            <div v-if="userData?.key_status" class="grid grid-cols-1 gap-6">

              <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Signing
                  Identity</label>
                <p class="text-sm font-mono text-gray-700 break-all">
                  CN={{ userData?.fullname }}, O=SignerPro, C=DE
                </p>
              </div>

              <!-- Key Fingerprint Row -->
              <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Active Key
                  Fingerprint</label>
                <div class="flex items-center bg-white p-3 rounded-lg border border-gray-200 shadow-inner">
                  <code class="text-xs font-mono text-blue-600 break-all">
            {{ userData?.active_key_fingerprint }}
           </code>
                </div>
              </div>
            </div>

            <!-- 3. ACTION ZONE -->

            <div v-if="userData?.key_status" class="mt-8 pt-6 border-t border-gray-100">

              <!-- THE DANGER BOX: A "contained threat" area -->
              <div class="p-5  rounded-2xl border border-red-100 flex flex-col justify-between items-center gap-4">

                <div class="w-full text-start">
                  <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2"> Your Public key : </label>
                </div>

                <div
                  class="w-full flex justify-between items-center flex-col sm:flex-row gap-3 bg-amber-300 px-3  p-3 rounded-lg border border-gray-200 shadow-inner">

                  <!-- Button 1: Download -->
                  <button @click="downloadKey"
                    class="w-full sm:w-1/3 flex items-center justify-center whitespace-nowrap overflow-hidden gap-1 text-green-600 hover:text-green-700 font-medium text-sm border border-green-600 px-2 py-2.5 rounded-md hover:bg-green-50 transition-all duration-300">
                    <svg class="w-4 h-4 shrink-0 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />

                    </svg>
                    Download key
                  </button>

                  <!-- Button 2: Deactivate -->
                  <button @click="toggleModal"
                    class="w-full sm:w-1/3 flex items-center justify-center whitespace-nowrap overflow-hidden px-2 py-2.5 
             bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 border border-red-600 hover:border-red-700 rounded-lg text-sm font-medium transition-all duration-300">
                    Deactivate Key
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

    </main>


    <!-- 3. THE BASE MODAL (Place it here!) -->
    <!-- It stays "invisible" until toggleModal is called -->
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
          <div key="success" v-else-if="result" class="h-full flex flex-col items-center justify-center text-center">
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
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue';
import { getUserData, rotateUserKeys } from '../api/auth';
import BaseModel from './BaseModel.vue';
import { triggerDownload } from '../utils/download';

//inpute from the modal
const password = ref('')

// key rotation
const result = ref(null)
const errorMessage = ref(null)
const loading = ref(false)

// user data
const userData = ref(null)
const userDataError = ref(null)

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
     // Re-fetch the fresh data 
    if(result.value){
      await getData()
    }
  } catch (e) {
    errorMessage.value = e.message
    console.log(e)
  } finally {
    loading.value = false
    password.value = ''
  }
}

async function getData() {
  try {
    const response = await getUserData()
    userData.value = response
    console.log(response)
  } catch (e) {
    userDataError.value = e.message
    console.log(e.message)
  }
}

onMounted(() => {
  getData()
})

const refreshPage = () => {
  window.location.reload();
};

function downloadKey() {
  if (!userData.value?.active_public_key) return

  triggerDownload(
    userData.value.active_public_key,
    `public_key_${userData.value.username}.pem`,
    'application/x-pem-file'
  )
}

</script>