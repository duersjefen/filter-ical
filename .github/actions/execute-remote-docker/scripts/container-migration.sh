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