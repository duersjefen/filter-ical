# Production Architecture Overview

## 🏗️ Clean Multi-Domain Setup

### File Structure on EC2
```
/opt/websites/                 # Production root
├── docker-compose.yml         # Single orchestration file
├── nginx/nginx.conf          # Domain routing configuration
├── .env                      # Environment variables
├── apps/                     # App-specific configs
└── backups/                  # Backup storage
```

### Container Architecture
```
┌─────────────────────────────────────────┐
│                Internet                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│              Nginx Proxy                │
│         (Port 80/443)                   │
│    - SSL Termination                    │
│    - Domain Routing                     │
│    - HTTP/2 + Security Headers          │
└─────────────┬───────────┬───────────────┘
              │           │
    ┌─────────▼─────────┐ │
    │   iCal Viewer     │ │
    │  (Port 3000)      │ │
    │ filter-ical.de    │ │
    └───────────────────┘ │
                          │
              ┌───────────▼─────────┐
              │   Future Apps       │
              │  (Port 4000+)       │
              │ gabs-massage.de     │
              └─────────────────────┘
```

### Security & SSL
- **Let's Encrypt SSL**: Free, auto-renewal
- **HTTP → HTTPS**: Automatic redirect
- **Security Headers**: CSP, XSS protection, etc.
- **Rate Limiting**: API protection

### Benefits
- ✅ **Single Entry Point**: One nginx handles everything
- ✅ **Easy Scaling**: Add new domains by config
- ✅ **Zero Downtime**: Rolling deployments
- ✅ **Professional**: Industry-standard setup
- ✅ **Cost Effective**: Free SSL, single EC2 instance