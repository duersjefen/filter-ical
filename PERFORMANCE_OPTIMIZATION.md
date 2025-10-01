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

## Server Configuration (To Be Implemented)

### Nginx Configuration for Static Assets

Add this to your Nginx configuration for optimal caching and compression:

```nginx
# Enable Brotli compression (better than gzip)
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

# Enable Gzip as fallback
gzip on;
gzip_vary on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

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

## Additional Recommendations

### 1. Preconnect to API Domain
Add to `frontend/index.html`:
```html
<link rel="preconnect" href="https://filter-ical.de" crossorigin>
<link rel="dns-prefetch" href="https://filter-ical.de">
```

### 2. Add Content Security Policy
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### 3. Enable HTTP/2 or HTTP/3
HTTP/2 multiplexing improves loading of multiple small chunks:
```nginx
listen 443 ssl http2;
```

### 4. Consider CDN
For global users, serve static assets from a CDN:
- Cloudflare (free tier available)
- AWS CloudFront
- Netlify/Vercel edge network

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

- [x] Route-based code splitting implemented
- [x] Vendor chunk splitting configured
- [x] i18n locales lazy-loaded
- [x] VueDevTools excluded from production
- [ ] Server compression enabled (Brotli + Gzip)
- [ ] Cache headers configured
- [ ] Security headers added
- [ ] Preconnect/DNS prefetch added
- [ ] HTTP/2 enabled
- [ ] Performance tested with Lighthouse

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
