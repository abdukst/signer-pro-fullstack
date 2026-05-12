import { createApp, Transition } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

const options = {
    position: "top-center",
    timeout: 3000,
    closeOnClick: true,
    transition: "global-toast",
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false
}


createApp(App).use(router).use(Toast, options).mount('#app')

