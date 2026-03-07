<template>
  <div class="
  min-h-screen 
bg-gray-50 
pt-24
pb-12
px-4">
    <div class="
     
     max-w-3xl
     mx-auto
     
     
   
   space-y-4
   ">
      <h2 class="
    text-2xl
    text-center 
    font-medium
    text-gray-800
    mb-8">
        Sign File
      </h2>

      <div class="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
        <form @submit.prevent="upload" class="space-y-6">
          <div>
            <input required type="file" @change="onFileChange" class="
        mt-1 w-full border px-3 py-2 rounded-lg outline-none transition-all duration-200 focus:border-green-500 focus:ring-2 focus:ring-green-200
        hover:border-green-600
        text-gray-400
        border-gray-300
        " />
          </div>

          <div>
            <input required type="password" v-model="password" placeholder="password" class="w-full px-3 outline-none py-2 border rounded-lg focus:ring-2 focus:ring-green-200 focus:border-green-500 hover:border-green-600 transition-all duration-200
        border-gray-300
        text-gray-900
        ">
          </div>
          <div class="flex justify-center">
            <button
              class="w-full inline-flex items-center justify-center bg-green-600 text-white font-medium shadow-sm hover:bg-green-700 rounded-lg py-1 px-3 transition-all duration-150 disabled:bg-gray-400"
              :disabled="loading">
              <span v-if="loading">loading</span>
              <span v-else>Upload & Sign </span>
            </button>
          </div>
        </form>
      </div>

      <!-- Success Message & Download Button -->
      <div v-if="result" class="mt-8 p-8 bg-green-50 border border-green-100 rounded-xl text-center shadow-sm">
        <div class="inline-flex items-center justify-center w-12 h-12 bg-green-100 text-green-600 rounded-full mb-4">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>

        <h3 class="text-xl font-semibold text-green-900 mb-2">File Signed Successfully!</h3>
        <p class="text-green-700 mb-6">Your signature file is ready for download.</p>

        <a :href="downloadUrl" :download="signatureFileName"
          class="inline-flex items-center justify-center bg-green-600 text-white font-medium px-8 py-3 rounded-lg hover:bg-green-700 transition-all duration-200 shadow-md hover:shadow-lg">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
          Download .sig File
        </a>
      </div>
      <!--  Error  -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 py-15 rounded-xl text-center">
        <p class="text-red-600">{{ error }}</p>
      </div>
      <!-- "Empty State" shown only when no result exists -->
      <div v-else class="text-center py-15 bg-white rounded-xl border border-dashed border-gray-300">
        <p class="text-gray-500">No file signed yet.</p>
      </div>

    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { signFile } from '../api/files';
const selectedFile = ref(null)
const password = ref("")
const result = ref(null)
const signatureFileName = ref('')
const downloadUrl = ref(null)

const loading = ref(false)
const error = ref(null)

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
}

function getSigFilenameFromResponse(response, fallbackName) {
  // 1. Grab the header
  const cdHeader = response.headers['content-disposition']
  // 2. Default filename if header is missing

  if (cdHeader) {
    const sigFileNameMatch = cdHeader.match(/filename=(.+)/)
    return sigFileNameMatch ? sigFileNameMatch[1] : `${fallbackName}.sig`
  }
  return `${fallbackName}.sig`
}

function createDownloadUrl(response, oldUrl) {
  const blob = response.data
  if (oldUrl) {
    console.log("ok...")
    window.URL.revokeObjectURL(oldUrl)
  }
  return window.URL.createObjectURL(blob)
}
async function upload() {
  loading.value = true
  error.value = null
  result.value = null
  try {
    const response = await signFile(selectedFile.value, password.value)
    signatureFileName.value = getSigFilenameFromResponse(response, selectedFile.value.name)
    downloadUrl.value = createDownloadUrl(response, downloadUrl.value)
    result.value = { success: true }
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }

}

</script>