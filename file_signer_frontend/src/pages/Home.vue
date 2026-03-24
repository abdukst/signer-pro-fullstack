<template>
  <!-- Main Wrapper with light gray background -->
  <div class="min-h-screen bg-gray-50 pt-24 pb-12 px-4">
    <!-- Professional Navbar -->
    <nav class="bg-white border-b border-gray-200 fixed w-full z-50 top-0 left-0">
      <div class="max-w-screen-2xl flex flex-wrap items-center justify-between mx-auto p-4 ">
        <span class="text-2xl font-bold text-green-600">SignerPro</span>
        <div class="flex items-center space-x-4">
          <span class="text-gray-600 text-sm hidden sm:block">
            Welcome,
            <span class="font-semibold text-gray-900">
              {{ username || 'User' }}
            </span>
          </span>
          <router-link to="/profile"
            class="bg-green-50 hover:bg-green-100 rounded text-gray-600 border border-green-200  font-bold px-4 py-2 text-sm  transition-all duration-150">
            Profile
          </router-link>
          <button @click="logout"
            class="bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 border border-red-100 hover:border-red-200 px-4 py-2 rounded text-sm font-medium transition duration-200">
            Logout
          </button>
        </div>
      </div>
    </nav>
    <!-- Content Area -->
    <div class="max-w-3xl mx-auto">
      <!-- New Header Section -->
      <div class="flex justify-between items-center  mb-8">
        <h1 class="text-2xl font-medium text-gray-800">
          Your Signed Files
        </h1>
        <router-link to="/upload"
          class="bg-green-600 hover:bg-green-700 rounded text-white font-medium px-5 py-2 shadow-sm transition-all duration-150">
          + Sign New File
        </router-link>
      </div>

      <div v-if="isLoadingFiles" class="flex justify-center py-3">
        <div class="animate-spin rounded-full h-10 w-8 border-b-3 border-t-3 border-green-600">
        </div>
      </div>

      <div v-else-if="errorMessage"
        class="w-1/3 mx-auto text-center border py-5 bg-white rounded-xl shadow-sm  border-gray-100">
        <div class="text-red-500 mb-2">⚠️</div>
        <p class="text-sm text-red-600 font-medium">{{ errorMessage }}</p>
        <button @click="refreshPage" class="text-sm text-gray-500 underline hover:text-gray-800">
          Try again
        </button>
      </div>

      <!-- File List -->
      <div v-else>
        <div v-if="files.length === 0"
          class="text-center py-12 bg-white   rounded-xl border border-dashed border-gray-300">
          <p class="text-gray-500"> No files signed yet. </p>
        </div>

        <div v-else class="space-y-4">
          <div v-for="file in files" :key="file.id"
            class="p-5 bg-white rounded-xl shadow-sm border border-gray-100 flex justify-between items-center hover:shadow-md transition">
            <div>
              <p class="font-semibold text-gray-900">{{ file.filename }}</p>
              <p class="text-xm text-gray-400 mt-1">Signed on: {{ (file.created_at) }}</p>
            </div>
            <router-link :to="`/verify/${file.id}`"
              class="text-green-600 hover:text-green-700 font-medium text-sm border border-green-600 px-3 py-1 rounded-md hover:bg-green-50 transition duration-200">
              Verify
            </router-link>

            <button @click="getFileSignatureInfo(file.id)"
              class="text-green-600 hover:text-green-700 font-medium text-sm border border-green-600 px-3 py-1 rounded-md hover:bg-green-50 transition duration-200">
              Inspect
            </button>

          </div>
        </div>
      </div>

    </div>


    <!-- Modal Overlay -->
    <base-model :open-modal="isModalOpen" @closeModal="toggleModal">

      <!-- Use mode="out-in" for a seamless swap -->
      <Transition mode="out-in" enter-active-class="transition duration-100 ease-out"
        enter-from-class="opacity-0 translate-y-2 translate-x-0" enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-50 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0">
        
        <!------------------ Waiting animation --------------->
        <div v-if="isLoadingInfo" class="flex justify-center py-3">
          <div class="animate-spin rounded-full h-10 w-8 border-b-3 border-t-3 border-green-600">
          </div>
        </div>

        <div v-else-if="fileSignatureData" class="space-y-4">
          <!------------------Title--------------------->
          <div class="px-6  border-gray-100 flex justify-between items-center bg-gray-50">
            <h3 class="font-bold text-gray-700">signature Audit Details</h3>
          </div>
          <!---------------- file name ------------------>
          <div class="grid grid-cols-2 gap-4 ">
            <div>
              <label class="text-xs font-bold text-gray-400 uppercase"> Document Name</label>
              <p class="text-gray-900 font-medium px-2 py-1 bg-gray-100">{{ fileSignatureData.filename }} </p>
            </div>
            <div>
              <label class="text-xs font-bold text-gray-400 uppercase">Record ID</label>
              <p class="text-gray-700 px-2 py-1.5 bg-gray-100 text-sm">{{ fileSignatureData.id }} </p>
            </div>
          </div>

          <!---------------- signer email ------------------>
          <div>
            <label class="text-xs font-bold text-gray-400 uppercase"> Signer Identity</label>
            <p class="text-gray-600 font-mono bg-gray-100 px-2 py-1  text-sm break-all">{{
              fileSignatureData.signer_identifier }}
            </p>
          </div>

          <!---------------- Key fingerprint  ------------------>
          <div>
            <label class="text-xs font-bold text-gray-400 uppercase">Key Fingerprint (SHA-256)</label>
            <p class="text-gray-600 font-mono text-xs bg-gray-100 p-2 rounded break-all mt-1">
              {{ fileSignatureData.key_fingerprint }}</p>
          </div>
          <!---------------- fileId signature date  ------------------>
          <div class="grid grid-cols-2 gap-4 pt-2 ">
            <div>
              <label class="text-xs font-bold text-gray-400 uppercase">Key status</label>
              <p class="text-gray-700 py-1 px-2 bg-gray-100 text-sm">
                {{ fileSignatureData?.key_status ? 'active' : 'Revoked on: ' + new
                  Date(fileSignatureData.revoked_at).toLocaleString() }}
              </p>
            </div>
            <div>
              <label class="text-xs font-bold text-gray-400 uppercase">Signature Timestamp</label>
              <p class="text-gray-700 py-1 px-2 bg-gray-100 text-sm">{{ 'Signed on: ' + new
                Date(fileSignatureData.created_at).toLocaleString() }} </p>
            </div>
          </div>
          <!---------------- Buttons section ------------------>
          <div class="grid grid-cols-2">
            <!---------------- Download key Button ------------------>
            <div class="mx-2">
              <label class="text-xs font-bold text-gray-400 uppercase"> Public key </label>
              <button @click="downloadKey"
                class=" w-full mt-2
                flex border
                items-center 
                justify-center bg-white text-green-700 font-medium px-8 py-1 rounded-lg hover:bg-green-50 transition-all duration-200 shadow-md hover:shadow-lg">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download key
              </button>
            </div>
            <!-------------- Download Signature Button ------------------>
            <div class="mx-2">
              <label class="text-xs font-bold text-gray-400 uppercase"> Signature </label>
              <button @click="downloadSignature"
                class=" w-full mt-2
                flex border
                items-center 
                justify-center bg-white text-green-700 font-medium px-8 py-1 rounded-lg hover:bg-green-50 transition-all duration-200 shadow-md hover:shadow-lg">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download .sig File
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </base-model>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { listFiles, getSignatureInspection } from '../api/files';
import { useAuth } from '../auth/authStore';
import router from '../router';
import { triggerDownload } from '../utils/download';
import BaseModel from './BaseModel.vue';
const files = ref([])
const { clearToken, username } = useAuth()

// file loading state
const isLoadingFiles = ref(false)
const errorMessage = ref('')

// Modal State
const fileSignatureData = ref(null)
const isModalOpen = ref(false)
const isLoadingInfo = ref(false)

// state of the popup modal
function toggleModal() {
  isModalOpen.value = !isModalOpen.value
}

onMounted(async () => {
  isLoadingFiles.value = true
  try {
    files.value = await listFiles()
  } catch (error) {
    isLoadingFiles.value = false
    errorMessage.value = error.message
  } finally {
    isLoadingFiles.value = false
  }

})

function logout() {
  clearToken()
  router.push("/login")
}

async function getFileSignatureInfo(fileId) {
  isLoadingInfo.value = true
  isModalOpen.value = true
  try {
    fileSignatureData.value = await getSignatureInspection(fileId)
    console.log(fileSignatureData.value)
  }
  catch (error) {
    console.log(error)
    isLoadingInfo.value = false
    closeModal()
  } finally {
    isLoadingInfo.value = false
  }
}
function closeModal() {
  fileSignatureData.value = null
  isModalOpen.value = false
}

function downloadSignature() {
  triggerDownload(
    fileSignatureData.value.signature,
    `${fileSignatureData.value.filename}.sig`,
    'text/plain'
  )
}

function downloadKey() {
  triggerDownload(
    fileSignatureData.value.public_key,
    `public_key_${username.value}.pem`,
    'application/x-pem-file'
  )
}

const refreshPage = () => {
  window.location.reload();
};
</script>
