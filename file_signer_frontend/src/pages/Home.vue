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
          <button @click="logout"
            class="bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 border border-red-100 hover:border-red-200 px-4 py-2 rounded text-sm font-medium transition duration-200">
            Logout
          </button>
        </div>
      </div>
    </nav>
    <!-- Content Area -->
    <div class="max-w-3xl mx-auto 
  ">
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

      <!-- File List -->
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
    <!-- Modal Overlay -->
    <div v-if="isModalOpen"
      class="fixed  inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <!---Modal Content-->
      <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden border border-gray-200">
        <!--Header-->
        <div class="px-6 py-3 border-b border-gray-200 flex justify-between items-center bg-gray-100">
          <h3 class="font-bold text-gray-700">signature Audit Details</h3>
          <button @click="closeModal" class="text-red-500 hover:text-red-600 font-extrabold text-2xl">&times;</button>
        </div>
        <!--Body-->
        <div class="p-5">
          <div v-if="isLoadingInfo" class="flex justify-center py-3">
            <div class="animate-spin rounded-full h-10 w-8 border-b-3 border-t-3 border-green-600"></div>
          </div>

          <div v-else-if="fileSignatureData" class="space-y-4">
            <div>
              <label class="text-xs font-bold text-gray-400 uppercase"> Document Name</label>
              <p class="text-gray-900 font-medium">{{ fileSignatureData.filename }} </p>
            </div>

            <div>
              <label class="text-xs font-bold text-gray-400 uppercase"> Signer Identity</label>
              <p class="text-gray-600 font-mono bg-gray-100 px-2 py-1  text-sm break-all">{{
                fileSignatureData.signer_identifier }}
              </p>
            </div>

            <div>
              <label class="text-xs font-bold text-gray-400 uppercase"> Signature </label>
              <a :href="sigDownloadUrl" :download="`${fileSignatureData.filename}.sig`"
                class="
                flex border
                items-center mx-5
                justify-center bg-white text-green-700 font-medium px-8 py-1 rounded-lg hover:bg-green-50 transition-all duration-200 shadow-md hover:shadow-lg">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download File
              </a>
            </div>

            <div>
              <label class="text-xs font-bold text-gray-400 uppercase">Key Fingerprint (SHA-256)</label>
              <p class="text-gray-600 font-mono text-xs bg-gray-100 p-2 rounded break-all mt-1">
                {{ fileSignatureData.key_fingerprint }}</p>
            </div>

            <div class="grid grid-cols-2 gap-4 pt-2 ">
              <div>
                <label class="text-xs font-bold text-gray-400 uppercase">Record ID</label>
                <p class="text-gray-700 py-1 px-2 bg-gray-100 text-sm">{{ fileSignatureData.id }} </p>
              </div>
              <div>
                <label class="text-xs font-bold text-gray-400 uppercase">Timestamp</label>
                <p class="text-gray-700 py-1 px-2 bg-gray-100 text-sm">{{ new Date(fileSignatureData.created_at).toLocaleString() }} </p>
              </div>
            </div>
          </div>
        </div>
        <!---Footer-->
        <div class="px-6 py-3 text-right border border-gray-200 bg-gray-100">
          <button @click="closeModal"
            class="bg-white text-red-600 border border-red-200 px-4 py-1 rounded text-sm font-medium hover:bg-red-100">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { listFiles, getSignatureInspection } from '../api/files';
import { useAuth } from '../auth/authStore';
import router from '../router';
const files = ref([])
const { clearToken, username } = useAuth()
// Modal State
const fileSignatureData = ref(null)
const isModalOpen = ref(false)
const isLoadingInfo = ref(false)
const sigDownloadUrl = ref(null)

onMounted(async () => {
  try {
    files.value = await listFiles()
  } catch (error) {
    console.error("Home load failed:", error);
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
    sigDownloadUrl.value = createDownloadUrl(
      fileSignatureData.value.signature,
      sigDownloadUrl.value
    )
  }
  catch (error) {
    console.log(error)
    closeModal()
  } finally {
    isLoadingInfo.value = false
  }
}
function closeModal() {
  sigDownloadUrl.value = null
  fileSignatureData.value = null
  isModalOpen.value = false
}

function createDownloadUrl(signature, oldUrl) {
  //Create a "Blob" (Binary Large Object) from the string.
  //We treat the Base64 string as plain text for the file content.
  const blob = new Blob([signature], { type: 'text/plain' })
  if (oldUrl) {
    window.URL.revokeObjectURL(oldUrl)
  }
  return window.URL.createObjectURL(blob)
}
</script>
