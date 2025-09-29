#!/bin/bash
# =============================================================================
# INPUT AND ENVIRONMENT VALIDATION FRAMEWORK
# =============================================================================
# Provides comprehensive validation for inputs, environment, and prerequisites
# Author: Claude Code
# =============================================================================

set -euo pipefail

# Source logging framework
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/logging.sh"

# =============================================================================
# Environment Variable Validation
# =============================================================================

# Validate required environment variables
validate_required_env() {
    local var_name="$1"
    local var_description="${2:-environment variable}"
    
    if [[ -z "${!var_name:-}" ]]; then
        log_critical "Missing required $var_description: $var_name"
        return 1
    fi
    
    log_debug "Validated $var_name: ${!var_name}"
    return 0
}

# Validate environment variables with defaults
validate_env_with_default() {
    local var_name="$1"
    local default_value="$2"
    local var_description="${3:-environment variable}"
    
    if [[ -z "${!var_name:-}" ]]; then
        log_info "Using default value for $var_name: $default_value"
        export "$var_name=$default_value"
    fi
    
    log_debug "Environment variable $var_name: ${!var_name}"
    return 0
}

# Batch validate multiple required variables
validate_required_envs() {
    local validation_failed=0
    
    for var_spec in "$@"; do
        # Support format: VAR_NAME or VAR_NAME:description
        local var_name="${var_spec%%:*}"
        local var_desc="${var_spec#*:}"
        
        if [[ "$var_desc" == "$var_spec" ]]; then
            var_desc="environment variable"
        fi
        
        if ! validate_required_env "$var_name" "$var_desc"; then
            validation_failed=1
        fi
    done
    
    return $validation_failed
}

# =============================================================================
# Input Parameter Validation
# =============================================================================

# Validate that input matches expected values
validate_input_enum() {
    local input_value="$1"
    local input_name="$2"
    shift 2
    local valid_values=("$@")
    
    for valid in "${valid_values[@]}"; do
        if [[ "$input_value" == "$valid" ]]; then
            log_debug "Input $input_name validated: $input_value"
            return 0
        fi
    done
    
    log_error "Invalid value for $input_name: '$input_value'"
    log_error "Valid values are: ${valid_values[*]}"
    return 1
}

# Validate container names against docker-compose services
validate_container_names() {
    local requested_containers="$1"
    local compose_file="${2:-docker-compose.yml}"
    
    log_subsection "Validating Container Names"
    
    # Get available services from docker-compose
    local available_services
    if ! available_services=$(docker-compose -f "$compose_file" config --services 2>/dev/null); then
        log_error "Failed to read services from $compose_file"
        return 1
    fi
    
    local valid_containers=""
    local invalid_containers=""
    
    for container in $requested_containers; do
        if echo "$available_services" | grep -q "^${container}$"; then
            valid_containers="$valid_containers $container"
            log_success "$container (valid service)"
        else
            invalid_containers="$invalid_containers $container"
            log_error "$container (invalid service)"
        fi
    done
    
    if [[ -n "$invalid_containers" ]]; then
        log_error "Invalid container names detected:$invalid_containers"
        log_info "Available services:"
        echo "$available_services" | while read -r service; do
            log_info "  - $service"
        done
        return 1
    fi
    
    # Return validated containers (trimmed)
    echo "${valid_containers# }"
    return 0
}

# =============================================================================
# AWS Configuration Validation
# =============================================================================

# Validate AWS credentials and permissions
validate_aws_credentials() {
    log_subsection "Validating AWS Credentials"
    
    # Test basic AWS access
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_critical "AWS credentials not available or invalid"
        log_info "AWS CLI version: $(aws --version 2>&1 || echo 'AWS CLI not found')"
        return 1
    fi
    
    # Get and display identity
    local identity
    identity=$(aws sts get-caller-identity --output json)
    local account=$(echo "$identity" | jq -r .Account)
    local arn=$(echo "$identity" | jq -r .Arn)
    
    log_success "AWS credentials validated"
    log_info "  Account: $account"
    log_info "  Identity: $arn"
    
    # Validate expected account if specified
    if [[ -n "${EXPECTED_AWS_ACCOUNT:-}" ]]; then
        if [[ "$account" != "$EXPECTED_AWS_ACCOUNT" ]]; then
            log_critical "AWS account mismatch!"
            log_error "  Expected: $EXPECTED_AWS_ACCOUNT"
            log_error "  Actual: $account"
            return 1
        fi
    fi
    
    return 0
}

# Validate ECR access
validate_ecr_access() {
    local region="${1:-$AWS_REGION}"
    local registry="${2:-$ECR_REGISTRY}"
    
    log_subsection "Validating ECR Access"
    
    # Test ECR repository access
    if ! aws ecr describe-repositories --region "$region" --max-items 1 >/dev/null 2>&1; then
        log_error "Cannot access ECR repositories in region $region"
        return 1
    fi
    
    # Validate ECR registry format
    if [[ ! "$registry" =~ ^[0-9]+\.dkr\.ecr\.[a-z0-9-]+\.amazonaws\.com$ ]]; then
        log_error "Invalid ECR registry format: $registry"
        log_info "Expected format: ACCOUNT.dkr.ecr.REGION.amazonaws.com"
        return 1
    fi
    
    log_success "ECR access validated"
    log_info "  Registry: $registry"
    log_info "  Region: $region"
    
    return 0
}

# =============================================================================
# Docker Configuration Validation
# =============================================================================

# Validate Docker daemon is running
validate_docker_daemon() {
    log_subsection "Validating Docker Daemon"
    
    if ! docker info >/dev/null 2>&1; then
        log_critical "Docker daemon is not running or not accessible"
        return 1
    fi
    
    # Get Docker version info
    local docker_version
    docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "unknown")
    
    log_success "Docker daemon is running"
    log_info "  Version: $docker_version"
    
    return 0
}

# Validate docker-compose is available
validate_docker_compose() {
    log_subsection "Validating Docker Compose"
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_critical "docker-compose is not installed"
        return 1
    fi
    
    local compose_version
    compose_version=$(docker-compose version --short 2>/dev/null || echo "unknown")
    
    log_success "Docker Compose is available"
    log_info "  Version: $compose_version"
    
    return 0
}

# Validate docker-compose configuration
validate_compose_config() {
    local compose_file="${1:-docker-compose.yml}"
    
    log_subsection "Validating Docker Compose Configuration"
    
    if [[ ! -f "$compose_file" ]]; then
        log_error "Docker Compose file not found: $compose_file"
        return 1
    fi
    
    # Export required environment variables for validation
    export AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-310829530903}"
    export AWS_REGION="${AWS_REGION:-eu-north-1}"
    export ECR_REGISTRY="${ECR_REGISTRY:-}"
    
    # Validate configuration syntax
    if ! docker-compose -f "$compose_file" config >/dev/null 2>&1; then
        log_error "Invalid docker-compose configuration in $compose_file"
        log_debug "Attempting to show configuration errors:"
        docker-compose -f "$compose_file" config 2>&1 | head -20
        return 1
    fi
    
    log_success "Docker Compose configuration is valid"
    
    # List available services
    local services
    services=$(docker-compose -f "$compose_file" config --services)
    log_info "Available services:"
    echo "$services" | while read -r service; do
        log_info "  - $service"
    done
    
    return 0
}

# =============================================================================
# File and Directory Validation
# =============================================================================

# Validate file exists and is readable
validate_file_exists() {
    local file_path="$1"
    local file_description="${2:-file}"
    
    if [[ ! -f "$file_path" ]]; then
        log_error "$file_description not found: $file_path"
        return 1
    fi
    
    if [[ ! -r "$file_path" ]]; then
        log_error "$file_description not readable: $file_path"
        return 1
    fi
    
    log_debug "File validated: $file_path"
    return 0
}

# Validate directory exists and is accessible
validate_directory_exists() {
    local dir_path="$1"
    local dir_description="${2:-directory}"
    
    if [[ ! -d "$dir_path" ]]; then
        log_error "$dir_description not found: $dir_path"
        return 1
    fi
    
    if [[ ! -r "$dir_path" ]] || [[ ! -x "$dir_path" ]]; then
        log_error "$dir_description not accessible: $dir_path"
        return 1
    fi
    
    log_debug "Directory validated: $dir_path"
    return 0
}

# Validate file checksum
validate_file_checksum() {
    local file_path="$1"
    local expected_checksum="$2"
    local algorithm="${3:-sha256}"
    
    if [[ ! -f "$file_path" ]]; then
        log_error "File not found for checksum validation: $file_path"
        return 1
    fi
    
    local actual_checksum
    case "$algorithm" in
        sha256)
            actual_checksum=$(sha256sum "$file_path" | cut -d' ' -f1)
            ;;
        sha1)
            actual_checksum=$(sha1sum "$file_path" | cut -d' ' -f1)
            ;;
        md5)
            actual_checksum=$(md5sum "$file_path" | cut -d' ' -f1)
            ;;
        *)
            log_error "Unknown checksum algorithm: $algorithm"
            return 1
            ;;
    esac
    
    if [[ "$actual_checksum" != "$expected_checksum" ]]; then
        log_error "Checksum mismatch for $file_path"
        log_error "  Expected: $expected_checksum"
        log_error "  Actual: $actual_checksum"
        return 1
    fi
    
    log_success "Checksum validated for $file_path"
    return 0
}

# =============================================================================
# Network and Connectivity Validation
# =============================================================================

# Validate network connectivity to host
validate_connectivity() {
    local host="$1"
    local port="${2:-443}"
    local timeout="${3:-5}"
    
    log_debug "Testing connectivity to $host:$port"
    
    if command -v nc >/dev/null 2>&1; then
        if nc -z -w "$timeout" "$host" "$port" 2>/dev/null; then
            log_success "Connectivity validated: $host:$port"
            return 0
        fi
    elif command -v timeout >/dev/null 2>&1; then
        if timeout "$timeout" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
            log_success "Connectivity validated: $host:$port"
            return 0
        fi
    fi
    
    log_error "Cannot connect to $host:$port"
    return 1
}

# =============================================================================
# Composite Validation
# =============================================================================

# Run all prerequisite validations for deployment
validate_deployment_prerequisites() {
    local environment="$1"
    local compose_file="${2:-docker-compose.yml}"
    
    log_section "Validating Deployment Prerequisites for $environment"
    
    local validation_failed=0
    
    # Validate required environment variables
    if ! validate_required_envs \
        "AWS_REGION:AWS region" \
        "ECR_REGISTRY:ECR registry URL" \
        "EC2_HOST:EC2 host address" \
        "EC2_USER:EC2 username"; then
        validation_failed=1
    fi
    
    # Validate AWS configuration
    if ! validate_aws_credentials; then
        validation_failed=1
    fi
    
    if ! validate_ecr_access; then
        validation_failed=1
    fi
    
    # Validate Docker configuration
    if ! validate_docker_daemon; then
        validation_failed=1
    fi
    
    if ! validate_docker_compose; then
        validation_failed=1
    fi
    
    if ! validate_compose_config "$compose_file"; then
        validation_failed=1
    fi
    
    if [[ $validation_failed -eq 0 ]]; then
        log_success "All deployment prerequisites validated successfully"
    else
        log_critical "Deployment prerequisite validation failed"
    fi
    
    return $validation_failed
}

# =============================================================================
# Export Functions
# =============================================================================

export -f validate_required_env
export -f validate_env_with_default
export -f validate_required_envs
export -f validate_input_enum
export -f validate_container_names
export -f validate_aws_credentials
export -f validate_ecr_access
export -f validate_docker_daemon
export -f validate_docker_compose
export -f validate_compose_config
export -f validate_file_exists
export -f validate_directory_exists
export -f validate_file_checksum
export -f validate_connectivity
export -f validate_deployment_prerequisites