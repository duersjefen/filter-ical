#!/bin/bash
# =============================================================================
# Automatic Configuration Discovery System (Simplified)
# =============================================================================
# Single source of truth - automatically discovers project configuration

set -euo pipefail

# Discover configuration from existing files
discover_project_config() {
    local project_root="${1:-.}"
    
    echo "🔍 Auto-discovering configuration from existing files..."
    
    # Initialize with generic defaults (no hardcoded project names)
    PROJECT_NAME="app"
    BACKEND_CONTAINER="app"
    FRONTEND_CONTAINER="app-frontend"
    NGINX_CONTAINER="nginx"
    BACKUP_PREFIX="backup"
    HEALTH_ENDPOINT="/health"
    API_ENDPOINT="/api/calendars"
    HEALTH_TIMEOUT="60"
    PORT_BACKEND="3000"
    PORT_FRONTEND="80"
    
    # Discover from Git
    if [ -d "$project_root/.git" ]; then
        echo "📁 Discovering from Git repository..."
        local remote_url
        remote_url=$(git -C "$project_root" remote get-url origin 2>/dev/null || echo "")
        if [ -n "$remote_url" ]; then
            PROJECT_NAME=$(echo "$remote_url" | sed 's/.*[\/:]//g' | sed 's/\.git$//')
            echo "   ✅ PROJECT_NAME: $PROJECT_NAME (from git remote)"
        fi
    fi
    
    # Discover from package.json
    if [ -f "$project_root/package.json" ]; then
        echo "📦 Found package.json"
        local npm_name
        npm_name=$(jq -r '.name // empty' "$project_root/package.json" 2>/dev/null || echo "")
        if [ -n "$npm_name" ] && [ "$PROJECT_NAME" = "app" ]; then
            PROJECT_NAME="$npm_name"
            echo "   ✅ PROJECT_NAME: $PROJECT_NAME (from package.json)"
        fi
    fi
    
    # Discover from .env files
    if [ -f "$project_root/.env" ]; then
        echo "🔧 Found .env file"
        while IFS='=' read -r key value; do
            [[ "$key" =~ ^[[:space:]]*# ]] && continue
            [[ -z "$key" ]] && continue
            
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | sed 's/^["'\'']\|["'\'']$//g' | xargs)
            
            case "$key" in
                "DOMAIN"|"APP_DOMAIN"|"DOMAIN_NAME")
                    DOMAIN_NAME="$value"
                    echo "   ✅ DOMAIN_NAME: $value"
                    ;;
                "PORT"|"BACKEND_PORT"|"SERVER_PORT")
                    PORT_BACKEND="$value"
                    echo "   ✅ BACKEND_PORT: $value"
                    ;;
            esac
        done < "$project_root/.env"
    fi
    
    # Apply deployment overrides
    local override_file="$project_root/.github/config/deployment-overrides.conf"
    if [ -f "$override_file" ]; then
        echo "🔧 Applying deployment overrides..."
        while IFS='=' read -r key value; do
            [[ "$key" =~ ^[[:space:]]*# ]] && continue
            [[ -z "$key" ]] && continue
            
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | sed 's/^["'\'']\|["'\'']$//g' | xargs)
            
            case "$key" in
                "DOMAIN_NAME") DOMAIN_NAME="$value" ;;
                "ECR_REGISTRY") ECR_REGISTRY="$value" ;;
                "AWS_REGION") AWS_REGION="$value" ;;
                "PROJECT_NAME") PROJECT_NAME="$value" ;;
                "BACKEND_CONTAINER") BACKEND_CONTAINER="$value" ;;
                "FRONTEND_CONTAINER") FRONTEND_CONTAINER="$value" ;;
            esac
            echo "   🔧 Override: $key=$value"
        done < "$override_file"
    fi
    
    # Generate smart defaults based on project name
    if [ "$BACKEND_CONTAINER" = "app" ] && [ "$PROJECT_NAME" != "app" ]; then
        BACKEND_CONTAINER="$PROJECT_NAME"
    fi
    
    if [ "$FRONTEND_CONTAINER" = "app-frontend" ] && [ "$PROJECT_NAME" != "app" ]; then
        FRONTEND_CONTAINER="$PROJECT_NAME-frontend"
    fi
    
    echo ""
    echo "✅ Configuration auto-discovered!"
    echo "📊 PROJECT_NAME: $PROJECT_NAME"
    echo "📊 BACKEND_CONTAINER: $BACKEND_CONTAINER"
    echo "📊 FRONTEND_CONTAINER: $FRONTEND_CONTAINER"
    echo "📊 DOMAIN_NAME: ${DOMAIN_NAME:-<needs-configuration>}"
    echo ""
}

# Export discovered values for other scripts
export_discovered_config() {
    export PROJECT_NAME BACKEND_CONTAINER FRONTEND_CONTAINER NGINX_CONTAINER
    export BACKUP_PREFIX HEALTH_ENDPOINT API_ENDPOINT HEALTH_TIMEOUT
    export PORT_BACKEND PORT_FRONTEND DOMAIN_NAME ECR_REGISTRY AWS_REGION
}

# Main function
main() {
    local project_root="${1:-.}"
    discover_project_config "$project_root"
    export_discovered_config
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi