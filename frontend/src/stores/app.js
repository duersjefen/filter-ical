/**
 * App Store - Temporary compatibility layer
 * Routes old store calls to new modular architecture
 * TODO: Gradually migrate components to use individual stores directly
 */
export { useCompatibilityStore as useAppStore } from './compatibility'