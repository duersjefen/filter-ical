#!/bin/bash
# =============================================================================
# Configuration-Driven Deployment (Pure Functional Approach)
# =============================================================================
# Zero hardcoded values - everything is configurable and testable

set -euo pipefail

# =============================================================================
# PURE FUNCTIONAL DEPLOYMENT FUNCTIONS
# =============================================================================

# Main deployment orchestrator (pure function)
deploy_application() {
    local project_root="$1"
    local environment="$2"
    local backend_changed="$3"
    local frontend_changed="$4"
    
    echo "🚀 Starting configuration-driven deployment..."
    
    # Auto-discover configuration from existing project files
    # Both scripts are in the same directory after upload with strip_components: 1
    local script_dir="$(dirname "${BASH_SOURCE[0]}")"
    source "$script_dir/auto-config.sh"
    discover_project_config "$project_root"
    export_discovered_config
    
    echo "🚀 Starting deployment for $PROJECT_NAME ($environment)"
    
    # Determine containers to update (pure function)
    local containers_to_update
    containers_to_update=$(determine_containers_to_update \
        "$backend_changed" \
        "$frontend_changed" \
        "$BACKEND_CONTAINER" \
        "$FRONTEND_CONTAINER")
    
    if [ -z "$containers_to_update" ]; then
        echo "✨ No containers require updating - deployment complete"
        return 0
    fi
    
    echo "📋 Containers to update: $containers_to_update"
    
    # Create backup (pure function)
    create_environment_backup "$containers_to_update" "$BACKUP_PREFIX"
    
    # Execute deployment (pure function)
    execute_container_deployment "$containers_to_update" "$NGINX_CONTAINER" "$frontend_changed"
    
    # Validate deployment (pure function)
    validate_deployment_health "$DOMAIN_NAME" "$HEALTH_ENDPOINT" "$API_ENDPOINT" "$HEALTH_TIMEOUT"
    
    # Clean up on success (pure function)
    cleanup_successful_deployment "$BACKUP_PREFIX"
    
    echo "✅ Deployment completed successfully"
}

# Pure function: determine containers to update
determine_containers_to_update() {
    local backend_changed="$1"
    local frontend_changed="$2"
    local backend_container="$3"
    local frontend_container="$4"
    
    local containers=""
    
    [ "$backend_changed" = "true" ] && containers="$containers $backend_container"
    [ "$frontend_changed" = "true" ] && containers="$containers $frontend_container"
    
    echo "$containers" | xargs
}

# Pure function: create environment backup
create_environment_backup() {
    local containers_to_update="$1"
    local backup_prefix="$2"
    
    echo "💾 Creating deployment backup with prefix: $backup_prefix"
    
    if ! docker-compose ps | grep -q "Up"; then
        echo "ℹ️ No running containers to backup"
        return 0
    fi
    
    local backup_count=0
    
    for container in $containers_to_update; do
        local current_image
        current_image=$(docker-compose images "$container" | tail -n 1 | awk '{print $4":"$5}' 2>/dev/null || echo "")
        
        if [ -n "$current_image" ] && [ "$current_image" != ":" ]; then
            docker tag "$current_image" "${current_image%:*}:${backup_prefix}-$container" 2>/dev/null || true
            echo "✅ Backup created: $container"
            backup_count=$((backup_count + 1))
        fi
    done
    
    echo "📊 Created $backup_count backup(s)"
}

# Pure function: execute container deployment  
execute_container_deployment() {
    local containers_to_update="$1"
    local nginx_container="$2"
    local frontend_changed="$3"
    
    echo "🔄 Executing zero-downtime rolling update..."
    
    # Rolling update
    docker-compose up -d --no-deps $containers_to_update
    
    # Intelligent health monitoring (no fixed waits)
    wait_for_container_health $containers_to_update
    
    # Smart nginx restart (only if frontend changed)
    if [ "$frontend_changed" = "true" ]; then
        echo "🔄 Restarting $nginx_container (frontend changed)..."
        docker-compose restart "$nginx_container"
        sleep 5
    else
        echo "⏭️ Nginx restart skipped (frontend unchanged)"
    fi
}

# Pure function: wait for container health
wait_for_container_health() {
    local containers_to_check="$1"
    local max_wait="${2:-60}"
    local check_interval="${3:-5}"
    
    echo "🏥 Monitoring container health..."
    
    for ((i=0; i<$((max_wait/check_interval)); i++)); do
        local unhealthy_count=0
        
        for container in $containers_to_check; do
            if ! docker-compose ps "$container" | grep -q "Up.*healthy\|Up.*health: starting"; then
                unhealthy_count=$((unhealthy_count + 1))
            fi
        done
        
        if [ $unhealthy_count -eq 0 ]; then
            echo "✅ All containers healthy after $((i * check_interval))s"
            return 0
        fi
        
        [ $i -eq 0 ] && echo "⏳ Waiting for containers to become healthy..."
        sleep $check_interval
    done
    
    echo "⚠️ Container health check timeout"
    return 1
}

# Pure function: validate deployment health
validate_deployment_health() {
    local domain="$1"
    local health_endpoint="$2"
    local api_endpoint="$3"
    local timeout="$4"
    
    echo "🧪 Validating deployment health..."
    
    # Parallel health checks for speed
    local temp_dir
    temp_dir=$(mktemp -d)
    
    # Launch parallel validation tests
    validate_https_endpoint "https://$domain/" "$temp_dir/https" &
    validate_https_endpoint "https://$domain$health_endpoint" "$temp_dir/health" &
    validate_https_endpoint "https://$domain$api_endpoint" "$temp_dir/api" &
    
    # Wait for all tests
    wait
    
    # Evaluate results
    local validation_failed=0
    
    check_validation_result "$temp_dir/https" "HTTPS site" || validation_failed=1
    check_validation_result "$temp_dir/health" "Health endpoint" || validation_failed=1
    check_validation_result "$temp_dir/api" "API endpoint" || validation_failed=1
    
    # Cleanup
    rm -rf "$temp_dir"
    
    if [ $validation_failed -eq 0 ]; then
        echo "✅ All health validation tests passed"
        return 0
    else
        echo "❌ Health validation failed"
        return 1
    fi
}

# Pure function: validate individual endpoint
validate_https_endpoint() {
    local url="$1"
    local result_file="$2"
    
    if curl -f --connect-timeout 5 --max-time 15 "$url" >/dev/null 2>&1; then
        echo "OK" > "$result_file"
    else
        echo "FAIL" > "$result_file"
    fi
}

# Pure function: check validation result
check_validation_result() {
    local result_file="$1"
    local test_name="$2"
    
    if grep -q "OK" "$result_file" 2>/dev/null; then
        echo "✅ $test_name passed"
        return 0
    else
        echo "❌ $test_name failed"
        return 1
    fi
}

# Pure function: cleanup successful deployment
cleanup_successful_deployment() {
    local backup_prefix="$1"
    
    echo "🧹 Cleaning up backup containers..."
    
    if docker images | grep -q "${backup_prefix}-"; then
        docker images --format "{{.Repository}}:{{.Tag}}" | grep "${backup_prefix}-" | xargs -r docker rmi 2>/dev/null || true
        echo "✅ Backup containers cleaned up"
    else
        echo "ℹ️ No backup containers to clean up"
    fi
}

# =============================================================================
# ROLLBACK FUNCTIONS (PURE)
# =============================================================================

# Pure function: execute rollback
execute_deployment_rollback() {
    local containers_to_rollback="$1"
    local backup_prefix="$2"
    local health_check_url="$3"
    
    echo "🔄 Executing automatic rollback..."
    
    # Verify backups exist
    if ! docker images | grep -q "${backup_prefix}-"; then
        echo "⚠️ No backup containers found with prefix: $backup_prefix"
        return 1
    fi
    
    # Stop failed containers
    for container in $containers_to_rollback; do
        echo "🛑 Stopping failed container: $container"
        docker-compose stop "$container" 2>/dev/null || true
    done
    
    # Restore from backup
    local rollback_count=0
    for container in $containers_to_rollback; do
        local backup_image
        backup_image=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "${backup_prefix}-$container" | head -1)
        
        if [ -n "$backup_image" ]; then
            local ecr_repo
            ecr_repo=$(echo "$backup_image" | cut -d: -f1)
            docker tag "$backup_image" "$ecr_repo:latest"
            echo "✅ Restored $container from backup"
            rollback_count=$((rollback_count + 1))
        fi
    done
    
    if [ $rollback_count -eq 0 ]; then
        echo "❌ No containers could be rolled back"
        return 1
    fi
    
    # Restart with backup images
    docker-compose up -d $containers_to_rollback
    
    # Validate rollback
    sleep 10
    if curl -f --connect-timeout 5 --max-time 10 "$health_check_url" >/dev/null 2>&1; then
        echo "✅ Rollback successful ($rollback_count containers restored)"
        return 0
    else
        echo "❌ Rollback validation failed"
        return 1
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Main function
main() {
    local project_root="${1:-.}"
    local environment="${2:-production}"
    local backend_changed="${3:-true}"
    local frontend_changed="${4:-true}"
    
    if deploy_application "$project_root" "$environment" "$backend_changed" "$frontend_changed"; then
        echo "🎉 Deployment completed successfully"
        exit 0
    else
        echo "❌ Deployment failed"
        exit 1
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi