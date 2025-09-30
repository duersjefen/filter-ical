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

main() {
    local operation="${1}"
    local containers="${2}"
    local nginx_restart="${3:-false}"
    local nginx_container="${4:-nginx}"

    echo "🐳 Starting deployment operation: $operation"
    echo "🎯 Target containers: $containers"

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