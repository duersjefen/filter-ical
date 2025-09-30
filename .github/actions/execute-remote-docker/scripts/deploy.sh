#!/bin/bash
set -euo pipefail

# =============================================================================
# Main Deployment Script - Modular, Maintainable, Industry Best Practice
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source all modules
source "$SCRIPT_DIR/container-migration.sh"
source "$SCRIPT_DIR/image-management.sh"
source "$SCRIPT_DIR/deployment-validation.sh"

check_disk_space() {
    echo "💾 Checking disk space..."

    local available_kb=$(df /opt/websites | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    local required_gb=2

    echo "   Available: ${available_gb}GB"
    echo "   Required: ${required_gb}GB"

    if [ "$available_gb" -lt "$required_gb" ]; then
        echo "❌ CRITICAL: Insufficient disk space!"
        echo "   Available: ${available_gb}GB"
        echo "   Required: ${required_gb}GB minimum"
        echo ""
        echo "🔍 Disk usage breakdown:"
        du -sh /opt/websites/* 2>/dev/null || true
        echo ""
        echo "💡 Suggestions:"
        echo "   1. Run backup cleanup: cleanup_old_backups 1"
        echo "   2. Remove unused Docker images: docker image prune -a"
        echo "   3. Check Docker volumes: docker system df"
        return 1
    fi

    echo "✅ Sufficient disk space available"
    return 0
}

main() {
    local operation="${1}"
    local containers="${2}"
    local nginx_restart="${3:-false}"
    local nginx_container="${4:-nginx}"

    echo "🐳 Starting deployment operation: $operation"
    echo "🎯 Target containers: $containers"

    # Check disk space before any operation (except list-backups)
    if [ "$operation" != "list-backups" ]; then
        if ! check_disk_space; then
            exit 1
        fi
    fi

    case "$operation" in
        "deploy")
            # Create backup before deployment
            create_deployment_backup "$containers"

            # Proceed with deployment
            migrate_legacy_containers
            deploy_containers "$containers"
            if [ "$nginx_restart" = "true" ]; then
                restart_nginx "$nginx_container"
            fi
            validate_deployment "$containers"

            # Cleanup old backups to free disk space
            cleanup_old_backups 3
            ;;
        "rollback")
            rollback_containers "$containers"
            ;;
        "clean")
            clean_deploy_containers "$containers"
            ;;
        "backup")
            # Standalone backup operation
            create_deployment_backup "$containers"
            ;;
        "list-backups")
            # List available backups
            list_backups
            ;;
        *)
            echo "❌ Unknown operation: $operation"
            exit 1
            ;;
    esac

    echo "✅ Operation '$operation' completed successfully"
}

main "$@"