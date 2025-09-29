#!/bin/bash
# =============================================================================
# Deployment Validation Module - Verify Deployment Success
# =============================================================================

validate_deployment() {
    local containers="$1"
    
    echo "🔍 Validating deployment success..."
    
    local validation_failed=0
    
    for container in $containers; do
        echo "   📦 Validating container: $container"
        
        # Check if container is running
        if ! docker ps --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
            echo "   ❌ Container $container is not running"
            validation_failed=1
            continue
        fi
        
        # Check container health
        container_status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null)
        if [[ "$container_status" != "running" ]]; then
            echo "   ❌ Container $container status: $container_status (expected: running)"
            validation_failed=1
            continue
        fi
        
        # Check container restart count (should be low)
        restart_count=$(docker inspect --format='{{.RestartCount}}' "$container" 2>/dev/null)
        if [[ $restart_count -gt 3 ]]; then
            echo "   ⚠️  Container $container has restarted $restart_count times"
        fi
        
        echo "   ✅ Container $container is healthy (status: $container_status)"
    done
    
    if [[ $validation_failed -eq 0 ]]; then
        echo "✅ All containers validated successfully"
    else
        echo "❌ Deployment validation failed"
        
        # Show container status for debugging
        echo "🔍 Current container status:"
        docker ps -a --filter "name=$(echo $containers | tr ' ' '|')" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" || true
    fi
    
    return $validation_failed
}

restart_nginx() {
    local nginx_container="$1"
    
    echo "🔄 Restarting nginx container: $nginx_container"
    
    if docker ps --filter "name=^${nginx_container}$" --format "{{.Names}}" | grep -q "^${nginx_container}$"; then
        if docker restart "$nginx_container"; then
            echo "✅ Nginx container restarted successfully"
            
            # Wait a moment for nginx to fully start
            sleep 5
            
            # Verify nginx is running
            if docker ps --filter "name=^${nginx_container}$" --format "{{.Names}}" | grep -q "^${nginx_container}$"; then
                echo "✅ Nginx is running after restart"
            else
                echo "❌ Nginx failed to start after restart"
                return 1
            fi
        else
            echo "❌ Failed to restart nginx container"
            return 1
        fi
    else
        echo "⚠️  Nginx container '$nginx_container' not found - skipping restart"
    fi
}

cleanup_deployment_artifacts() {
    echo "🧹 Cleaning up deployment artifacts..."
    
    # Remove any temporary files
    rm -f /tmp/result_* 2>/dev/null || true
    
    # Clean up unused Docker images (keep recent ones)
    echo "🗑️  Removing unused Docker images..."
    docker image prune -f >/dev/null 2>&1 || true
    
    # Clean up unused networks
    docker network prune -f >/dev/null 2>&1 || true
    
    echo "✅ Cleanup completed"
}

show_deployment_summary() {
    local containers="$1"
    
    echo ""
    echo "📋 DEPLOYMENT SUMMARY"
    echo "═══════════════════════════════════════════════════════════"
    
    # Show running containers
    echo "🐳 Running containers:"
    for container in $containers; do
        if docker ps --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
            image=$(docker inspect --format='{{.Config.Image}}' "$container" 2>/dev/null)
            uptime=$(docker inspect --format='{{.State.StartedAt}}' "$container" 2>/dev/null)
            echo "   ✅ $container ($image) - Started: $uptime"
        else
            echo "   ❌ $container - NOT RUNNING"
        fi
    done
    
    # Show resource usage
    echo ""
    echo "📊 Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(echo $containers | tr ' ' '\n' | xargs) 2>/dev/null || true
    
    echo "═══════════════════════════════════════════════════════════"
}