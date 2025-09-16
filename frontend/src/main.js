import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import i18n from './i18n'
import './styles/tailwind.css'

import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'
import CalendarView from './views/CalendarView.vue'

const routes = [
  { 
    path: '/', 
    redirect: () => {
      // Check if user is already logged in via localStorage
      try {
        const savedUser = localStorage.getItem('icalViewer_user')
        if (savedUser) {
          const parsed = JSON.parse(savedUser)
          if (parsed && parsed.username && parsed.loggedIn) {
            return '/home'
          }
        }
      } catch (error) {
        console.warn('Error checking saved user:', error)
      }
      return '/login'
    }
  },
  { 
    path: '/login', 
    component: LoginView,
    meta: { requiresGuest: true }
  },
  { 
    path: '/home', 
    component: HomeView,
    meta: { requiresAuth: true }
  },
  { 
    path: '/calendar/:id', 
    component: CalendarView, 
    props: true,
    meta: { requiresAuth: true }
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
      next('/home')
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