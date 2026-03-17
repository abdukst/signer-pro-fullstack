<template>
  <Teleport to="body">
    <Transition
        
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"

      
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"  
    >
    <div v-if="openModal" class="absolute w-full h-screen z-50  p-4 top-0 backdrop-blur-sm ">

      
       <!-- INNER MODAL TRANSITION: Handles the scaling pop -->
       <Transition
          appear
          enter-active-class="transition duration-200 delay-50 ease-out"
          enter-from-class="opacity-0 scale-90"
          enter-to-class="opacity-100 scale-100"
       >
       <!-- The White Box -->
      <div class="relative top-1/6 max-w-xl mx-auto bg-white rounded-lg">
        <!-----------------------Header------------------------------>
        <header class="flex justify-between bg-gray-100  border border-gray-200 px-2 py-2 rounded-t-lg">
          <div>
            <span class="text-xl font-bold text-green-600">
              SignerPro
            </span>
          </div>
          <div>
            <button @click="$emit('closeModal')">✕</button>
          </div>
        </header>
        <!-----------------------Main------------------------------>
        <main class="flex flex-col min-h-60  justify-center items-center border border-gray-200 rounded-b-lg px-2 py-4">
        <!-- The Slot: to put ANY HTML inside from the parent -->
          <slot></slot>
        </main>
      </div>
      </Transition>
    </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, Transition } from 'vue';
defineProps(['openModal'])
defineEmits(['closeModal'])
</script>
