import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import i18n from './i18n'
import './styles/tailwind.css'

// Use dynamic imports for code splitting - each route becomes a separate chunk
const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    component: () => import('./views/HomeView.vue')
  },
  {
    path: '/calendar/:id',
    component: () => import('./views/CalendarView.vue'),
    props: true
  },
  {
    path: '/admin',
    component: () => import('./views/AdminPanelView.vue')
  },
  {
    path: '/admin/reset-password',
    component: () => import('./views/AdminResetPasswordView.vue')
  },
  {
    path: '/login',
    component: () => import('./views/LoginView.vue')
  },
  {
    path: '/reset-password',
    component: () => import('./views/PasswordResetView.vue')
  },
  {
    path: '/profile',
    component: () => import('./views/UserProfileView.vue')
  },
  {
    path: '/contact',
    component: () => import('./views/ContactView.vue')
  },
  // More specific routes MUST come before general ones
  {
    path: '/:domain/admin',
    component: () => import('./views/AdminView.vue'),
    props: (route) => ({ domain: route.params.domain }),
    beforeEnter: (to, from, next) => {
      // Check if user is logged in by checking for auth token
      const authToken = localStorage.getItem('auth_token')
      if (!authToken) {
        // Not logged in, redirect to login with return URL
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
      } else {
        // Logged in, allow access
        next()
      }
    }
  },
  {
    path: '/:domain',
    component: () => import('./views/DomainView.vue'),
    props: (route) => ({ domain: route.params.domain })
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const pinia = createPinia()

// Create app instance
const app = createApp(App).use(pinia).use(i18n)

// No authentication guards needed for public-first access

app.use(router).mount('#app')