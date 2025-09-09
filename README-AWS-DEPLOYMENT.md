# AWS Deployment Setup for iCal Viewer

This guide walks you through deploying the iCal Viewer with a modern ClojureScript frontend and Clojure backend using AWS infrastructure.

## Project Structure

```
ical-viewer/
├── backend/                    # Clojure API server
│   ├── deps.edn               # Backend dependencies
│   ├── Dockerfile             # Backend container
│   └── src/app/               # Backend source code
├── frontend/                   # ClojureScript SPA
│   ├── deps.edn               # Frontend dependencies
│   ├── shadow-cljs.edn        # ClojureScript build config
│   ├── package.json           # Node.js dependencies
│   ├── Dockerfile             # Frontend container
│   ├── nginx.conf             # Nginx configuration
│   └── src/ical_viewer/       # Frontend source code
├── infrastructure/             # AWS deployment scripts
│   ├── aws-setup.sh           # Sets up ECR repositories
│   ├── ec2-setup.sh           # Configures EC2 instance
│   └── docker-compose.prod.yml # Production Docker Compose
├── .github/workflows/          # CI/CD pipeline
│   └── deploy.yml             # Auto-deployment workflow
└── docker-compose.yml         # Development environment
```

## Quick Start (Development)

1. **Start development environment:**
   ```bash
   # Build and start both services
   docker-compose up -d
   
   # Or run individually for hot reload:
   # Terminal 1 - Backend
   cd backend && clojure -M:run
   
   # Terminal 2 - Frontend
   cd frontend && npm install && npm run dev
   ```

2. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:3000

## AWS Production Deployment

### Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed locally
- GitHub repository with this code

### Step 1: Set up AWS Infrastructure

```bash
# Run the AWS setup script
./infrastructure/aws-setup.sh
```

This creates:
- ECR repositories for your Docker images
- Outputs the repository URIs for configuration

### Step 2: Launch and Configure EC2 Instance

1. Launch an EC2 instance (t3.medium or larger recommended)
2. SSH into the instance and run:
   ```bash
   # Copy and run the EC2 setup script
   curl -o ec2-setup.sh https://raw.githubusercontent.com/YOUR_USERNAME/ical-viewer/main/infrastructure/ec2-setup.sh
   chmod +x ec2-setup.sh
   ./ec2-setup.sh
   ```

### Step 3: Configure GitHub Actions

Add these secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key  
- `EC2_HOST` - Your EC2 instance public IP
- `EC2_SSH_KEY` - Your EC2 private key (for SSH access)

### Step 4: Update Configuration Files

1. **Update docker-compose.prod.yml:**
   Replace `YOUR_ACCOUNT_ID` with your actual AWS account ID:
   ```bash
   # Get your AWS account ID
   aws sts get-caller-identity --query Account --output text
   ```

2. **Update the production compose file:**
   ```bash
   sed -i 's/YOUR_ACCOUNT_ID/123456789012/g' infrastructure/docker-compose.prod.yml
   ```

### Step 5: Deploy

```bash
# Push to main branch to trigger deployment
git add .
git commit -m "Set up AWS deployment"
git push origin main
```

The GitHub Actions workflow will:
1. Run tests
2. Build Docker images
3. Push to ECR
4. Deploy to EC2
5. Perform health checks

## Architecture Benefits

✅ **Separation of Concerns**: Frontend and backend are independent services
✅ **Scalable**: Can scale frontend and backend independently  
✅ **Cloud Native**: Uses AWS managed services (ECR)
✅ **CI/CD Ready**: Automated testing and deployment
✅ **Development Friendly**: Hot reload for both frontend and backend
✅ **Production Ready**: Health checks, graceful shutdowns, logging

## Development Workflow

1. **Make changes** to frontend (src/ical_viewer/) or backend (src/app/)
2. **Test locally** with `docker-compose up`
3. **Push to main branch** for automatic deployment
4. **Monitor deployment** in GitHub Actions

## Customization

### Environment Variables

Add to your EC2 `/opt/ical-viewer/.env`:
```bash
ENV=production
BASE_URL=https://your-domain.com
# Add any other environment variables your app needs
```

### SSL/HTTPS Setup

To add SSL certificates:
1. Update nginx.conf with SSL configuration
2. Mount certificates in docker-compose.prod.yml
3. Configure your domain to point to EC2 instance

### Scaling

To scale the application:
1. Add Application Load Balancer
2. Use multiple EC2 instances
3. Consider ECS/Fargate for container orchestration

## Troubleshooting

**Check deployment status:**
```bash
# On EC2 instance
cd /opt/ical-viewer
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

**Check application health:**
```bash
curl -f http://localhost/
curl -f http://localhost:3000/health
```

**View logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

## Cost Optimization

- Use t3.micro for development/testing
- Set up EC2 auto-stop during off hours
- Monitor ECR storage costs
- Use CloudWatch for monitoring

## Next Steps

1. Set up a custom domain
2. Add SSL certificates  
3. Set up CloudWatch monitoring
4. Configure automated backups
5. Add load balancing for high availability