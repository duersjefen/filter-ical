#!/bin/bash
# Deployment Health Check Script
# Run this when deployments appear broken

echo "🔍 DEPLOYMENT HEALTH CHECK"
echo "========================="

echo "1. Site Response:"
curl -I https://filter-ical.de/ 2>/dev/null | head -1

echo -e "\n2. Container Status:"
ssh -i ~/.ssh/wsl2.pem ec2-user@56.228.25.95 "cd /opt/websites && docker-compose ps"

echo -e "\n3. JavaScript Loading:"
curl -I https://filter-ical.de/js/main.js 2>/dev/null | head -1

echo -e "\n4. Backend Health:"
curl -f https://filter-ical.de/health 2>/dev/null && echo "✅ Backend OK" || echo "❌ Backend failed"

echo -e "\n5. Container Logs (last 3 lines each):"
echo "Backend:"
ssh -i ~/.ssh/wsl2.pem ec2-user@56.228.25.95 "cd /opt/websites && docker logs ical-viewer --tail 3"
echo "Frontend:" 
ssh -i ~/.ssh/wsl2.pem ec2-user@56.228.25.95 "cd /opt/websites && docker logs ical-viewer-frontend --tail 3"

echo -e "\n🎯 Run './scripts/debug-deployment.sh' anytime deployment seems broken"