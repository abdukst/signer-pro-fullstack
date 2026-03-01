<template>
  <div class="max-w-xl mx-auto mt-10 p-6 bg-white border border-blue-100 rounded shadow-2xl">
    <h2 class="text-xl font-medium border rounded border-blue-200 p-2 mb-4">
      Verify File
    </h2>
    <input type="file" @change="onFileChange" class="border p-1  bg-blue-700 text-white" >

    <button @click="verify" :disabled="!selectedFile" class="py-1 ml-6 px-4 border text-white bg-green-600 rounded">
      Verify
    </button>
    <div v-if="result !== null" class="border border-blue-200 mt-4 font-medium">
      <p v-if="result.valid" class="text-green-600">File is valid (unchanged)</p>
      <p v-else class="text-red-600"> File has been modified</p>
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

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
}

async function verify() {
  try {
    result.value = await verifyFile(fileId, selectedFile.value)
  } catch (error) {
    alert(error)
  }
}
</script>