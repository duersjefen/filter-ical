/**
 * Tests for main App component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import App from '../src/App.vue';

describe('App Component', () => {
  let wrapper;
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    wrapper = mount(App, {
      global: {
        plugins: [pinia]
      }
    });
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