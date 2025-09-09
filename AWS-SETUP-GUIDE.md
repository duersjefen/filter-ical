# Complete AWS Setup Guide for iCal Viewer

This guide walks you through setting up AWS infrastructure and GitHub secrets for automated deployment.

## Prerequisites

- AWS Account with appropriate permissions
- GitHub repository with your code
- Docker installed locally
- AWS CLI installed

## Step 1: Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1 (or your preferred region)
# Default output format: json
```

## Step 2: Set Up AWS Infrastructure

### Run the AWS Setup Script

```bash
# Make sure you're in the project root
cd /path/to/ical-viewer

# Run the setup script
./infrastructure/aws-setup.sh
```

This script will:
- Create ECR repositories for backend and frontend images
- Output the repository URIs you'll need later
- Configure ECR login

### Manual ECR Setup (Alternative)

If the script doesn't work, create repositories manually:

```bash
# Create backend repository
aws ecr create-repository --repository-name ical-viewer-backend --region us-east-1

# Create frontend repository  
aws ecr create-repository --repository-name ical-viewer-frontend --region us-east-1

# Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your Account ID: $ACCOUNT_ID"
```

## Step 3: Launch EC2 Instance

### 3.1 Launch Instance

1. Go to AWS EC2 Console
2. Click "Launch Instance"
3. Choose configuration:
   - **Name**: `ical-viewer-production`
   - **AMI**: Amazon Linux 2023 (free tier eligible)
   - **Instance Type**: t3.micro (for testing) or t3.medium (recommended)
   - **Key Pair**: Create new or use existing (you'll need this for deployment)
   - **Security Group**: Allow HTTP (80), HTTPS (443), and SSH (22)
   - **Storage**: 20 GB GP3 (default is fine)

### 3.2 Configure Security Group

Allow these inbound rules:
- **SSH (22)**: From your IP or 0.0.0.0/0
- **HTTP (80)**: From 0.0.0.0/0  
- **HTTPS (443)**: From 0.0.0.0/0
- **Custom TCP (8080)**: From 0.0.0.0/0 (for direct frontend access)
- **Custom TCP (8081)**: From 0.0.0.0/0 (for direct backend access)

### 3.3 Configure EC2 Instance

SSH into your instance and run:

```bash
# Download and run the EC2 setup script
curl -o ec2-setup.sh https://raw.githubusercontent.com/YOUR_USERNAME/ical-viewer/main/infrastructure/ec2-setup.sh
chmod +x ec2-setup.sh
./ec2-setup.sh

# Configure AWS CLI on EC2
aws configure
# Use the same credentials as your local setup
```

## Step 4: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets

Add these repository secrets:

1. **AWS_ACCESS_KEY_ID**
   - Your AWS access key ID
   - Same as used in `aws configure`

2. **AWS_SECRET_ACCESS_KEY**  
   - Your AWS secret access key
   - Same as used in `aws configure`

3. **EC2_HOST**
   - Your EC2 instance public IP address
   - Find this in EC2 console or run: `curl http://169.254.169.254/latest/meta-data/public-ipv4` on EC2

4. **EC2_SSH_KEY**
   - Your EC2 private key content
   - The .pem file content you downloaded when creating the key pair
   - Copy entire file content including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`

### How to Get EC2_SSH_KEY Content

```bash
# On your local machine, display the private key
cat path/to/your-key.pem

# Copy the entire output (including BEGIN/END lines) and paste into GitHub secret
```

## Step 5: Update Configuration Files

### 5.1 Update Production Docker Compose

Edit `infrastructure/docker-compose.prod.yml`:

```bash
# Replace YOUR_ACCOUNT_ID with your actual AWS account ID
sed -i 's/YOUR_ACCOUNT_ID/123456789012/g' infrastructure/docker-compose.prod.yml
```

Get your account ID with:
```bash
aws sts get-caller-identity --query Account --output text
```

### 5.2 Copy Production Config to EC2

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@YOUR_EC2_IP

# Copy the production docker-compose file
scp -i your-key.pem infrastructure/docker-compose.prod.yml ec2-user@YOUR_EC2_IP:/opt/ical-viewer/
```

## Step 6: Test Deployment

### 6.1 Manual Deployment Test

Before using GitHub Actions, test manually:

```bash
# On your local machine, build and push images
./infrastructure/aws-setup.sh  # This logs you into ECR

# Build and push backend
cd backend
docker build -t $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ical-viewer-backend:latest .
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ical-viewer-backend:latest

# Build and push frontend  
cd ../frontend
docker build -t $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ical-viewer-frontend:latest .
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ical-viewer-frontend:latest

# SSH to EC2 and deploy
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
cd /opt/ical-viewer
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker-compose -f docker-compose.prod.yml up -d
```

### 6.2 Automated Deployment

Once manual test works, try automated deployment:

```bash
# Commit and push to trigger GitHub Actions
git add .
git commit -m "Configure production deployment"
git push origin main
```

Watch the deployment in GitHub Actions tab.

## Step 7: Verify Deployment

After deployment completes, test your application:

```bash
# Test frontend
curl -I http://YOUR_EC2_IP

# Test backend API  
curl -I http://YOUR_EC2_IP/api/health

# Or visit in browser
# Frontend: http://YOUR_EC2_IP
# Backend API: http://YOUR_EC2_IP:8081 (if direct access enabled)
```

## Troubleshooting

### GitHub Actions Failing

1. **Check secrets**: Make sure all 4 secrets are correctly set
2. **Check EC2_SSH_KEY**: Must include BEGIN/END lines and correct formatting
3. **Check EC2_HOST**: Use public IP, not private IP
4. **Check Security Groups**: SSH (22) must be allowed from GitHub Actions IPs

### EC2 Connection Issues

```bash
# Test SSH connection
ssh -i your-key.pem ec2-user@YOUR_EC2_IP

# Check if Docker is running
sudo systemctl status docker

# Check if AWS CLI is configured
aws sts get-caller-identity
```

### Container Issues

```bash
# On EC2, check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Restart containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### ECR Access Issues

```bash
# Re-login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Check repositories exist
aws ecr describe-repositories
```

## Production Optimizations

### SSL/HTTPS Setup

1. Get a domain name and point it to your EC2 IP
2. Use Let's Encrypt for free SSL certificates:

```bash
# Install certbot on EC2
sudo yum install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Update nginx config to use SSL
```

### Auto-scaling Setup

1. Create Application Load Balancer
2. Set up Auto Scaling Group
3. Use ECS/Fargate for container orchestration

### Monitoring

1. Set up CloudWatch for logs and metrics
2. Configure health checks
3. Set up alerts for downtime

### Backup Strategy

1. Schedule EBS snapshots
2. Backup application data regularly
3. Test restore procedures

## Cost Management

- **Development**: Use t3.micro instances (free tier)
- **Production**: Start with t3.medium, scale as needed  
- **Storage**: Use GP3 volumes for better cost/performance
- **Monitoring**: Set up billing alerts
- **Cleanup**: Regularly remove old Docker images and unused resources

## Security Best Practices

1. **IAM Roles**: Use IAM roles instead of access keys when possible
2. **Security Groups**: Restrict access to necessary ports only
3. **Updates**: Keep EC2 instance and containers updated
4. **Secrets**: Never commit secrets to Git
5. **VPC**: Consider using private subnets for production

## Next Steps

1. Set up domain name and SSL certificates
2. Configure monitoring and alerting  
3. Set up automated backups
4. Plan for scaling and high availability
5. Implement logging and error tracking