import {createRouter, createWebHistory} from 'vue-router'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Home from '../pages/Home.vue'
import { useAuth } from '../auth/authStore'
import Uploadfile from '../pages/Uploadfile.vue'
import VerifyFile from '../pages/VerifyFile.vue'
import IndependentVerification from '../pages/IndependentVerification.vue'

const routes = [
  {
    path:'/',
    redirect:'/home'
  },
  {
    path:'/login',
    component: Login
  },
  {
    path:'/register',
    component: Register 
  },
  {
    path: '/home',
    component: Home,
    meta: {requiresAuth: true}
  },
  {
    path: '/upload',
    component: Uploadfile,
    meta: { requiresAuth: true },
  },
  {
    path: '/verify/:id',
    component: VerifyFile,
    meta: {requiresAuth:true}
  },
  {
    path:'/verification',
    component: IndependentVerification
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes
})

/* Route Gaurd */

router.beforeEach((to)=>{
  const {isAuthenticated} = useAuth()
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return '/login'
  }
  if ((to.path === '/login' || to.path === '/register') && isAuthenticated.value)  {
    return '/home'
  }
})

export default router