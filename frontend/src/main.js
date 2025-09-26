import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import i18n from './i18n'
import './styles/tailwind.css'

import HomeView from './views/HomeView.vue'
import CalendarView from './views/CalendarView.vue'
import DomainView from './views/DomainView.vue'
import AdminView from './views/AdminView.vue'

const routes = [
  { 
    path: '/', 
    redirect: '/home'
  },
  { 
    path: '/home', 
    component: HomeView
  },
  { 
    path: '/calendar/:id', 
    component: CalendarView, 
    props: true
  },
  // More specific routes MUST come before general ones
  { 
    path: '/:domain/admin', 
    component: AdminView, 
    props: (route) => ({ domain: route.params.domain })
  },
  { 
    path: '/:domain', 
    component: DomainView, 
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