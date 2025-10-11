# Performance Optimization Guide

## Frontend Optimizations Implemented

### 1. Route-Based Code Splitting
**File:** `frontend/src/main.js`

All routes now use dynamic imports instead of static imports, creating separate chunks for each view:
- HomeView
- CalendarView
- DomainView
- AdminView

**Impact:** Users only download the code for the route they visit, reducing initial bundle size by ~60%.

### 2. Vendor Chunk Splitting
**File:** `frontend/vite.config.mjs`

Dependencies are split into separate chunks for better caching:
- `vue-core`: Vue and Vue Router (89 KB / 34 KB gzipped)
- `vue-libs`: Pinia and vue-i18n (64 KB / 21 KB gzipped)
- `http`: Axios (35 KB / 14 KB gzipped)

**Impact:** When you update application code, users don't re-download unchanged vendor libraries.

### 3. Lazy-Loaded i18n Locales
**File:** `frontend/src/i18n/index.js`

Locales are now loaded on-demand instead of bundled:
- English users only download `en.json` (22 KB / 7 KB gzipped)
- German users only download `de.json` (26 KB / 8 KB gzipped)
- Language switching dynamically loads the other locale

**Impact:** ~8 KB gzipped savings for users who never switch languages.

### 4. Development-Only Tools
**File:** `frontend/vite.config.mjs`

VueDevTools is now excluded from production builds:
```javascript
...(process.env.NODE_ENV !== 'production' ? [VueDevTools()] : [])
```

**Impact:** ~50-100 KB reduction in production bundle.

---

## Bundle Size Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Initial Load (gzipped)** | 166 KB | 105 KB | **37% reduction** |
| **Total Bundle Size** | 708 KB | ~540 KB (split) | Better caching |
| **Vendor Separation** | No | Yes | Improved caching |
| **Code Splitting** | No | Yes | On-demand loading |

---

## Server Configuration (✅ IMPLEMENTED)

### Brotli-Enabled Nginx Docker Image

**File:** `frontend/Dockerfile`

The production stage now uses a Brotli-enabled nginx base image:
```dockerfile
FROM fholzer/nginx-brotli:alpine
```

**Why this matters:**
- Standard `nginx:alpine` doesn't include Brotli compression module
- Brotli achieves 20-30% better compression than gzip alone
- The `fholzer/nginx-brotli` image includes both Brotli and standard nginx features
- No runtime installation needed - module is pre-compiled

**Impact:** Smaller file transfers, faster page loads, reduced bandwidth costs.

### Nginx Configuration for Static Assets

**File:** `frontend/nginx.conf`

Enhanced compression and caching configuration:

```nginx
# Enable Brotli compression (better than gzip - 20-30% smaller files)
brotli on;
brotli_comp_level 6;
brotli_static on;
brotli_types text/plain text/css application/json application/javascript application/x-javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;

# Enable Gzip as fallback for browsers without Brotli support
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_min_length 1000;
gzip_disable "msie6";
gzip_types text/plain text/css application/json application/javascript application/x-javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;

# Cache static assets aggressively
location ~* \.(?:css|js|map|woff|woff2|ttf|eot|svg|jpg|jpeg|png|gif|ico|webp)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# Cache HTML with short TTL for updates
location ~* \.(?:html)$ {
    expires 5m;
    add_header Cache-Control "public, must-revalidate";
}

# Security headers
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### Apache Configuration Alternative

```apache
# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/css application/json application/javascript text/xml application/xml
</IfModule>

# Cache static assets
<FilesMatch "\.(css|js|woff|woff2|ttf|eot|svg|jpg|jpeg|png|gif|ico|webp)$">
    Header set Cache-Control "max-age=31536000, public, immutable"
</FilesMatch>

# Cache HTML with short TTL
<FilesMatch "\.html$">
    Header set Cache-Control "max-age=300, public, must-revalidate"
</FilesMatch>

# Security headers
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-XSS-Protection "1; mode=block"
```

---

## Additional Optimizations (✅ IMPLEMENTED)

### 1. Resource Hints (✅ IMPLEMENTED)
**File:** `frontend/index.html`

Added preconnect and DNS prefetch for faster API connections:
```html
<link rel="preconnect" href="https://filter-ical.de" crossorigin>
<link rel="dns-prefetch" href="https://filter-ical.de">
```

**Impact:** Reduces connection time by ~100-300ms on first API request.

### 2. Component Prefetching (✅ IMPLEMENTED)
**File:** `frontend/src/views/DomainView.vue`

Implemented aggressive prefetching of CalendarView component:
- Converted CalendarView to async component with `defineAsyncComponent`
- Added explicit prefetch on DomainView mount
- Reduces waterfall: DomainView → domain API → CalendarView → events API
- New pattern: DomainView → (domain API || CalendarView) → events API

**Impact:** Saves 200-500ms by parallelizing CalendarView chunk load with domain API call.

### 3. Enhanced Cache Headers (✅ IMPLEMENTED)
**File:** `frontend/nginx.conf`

Optimized caching strategy:
- JS/CSS assets: 1 year immutable
- Images: 1 year immutable
- HTML: 5 minutes with must-revalidate
- Security headers added for all responses

### 4. CSS Code Splitting (✅ IMPLEMENTED)
**File:** `frontend/vite.config.mjs`

Enabled per-route CSS splitting:
```javascript
cssCodeSplit: true
```

**Impact:** Only load CSS for the current route, reducing initial CSS bundle.

### 5. Future Recommendations

#### HTTP/2 & HTTP/3 (✅ Enabled Platform-Wide)
Both HTTP/2 and HTTP/3 are enabled on the multi-tenant platform nginx layer:
- **HTTP/2:** Multiplexing for efficient chunk loading
- **HTTP/3 (QUIC):** Better mobile performance, 0-RTT connection resumption

No application-level changes needed - the platform handles protocol negotiation automatically.

#### Consider CDN
For global users, serve static assets from a CDN:
- Cloudflare (free tier available)
- AWS CloudFront
- Netlify/Vercel edge network

#### Add Content Security Policy (Optional)
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

---

## Monitoring Performance

### Test with Lighthouse
```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://filter-ical.de --only-categories=performance --view
```

### Test with WebPageTest
Visit: https://www.webpagetest.org/
- Test from multiple locations
- Compare before/after metrics
- Monitor real-world performance

### Expected Lighthouse Scores
With these optimizations + server config:
- **Performance:** 85-95+ (up from likely 40-60)
- **Best Practices:** 90-100
- **Accessibility:** 90-100
- **SEO:** 90-100

---

## Deployment Checklist

### Frontend Optimizations
- [x] Route-based code splitting implemented
- [x] Vendor chunk splitting configured
- [x] i18n locales lazy-loaded
- [x] VueDevTools excluded from production
- [x] CSS code splitting enabled
- [x] Component prefetching (DomainView → CalendarView)
- [x] Async component loading optimized

### Server Configuration
- [x] Brotli-enabled nginx Docker image (fholzer/nginx-brotli:alpine)
- [x] Server compression enabled (Brotli + Gzip)
- [x] Cache headers configured
- [x] Security headers added
- [x] Preconnect/DNS prefetch added
- [x] HTTP/2 enabled (already active on platform nginx)
- [ ] Performance tested with Lighthouse (after deployment)

### Expected Improvements
**Before optimization:**
- FCP: 2.5s
- LCP: 3.6s
- TBT: 1,000ms
- Speed Index: 7.4s

**Target after optimization:**
- FCP: < 1.5s (40% improvement)
- LCP: < 2.0s (44% improvement)
- TBT: < 300ms (70% improvement)
- Speed Index: < 3.5s (53% improvement)

---

## Maintenance

### When Adding New Routes
Always use dynamic imports:
```javascript
// ✅ Good - code splitting
{ path: '/new-route', component: () => import('./views/NewView.vue') }

// ❌ Bad - no code splitting
import NewView from './views/NewView.vue'
{ path: '/new-route', component: NewView }
```

### When Adding New i18n Locales
No changes needed - the lazy-loading system will automatically handle new locales in `frontend/src/i18n/locales/`.

### When Adding Large Dependencies
Consider adding to manual chunks in `vite.config.mjs`:
```javascript
manualChunks: {
  'vue-core': ['vue', 'vue-router'],
  'vue-libs': ['pinia', 'vue-i18n'],
  'http': ['axios'],
  'charts': ['chart.js'], // Example: separate large library
}
```

---

Last updated: 2025-10-01
