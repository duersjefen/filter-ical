#!/bin/bash
# Domain Setup Script for filter-ical.de
# Run this after buying and configuring DNS for your domain

set -e

DOMAIN="filter-ical.de"
EC2_HOST="56.228.25.95"

echo "🌐 Setting up domain-based deployment for $DOMAIN"
echo "=================================================="

# Function to check if domain points to our server
check_dns() {
    echo "🔍 Checking DNS propagation..."
    RESOLVED_IP=$(dig +short $DOMAIN | tail -n1)
    if [ "$RESOLVED_IP" = "$EC2_HOST" ]; then
        echo "✅ DNS correctly points $DOMAIN → $EC2_HOST"
        return 0
    else
        echo "❌ DNS not ready. $DOMAIN points to: $RESOLVED_IP (expected: $EC2_HOST)"
        echo "   Please wait for DNS propagation or check your DNS settings."
        return 1
    fi
}

# Function to deploy domain-based configuration
deploy_domain_config() {
    echo "🚀 Deploying domain-based configuration..."
    
    # SSH into EC2 and deploy
    ssh -i ~/.ssh/wsl2.pem -o StrictHostKeyChecking=no ec2-user@$EC2_HOST << 'EOF'
        cd /opt/multi-apps
        
        # Stop current deployment
        docker-compose -f docker-compose.multi-app.yml down
        
        # Switch to domain-based config
        cp docker-compose.domains.yml docker-compose.yml
        cp nginx-domains.conf nginx.conf
        
        # Start with domain configuration
        docker-compose up -d
        
        echo "✅ Domain-based deployment started"
EOF
}

# Function to get SSL certificate
setup_ssl() {
    echo "🔐 Setting up SSL certificate..."
    
    ssh -i ~/.ssh/wsl2.pem -o StrictHostKeyChecking=no ec2-user@$EC2_HOST << EOF
        # Install certbot if not present
        sudo yum update -y
        sudo yum install -y certbot python3-certbot-nginx
        
        # Get certificate
        sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email your-email@example.com
        
        echo "✅ SSL certificate installed"
EOF
}

# Function to test the setup
test_deployment() {
    echo "🧪 Testing deployment..."
    
    # Test HTTP redirect
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN)
    if [ "$HTTP_CODE" = "301" ]; then
        echo "✅ HTTP redirect working (301)"
    else
        echo "⚠️ HTTP redirect not working (got $HTTP_CODE)"
    fi
    
    # Test HTTPS
    HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN)
    if [ "$HTTPS_CODE" = "200" ]; then
        echo "✅ HTTPS working (200)"
        echo "🎉 Your website is live at https://$DOMAIN"
    else
        echo "⚠️ HTTPS not working (got $HTTPS_CODE)"
    fi
}

# Main execution
main() {
    echo "Prerequisites checklist:"
    echo "□ Domain $DOMAIN purchased"
    echo "□ DNS A record: @ → $EC2_HOST"
    echo "□ DNS A record: www → $EC2_HOST"
    echo "□ DNS propagated (wait 5-30 minutes after DNS changes)"
    echo ""
    
    read -p "Have you completed all prerequisites? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "Please complete prerequisites first."
        echo "See DOMAIN-BUYING-GUIDE.md for detailed instructions."
        exit 1
    fi
    
    # Check DNS
    if ! check_dns; then
        exit 1
    fi
    
    # Deploy domain configuration
    deploy_domain_config
    
    # Wait for deployment
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    # Set up SSL
    setup_ssl
    
    # Test everything
    test_deployment
    
    echo ""
    echo "🎉 Domain setup complete!"
    echo "Your iCal Viewer is now live at:"
    echo "  🌐 https://$DOMAIN"
    echo "  🌐 https://www.$DOMAIN"
    echo ""
    echo "Next steps:"
    echo "1. Test your website in a browser"
    echo "2. Set up gabs-massage.de (when ready)"
    echo "3. Enjoy your professional domain! 🚀"
}

main "$@"