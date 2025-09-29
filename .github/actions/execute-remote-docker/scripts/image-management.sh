#!/bin/bash
# =============================================================================
# Image Management Module - Handle Docker Image Operations
# =============================================================================

# Service to ECR repository mapping
declare -A service_to_repo_map
service_to_repo_map["filter-ical"]="filter-ical-backend"
service_to_repo_map["filter-ical-frontend"]="filter-ical-frontend"
service_to_repo_map["filter-ical-backend-staging"]="filter-ical-backend"
service_to_repo_map["filter-ical-frontend-staging"]="filter-ical-frontend"
service_to_repo_map["filter-ical-backend-dev"]="filter-ical-backend"
service_to_repo_map["filter-ical-frontend-dev"]="filter-ical-frontend"

pull_and_tag_images() {
    local containers="$1"
    
    echo "📥 Pulling and tagging images for deployment..."
    
    if [ -n "$IMAGE_TAG" ]; then
        echo "🏷️  Using specific image tag: $IMAGE_TAG"
        
        # Verify all images exist in ECR
        echo "🔍 Verifying images exist in ECR before pulling..."
        for container in $containers; do
            repo_name="${service_to_repo_map[$container]:-$container}"
            image_uri="$ECR_REGISTRY/$repo_name:$IMAGE_TAG"
            echo "   Checking: $image_uri (service: $container)"
            
            if ! aws ecr describe-images --region "$AWS_REGION" --repository-name "$repo_name" --image-ids imageTag="$IMAGE_TAG" >/dev/null 2>&1; then
                echo "❌ CRITICAL: Image does not exist in ECR: $image_uri"
                echo "🔍 Available tags for repository $repo_name:"
                aws ecr describe-images --region "$AWS_REGION" --repository-name "$repo_name" --query 'imageDetails[*].imageTags[0]' --output text 2>/dev/null | head -10 || echo "   Could not list tags"
                exit 1
            fi
            echo "   ✅ $image_uri exists in ECR"
        done
        
        # Pull and tag images with environment-specific tags
        echo "📥 Pulling verified images..."
        for container in $containers; do
            repo_name="${service_to_repo_map[$container]:-$container}"
            image_uri="$ECR_REGISTRY/$repo_name:$IMAGE_TAG"
            echo "   Pulling: $image_uri (for service: $container)"
            
            if ! docker pull "$image_uri"; then
                echo "❌ CRITICAL: Failed to pull $image_uri"
                exit 1
            fi
            
            # Determine correct tag based on IMAGE_TAG prefix
            local_tag="latest"  # Default for production
            if [[ "$IMAGE_TAG" == staging-* ]]; then
                local_tag="staging-latest"
            elif [[ "$IMAGE_TAG" == dev-* ]]; then
                local_tag="dev-latest"
            fi
            
            docker tag "$image_uri" "$ECR_REGISTRY/$repo_name:$local_tag"
            echo "   ✅ $container: pulled $IMAGE_TAG and tagged as $local_tag"
        done
    else
        echo "📥 Pulling images using docker-compose (latest tags)..."
        if ! docker-compose pull $containers; then
            echo "❌ CRITICAL: Docker pull failed! ECR authentication or network issue"
            echo "🔍 Current images before failed pull:"
            docker-compose images $containers || true
            exit 1
        fi
    fi
}

authenticate_ecr() {
    echo "🔑 Refreshing ECR authentication..."
    echo "   ECR Registry: $ECR_REGISTRY"
    echo "   AWS Region: $AWS_REGION"
    
    # Test AWS credentials first
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo "❌ CRITICAL: AWS credentials not available or invalid"
        echo "🔍 AWS CLI version: $(aws --version 2>&1 || echo 'AWS CLI not found')"
        exit 1
    fi
    
    # Get ECR login with proper error handling
    echo "🔐 Getting ECR login token..."
    if ! aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"; then
        echo "❌ CRITICAL: ECR authentication failed"
        echo "🔍 Testing basic AWS access..."
        aws sts get-caller-identity || true
        echo "🔍 Testing ECR access..."
        aws ecr describe-repositories --region "$AWS_REGION" --max-items 1 || true
        exit 1
    fi
    
    echo "✅ ECR authentication successful"
}