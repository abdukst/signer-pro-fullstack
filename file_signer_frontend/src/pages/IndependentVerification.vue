<template>
  <div class="min-h-screen bg-gray-200 pt-20 pb-12 px-4">
    <!-- Public Header -->
    <header class="max-w-3xl mx-auto mb-10 text-center">
      <h1 class="text-2xl font-bold text-green-600 mb-2">
        SignerPro
      </h1>
      <p class="text-gray-500">
        Independent Document Verification
      </p>
    </header>
    <!--Main section-->
    <main class=" max-w-2xl mx-auto space-y-2">
      <!-- Card Section -->
      <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 ">
        <form @submit.prevent="verifyIndependent" class="space-y-6">
          <!-- 1. Original File Input -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">1. Original File</label>
            <input class="
            
            text-sm
            p-2 
            w-full 
            outline-none
            border 
            border-gray-300
            text-gray-400
            rounded 
            focus:ring-2
             focus:ring-green-200 
             hover:border-green-600
             transition-all duration-150
              " type="file" required @change="e => originalFile = e.target.files[0]">
          </div>

          <!-- 2. Signature File Input -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">2. Signature File (.sig)</label>
            <input class="
            text-sm
            p-2 
            w-full 
            outline-none
            border 
            border-gray-300
            text-gray-400
            rounded 
            focus:ring-2
             focus:ring-green-200 
             hover:border-green-600
             transition-all duration-150
              " type="file" required @change="e => signature = e.target.files[0]">
          </div>

          <!-- 3. Public Key Input -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">3. Signer's Public Key</label>
            <textarea v-model="publicKey" required rows="4" placeholder="Paste the public key here..." class="
            p-2
            text-sm
            outline-none
            w-full
            rounded
            border
            border-gray-300
            focus:ring-1
             focus:ring-green-200 
             hover:border-green-600
             transition-all 
             duration-100
            ">
            </textarea>
            <button type="submit"
              class="w-full bg-green-600 text-white font-bold py-2 rounded hover:bg-green-700 transition shadow-md">
              Verifying
            </button>
          </div>
        </form>
      </div>
      <!-------------- Result Card -------------------->
      <div>
        <div v-if="result !== null || error" >
          <!-- Result True (Verification Success)-->
           <div v-if="result" class="border border-green-200 bg-green-50 text-center p-6 rounded-xl ">
            <span class="text-4xl text-green-600 block mb-2">✓</span>
            <h3 class="text-xl font-bold text-green-900 ">Document is Authentic</h3>
            <p class="text-green-700">The signature matches the file and the public key provided.</p>
           </div>
           <!--Result False (Verification failed)-->
           <div v-else class="bg-red-50 border border-red-200 p-6 rounded-xl text-center">
            <span class="text-red-600 text-4xl block mb-2">
              ✕
            </span>
            <h3 class="text-xl font-bold text-red-900">
              Verification Failed
            </h3>
            <p class="text-red-700">
              {{error}}
            </p>
           </div>

        </div>
        <div v-else class="text-center border border-dashed rounded-xl py-15 bg-white border-gray-300 shadow">
          <p class="text-gray-500 ">waiting result</p>
        </div>


      </div>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { verifySigIndependent } from '../api/files';

// data from user
const originalFile = ref(null)
const signature = ref(null)
const publicKey = ref('')
// UI State
const result = ref(null)
const loading = ref(false)
const error = ref(null)

async function verifyIndependent() {
  result.value = null
  loading.value = true
  error.value = null

  try {
    result.value = await verifySigIndependent(
      originalFile.value,
      signature.value,
       publicKey.value
      )
    
  } catch (e) {
    error.value = e
    console.log(error)
  } finally {
    loading.value = false
  }

}

</script>