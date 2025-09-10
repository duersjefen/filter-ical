# Architecture Documentation

## System Overview

Professional full-stack web application template with automated CI/CD pipeline, designed for zero-downtime deployment on AWS infrastructure.

## Technical Stack

### Backend
- **Runtime**: Clojure 1.11.1
- **Web Framework**: Ring + Jetty
- **API**: RESTful endpoints with JSON
- **Authentication**: Multiple strategies (magic-link, telegram)
- **Storage**: EDN files for persistence
- **Testing**: clojure.test with automated test runner

### Frontend  
- **Language**: ClojureScript
- **Build Tool**: shadow-cljs
- **UI Framework**: Reagent + Re-frame
- **Bundling**: Optimized production builds
- **Serving**: nginx container with gzip compression

### Infrastructure
- **Cloud Provider**: AWS (Account: 310829530903, Region: eu-north-1)
- **Compute**: EC2 instance (i-01647c3d9af4fe9fc)
- **Container Registry**: Amazon ECR
- **Reverse Proxy**: nginx with Let's Encrypt SSL
- **Container Orchestration**: Docker Compose

## Architecture Diagrams

### Request Flow
```
Internet → Route53/DNS → EC2 Instance
                         ├── nginx (80/443) → SSL termination
                         ├── ical-viewer-frontend (80) → Static files
                         └── ical-viewer (3000) → API endpoints
```

### CI/CD Pipeline
```
GitHub Push → Actions Runner → Build & Test → ECR Push → EC2 Deploy → Health Check
```

### Multi-Project Support
```
EC2 Instance (56.228.25.95)
├── nginx (reverse proxy)
│   ├── filter-ical.de → ical-viewer containers
│   ├── example.com → project2 containers  
│   └── [future domains] → [future projects]
└── /opt/websites/ (shared deployment directory)
```

## Security Architecture

### Network Security
- Only ports 80/443 exposed to internet
- Internal container communication on private network
- Unknown domains rejected with 444 response

### SSL/TLS
- Automatic certificate generation via Let's Encrypt
- TLS 1.2+ with strong cipher suites
- HSTS headers for browser security
- Auto-renewal every 6 hours via certbot

### Application Security
- CSP headers preventing XSS attacks
- No secrets in source code or containers
- Environment-based configuration
- Rate limiting on API endpoints

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Load balancer-ready architecture
- Container-based deployment for easy replication

### Performance Optimizations
- ClojureScript compilation for minimal bundle size
- nginx gzip compression and caching
- Docker multi-stage builds
- GitHub Actions cache optimization

## Data Flow

### Development
1. Developer commits → Pre-commit hooks run tests
2. Push to main → GitHub Actions triggered
3. Tests pass → Containers built and pushed to ECR
4. Deployment to production with health validation

### Production
1. User request → nginx reverse proxy
2. Static files → Frontend container
3. API calls → Backend container  
4. Response with security headers and compression

## Monitoring & Observability

### Health Endpoints
- `https://domain/health` → Backend health
- `http://localhost:8080/nginx-health` → nginx status

### Logging
- Container logs via docker-compose logs
- nginx access/error logs
- GitHub Actions deployment logs
- Pre-commit hook execution logs

## Disaster Recovery

### Backup Strategy
- Infrastructure as Code (all configs in git)
- Container images in ECR with multiple tags
- Easy recreation from template

### Rollback Procedures
- Git revert for quick rollbacks
- Previous container images remain available
- Zero-downtime deployment with health checks

## Template Replication

This architecture serves as a template for new projects:
1. Copy essential files (automated via Claude Code)
2. Update project-specific configuration
3. Deploy with same proven infrastructure
4. Benefit from all architectural decisions and optimizations