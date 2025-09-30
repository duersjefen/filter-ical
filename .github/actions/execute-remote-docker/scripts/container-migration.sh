#!/bin/bash
# =============================================================================
# Container Migration Module - Handle Legacy Container Cleanup
# =============================================================================

migrate_legacy_containers() {
    echo "🔄 Checking for containers that need cleanup before deployment..."

    # LEGACY MIGRATION: Check for old ical-viewer containers
    legacy_containers=""
    if docker ps -a --filter "name=ical-viewer$" --format "{{.Names}}" | grep -q "ical-viewer"; then
        legacy_containers="$legacy_containers ical-viewer"
        echo "   📦 Found legacy container: ical-viewer"
    fi

    if docker ps -a --filter "name=ical-viewer-frontend$" --format "{{.Names}}" | grep -q "ical-viewer-frontend"; then
        legacy_containers="$legacy_containers ical-viewer-frontend"
        echo "   📦 Found legacy container: ical-viewer-frontend"
    fi

    # CONFLICT RESOLUTION: Check for containers that would conflict with deployment
    conflicting_containers=""
    for container in $containers; do
        if docker ps -a --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
            conflicting_containers="$conflicting_containers $container"
            echo "   ⚠️  Found conflicting container: $container"
        fi
    done

    # Clean up both legacy and conflicting containers
    all_cleanup_containers="$legacy_containers $conflicting_containers"
    all_cleanup_containers=$(echo $all_cleanup_containers | xargs)  # Remove extra spaces

    if [ -n "$all_cleanup_containers" ]; then
        echo "🔄 Cleaning up containers before deployment..."
        for container in $all_cleanup_containers; do
            echo "   🛑 Stopping container: $container"
            docker stop "$container" 2>/dev/null || echo "   ⚠️  Container $container was already stopped"
            echo "   🗑️  Removing container: $container"
            docker rm "$container" 2>/dev/null || echo "   ⚠️  Container $container was already removed"
        done
        echo "✅ Container cleanup completed - deployment can proceed"
    else
        echo "✅ No container conflicts found - deployment can proceed"
    fi
}

rollback_containers() {
    local containers="$1"
    local backup_tag="${BACKUP_TAG:-}"

    echo "🔄 Starting container rollback process..."
    echo "   Target containers: $containers"

    # Auto-detect backup tag if not provided
    if [ -z "$backup_tag" ]; then
        echo "🔍 No backup tag provided, searching for most recent backup..."

        # Get most recent backup tag
        backup_tag=$(docker images "$ECR_REGISTRY/filter-ical-*:backup-*" --format "{{.Tag}}" | sort -u | sort -t- -k2 -rn | head -1)

        if [ -z "$backup_tag" ]; then
            echo "❌ CRITICAL: No backups found and none provided!"
            echo "📋 Available images:"
            docker images "$ECR_REGISTRY/filter-ical-*" --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}"
            exit 1
        fi

        echo "   ✅ Found backup: $backup_tag"
    fi

    # Restore images from backup
    if ! restore_from_backup "$backup_tag" "$containers"; then
        echo "❌ CRITICAL: Failed to restore images from backup"
        exit 1
    fi

    # Stop and remove current containers
    echo "🛑 Stopping current containers..."
    for container in $containers; do
        if docker ps --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
            echo "   Stopping $container..."
            docker stop "$container" 2>/dev/null || echo "   ⚠️  Container already stopped"
        fi

        if docker ps -a --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
            echo "   Removing $container..."
            docker rm "$container" 2>/dev/null || echo "   ⚠️  Container already removed"
        fi
    done

    # Restart containers with backed-up images using docker-compose
    echo "🚀 Starting containers with backed-up images..."
    if ! docker-compose up -d $containers; then
        echo "❌ CRITICAL: Failed to start containers after rollback!"
        echo "🔍 Checking container status:"
        docker-compose ps $containers
        exit 1
    fi

    # Wait for containers to be healthy
    echo "⏳ Waiting for containers to be healthy..."
    local max_wait=60
    local waited=0
    local all_healthy=false

    while [ $waited -lt $max_wait ]; do
        all_healthy=true

        for container in $containers; do
            # Check if container is running
            if ! docker ps --filter "name=^${container}$" --filter "status=running" --format "{{.Names}}" | grep -q "^${container}$"; then
                all_healthy=false
                break
            fi

            # Check health status if healthcheck is defined
            local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
            if [ "$health_status" != "none" ] && [ "$health_status" != "healthy" ]; then
                all_healthy=false
                break
            fi
        done

        if [ "$all_healthy" = true ]; then
            echo "✅ All containers are healthy"
            break
        fi

        sleep 2
        waited=$((waited + 2))
        echo "   Waiting... ($waited/$max_wait seconds)"
    done

    if [ "$all_healthy" = false ]; then
        echo "⚠️  Warning: Some containers may not be fully healthy after rollback"
        echo "🔍 Container status:"
        docker-compose ps $containers
    fi

    echo "✅ Rollback completed successfully"
    echo "   Rolled back to: $backup_tag"

    # Display backup metadata if available
    if [ -f "/tmp/${backup_tag}.meta" ]; then
        echo "📋 Backup details:"
        cat "/tmp/${backup_tag}.meta" | sed 's/^/   /'
    fi

    return 0
}