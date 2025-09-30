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

create_deployment_backup() {
    local containers="$1"
    local backup_tag="backup-$(date +%s)"

    echo "💾 Creating deployment backup: $backup_tag"

    # Ensure GITHUB_OUTPUT is set (fallback to file)
    if [ -z "$GITHUB_OUTPUT" ]; then
        export GITHUB_OUTPUT="/tmp/github-actions-outputs/deployment-outputs.txt"
        mkdir -p "$(dirname "$GITHUB_OUTPUT")"
        touch "$GITHUB_OUTPUT"
    fi

    local backed_up_containers=""
    for container in $containers; do
        # Check if container is running
        if ! docker ps --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
            echo "   ⚠️  Container $container not running - skipping backup"
            continue
        fi

        # Get current image of running container
        local current_image=$(docker inspect --format='{{.Image}}' "$container" 2>/dev/null)
        if [ -z "$current_image" ]; then
            echo "   ⚠️  Could not get image for $container - skipping"
            continue
        fi

        # Get repository name
        local repo_name="${service_to_repo_map[$container]:-$container}"

        # Tag current image as backup
        local backup_image="$ECR_REGISTRY/$repo_name:$backup_tag"
        if docker tag "$current_image" "$backup_image"; then
            echo "   ✅ Backed up $container: $backup_image"
            backed_up_containers="$backed_up_containers $container"
        else
            echo "   ❌ Failed to backup $container"
        fi
    done

    if [ -z "$backed_up_containers" ]; then
        echo "⚠️  No containers backed up - deployment will proceed without rollback capability"
        echo "BACKUP_TAG=" >> "$GITHUB_OUTPUT"
        return 0
    fi

    # Store backup metadata
    local backup_metadata="/tmp/backup-${backup_tag}.meta"
    cat > "$backup_metadata" << EOF
BACKUP_TAG=$backup_tag
BACKUP_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
BACKED_UP_CONTAINERS=$backed_up_containers
COMMIT_SHA=${GITHUB_SHA:-unknown}
IMAGE_TAG=${IMAGE_TAG:-latest}
EOF

    echo "✅ Backup created successfully: $backup_tag"
    echo "   Containers backed up:$backed_up_containers"
    echo "BACKUP_TAG=$backup_tag" >> "$GITHUB_OUTPUT"
    return 0
}

list_backups() {
    echo "📋 Available backups:"

    # List all backup tags from local images
    local backup_images=$(docker images "$ECR_REGISTRY/filter-ical-*:backup-*" --format "{{.Repository}}:{{.Tag}}" | sort -r)

    if [ -z "$backup_images" ]; then
        echo "   No backups found"
        return 0
    fi

    echo "$backup_images" | while read -r image; do
        local tag=$(echo "$image" | cut -d: -f2)
        local timestamp=$(echo "$tag" | sed 's/backup-//')
        local date_str=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "unknown")

        if [ -f "/tmp/${tag}.meta" ]; then
            echo "   🔖 $tag (created: $date_str)"
            cat "/tmp/${tag}.meta" | grep -E "BACKED_UP_CONTAINERS|COMMIT_SHA" | sed 's/^/      /'
        else
            echo "   🔖 $tag (created: $date_str)"
        fi
    done
}

cleanup_old_backups() {
    local keep_count="${1:-3}"

    echo "🧹 Cleaning up old backups (keeping last $keep_count)..."

    # Get all backup tags sorted by timestamp (newest first)
    local all_backups=$(docker images "$ECR_REGISTRY/filter-ical-*:backup-*" --format "{{.Tag}}" | sort -u | sort -t- -k2 -rn)

    if [ -z "$all_backups" ]; then
        echo "   No backups to clean"
        return 0
    fi

    local backup_count=$(echo "$all_backups" | wc -l)
    if [ "$backup_count" -le "$keep_count" ]; then
        echo "   Current backup count ($backup_count) within limit ($keep_count)"
        return 0
    fi

    # Delete old backups
    local deleted=0
    echo "$all_backups" | tail -n +$((keep_count + 1)) | while read -r backup_tag; do
        echo "   🗑️  Removing old backup: $backup_tag"

        # Remove all images with this backup tag
        docker images "$ECR_REGISTRY/*:$backup_tag" --format "{{.Repository}}:{{.Tag}}" | while read -r image; do
            docker rmi "$image" 2>/dev/null || echo "      ⚠️  Could not remove $image"
        done

        # Remove metadata file
        rm -f "/tmp/${backup_tag}.meta" 2>/dev/null

        deleted=$((deleted + 1))
    done

    echo "✅ Cleaned up old backups"
}

restore_from_backup() {
    local backup_tag="$1"
    local containers="$2"

    echo "🔄 Restoring from backup: $backup_tag"

    # Validate backup tag format
    if [[ ! "$backup_tag" =~ ^backup-[0-9]+$ ]]; then
        echo "❌ Invalid backup tag format: $backup_tag"
        echo "   Expected format: backup-<timestamp> (e.g., backup-1234567890)"
        list_backups
        return 1
    fi

    # Verify backup exists
    local backup_exists=false
    for container in $containers; do
        local repo_name="${service_to_repo_map[$container]:-$container}"
        local backup_image="$ECR_REGISTRY/$repo_name:$backup_tag"

        if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${backup_image}$"; then
            backup_exists=true
            break
        fi
    done

    if [ "$backup_exists" = false ]; then
        echo "❌ CRITICAL: Backup $backup_tag not found!"
        list_backups
        return 1
    fi

    # Restore each container
    local restored_containers=""
    for container in $containers; do
        local repo_name="${service_to_repo_map[$container]:-$container}"
        local backup_image="$ECR_REGISTRY/$repo_name:$backup_tag"

        # Check if backup exists for this container
        if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${backup_image}$"; then
            echo "   ⚠️  No backup found for $container - skipping"
            continue
        fi

        # Determine environment-specific tag
        local env_tag="latest"
        if [[ "$container" == *-staging ]]; then
            env_tag="staging-latest"
        elif [[ "$container" == *-dev ]]; then
            env_tag="dev-latest"
        fi

        # Re-tag backup as current
        local current_tag="$ECR_REGISTRY/$repo_name:$env_tag"
        if docker tag "$backup_image" "$current_tag"; then
            echo "   ✅ Restored $container from backup"
            restored_containers="$restored_containers $container"
        else
            echo "   ❌ Failed to restore $container"
        fi
    done

    if [ -z "$restored_containers" ]; then
        echo "❌ No containers were restored!"
        return 1
    fi

    echo "✅ Backup restoration complete"
    echo "   Restored containers:$restored_containers"
    return 0
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