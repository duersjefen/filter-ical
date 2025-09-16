import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import i18n from './i18n'
import './styles/tailwind.css'

import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'
import CalendarView from './views/CalendarView.vue'
import ExterPasswordView from './views/ExterPasswordView.vue'

const routes = [
  { 
    path: '/', 
    component: HomeView,
    meta: { requiresAuth: true }
  },
  { 
    path: '/login', 
    component: LoginView,
    meta: { requiresGuest: true }
  },
  { 
    path: '/calendar/:id', 
    component: CalendarView, 
    props: true,
    meta: { requiresAuth: true }
  },
  { 
    path: '/exter', 
    component: ExterPasswordView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const pinia = createPinia()

// Create app instance
const app = createApp(App).use(pinia).use(i18n)

// Add navigation guards after pinia is available
router.beforeEach((to, from, next) => {
  try {
    // Handle community routes separately (they have their own authentication)
    if (to.path.startsWith('/exter')) {
      next()
      return
    }
    
    const savedUser = localStorage.getItem('icalViewer_user')
    let isLoggedIn = false
    
    if (savedUser) {
      const parsed = JSON.parse(savedUser)
      isLoggedIn = !!(parsed && parsed.username && parsed.loggedIn)
    }
    
    // If route requires auth and user is not logged in
    if (to.meta.requiresAuth && !isLoggedIn) {
      next('/login')
      return
    }
    
    // If route requires guest (login page) and user is logged in
    if (to.meta.requiresGuest && isLoggedIn) {
      next('/')
      return
    }
    
    next()
  } catch (error) {
    console.warn('Navigation guard error:', error)
    // Clear corrupted data and redirect to login
    localStorage.removeItem('icalViewer_user')
    if (to.meta.requiresAuth) {
      next('/login')
    } else {
      next()
    }
  }
})

app.use(router).mount('#app')