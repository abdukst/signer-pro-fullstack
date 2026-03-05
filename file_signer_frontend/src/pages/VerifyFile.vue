<template>
  <div class="min-h-screen bg-gray-200 pt-20 pb-12 space-y-8">
    <div class=" max-w-2xl mx-auto text-center space-y-4">
      <h1 class="text-3xl font-bold text-green-600">
        SignerPro
      </h1>
      <p class="text-xl font-semibold text-gray-500 ">
        Signature verification
      </p>
    </div>
    <div class="max-w-xl mx-auto space-y-2  p-8 bg-white border border-gray-200 rounded-2xl  shadow-sm ">
      <div>
        <input type="file" @change="onFileChange"
          class="w-full border text-gray-400 border-gray-200 p-1 rounded bg-gray-50 ">
      </div>
      <div>
        <button @click="verify" :disabled="!selectedFile"
          class="w-full py-1 px-4 border text-white bg-green-600 rounded">
          Verify
        </button>
      </div>

    </div>
    <div class="max-w-xl mx-auto bg-white rounded-xl">
      <div v-if="result !== null" class="border border-blue-200 mt-4 font-medium">
        <p v-if="result.valid" class="text-green-600">File is valid (unchanged)</p>
        <p v-else class="text-red-600"> File has been modified</p>
      </div>
      <div v-else class="text-center border border-dashed rounded-xl py-15 bg-white border-gray-300 shadow">
        <p v-if="errorMessage" class="text-red-600">{{ errorMessage }}</p>
        <p v-else class="text-gray-500 ">waiting result</p>
      </div>
    </div>
  </div>

</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { verifyFile } from '../api/files';

const route = useRoute()
const fileId = route.params.id

const selectedFile = ref(null)
const result = ref(null)
const errorMessage = ref("")

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
}

async function verify() {
  errorMessage.value = ""
  try {
    result.value = await verifyFile(fileId, selectedFile.value)
  } catch (error) {
    errorMessage.value = error
    console.log(errorMessage.value)
  } 
}
</script>