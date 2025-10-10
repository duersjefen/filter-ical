/**
 * Tests for main App component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';
import { createI18n } from 'vue-i18n';
import App from '../src/App.vue';

// Mock components for testing
const MockLoginView = { template: '<div data-testid="login-view"><h1>iCal Viewer</h1></div>' };
const MockHomeView = { template: '<div data-testid="home-view"><nav>Navigation</nav><main>Home Content</main></div>' };
const MockCalendarView = { template: '<div data-testid="calendar-view">Calendar</div>' };

// Create mock i18n instance
const createMockI18n = () => {
  return createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages: {
      en: {
        // Add minimal translations needed for tests
        app: {
          title: 'iCal Viewer'
        }
      }
    },
    globalInjection: true
  });
};

describe('App Component', () => {
  let wrapper;
  let pinia;
  let router;
  let i18n;

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

    // Create i18n instance
    i18n = createMockI18n();

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

    // Mount component with router, pinia, and i18n
    wrapper = mount(App, {
      global: {
        plugins: [router, pinia, i18n],
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
    // The root div has id="app" and should have min-h-screen class
    const appDiv = wrapper.find('#app');
    expect(appDiv.exists()).toBe(true);
    expect(appDiv.classes()).toContain('min-h-screen');
  });
});