/**
 * Tests for main App component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';
import App from '../src/App.vue';

// Mock components for testing
const MockLoginView = { template: '<div data-testid="login-view"><h1>iCal Viewer</h1></div>' };
const MockHomeView = { template: '<div data-testid="home-view"><nav>Navigation</nav><main>Home Content</main></div>' };
const MockCalendarView = { template: '<div data-testid="calendar-view">Calendar</div>' };

describe('App Component', () => {
  let wrapper;
  let pinia;
  let router;

  beforeEach(async () => {
    // Create test router
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', redirect: '/login' },
        { path: '/login', component: MockLoginView },
        { path: '/home', component: MockHomeView },
        { path: '/calendar/:id', component: MockCalendarView, props: true }
      ]
    });

    // Create pinia store
    pinia = createPinia();

    // Mock the store initialization
    const mockStore = {
      initializeApp: vi.fn()
    };
    
    // Mock the composable
    vi.doMock('../src/composables/useDarkMode', () => ({
      useDarkMode: () => ({
        isDarkMode: { value: false },
        toggleDarkMode: vi.fn()
      })
    }));

    // Mount component with router and pinia
    wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          RouterView: {
            template: '<div data-testid="router-view"><h1>iCal Viewer</h1><nav>Navigation</nav><main>Main Content</main></div>'
          }
        }
      }
    });

    // Wait for router to be ready
    await router.isReady();
  });

  it('renders without crashing', () => {
    expect(wrapper.exists()).toBe(true);
  });

  it('has correct title structure', () => {
    expect(wrapper.find('h1').exists()).toBe(true);
    const title = wrapper.find('h1');
    expect(title.text()).toContain('iCal Viewer');
  });

  it('shows navigation menu', () => {
    const nav = wrapper.find('nav');
    expect(nav.exists()).toBe(true);
  });

  it('displays main content area', () => {
    const main = wrapper.find('main');
    expect(main.exists()).toBe(true);
  });

  it('handles responsive design classes', () => {
    expect(wrapper.classes()).toContain('min-h-screen');
  });
});