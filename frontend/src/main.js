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
  // More specific routes MUST come before general ones
  {
    path: '/:domain/admin',
    component: () => import('./views/AdminView.vue'),
    props: (route) => ({ domain: route.params.domain })
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