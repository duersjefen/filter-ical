#!/bin/bash
# =============================================================================
# ENTERPRISE LOGGING FRAMEWORK
# =============================================================================
# Provides centralized logging with levels, formatting, and observability
# Author: Claude Code
# =============================================================================

set -euo pipefail

# Color codes for terminal output
readonly COLOR_RESET='\033[0m'
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_GRAY='\033[0;90m'

# Emoji indicators for log levels
readonly EMOJI_SUCCESS="✅"
readonly EMOJI_ERROR="❌"
readonly EMOJI_WARNING="⚠️"
readonly EMOJI_INFO="ℹ️"
readonly EMOJI_DEBUG="🔍"
readonly EMOJI_CRITICAL="🚨"
readonly EMOJI_SECTION="📋"
readonly EMOJI_ROCKET="🚀"
readonly EMOJI_PACKAGE="📦"

# Log levels
readonly LOG_LEVEL_DEBUG=0
readonly LOG_LEVEL_INFO=1
readonly LOG_LEVEL_WARNING=2
readonly LOG_LEVEL_ERROR=3
readonly LOG_LEVEL_CRITICAL=4

# Current log level (can be overridden by environment variable)
LOG_LEVEL="${LOG_LEVEL:-$LOG_LEVEL_INFO}"

# =============================================================================
# Core Logging Functions
# =============================================================================

# Get timestamp in ISO 8601 format
get_timestamp() {
    date -u '+%Y-%m-%dT%H:%M:%S.%3NZ'
}

# Log with specific level and formatting
log() {
    local level="$1"
    local message="$2"
    local emoji="${3:-}"
    local color="${4:-$COLOR_RESET}"
    
    # Check if we should log this level
    local numeric_level
    case "$level" in
        DEBUG) numeric_level=$LOG_LEVEL_DEBUG ;;
        INFO) numeric_level=$LOG_LEVEL_INFO ;;
        WARNING) numeric_level=$LOG_LEVEL_WARNING ;;
        ERROR) numeric_level=$LOG_LEVEL_ERROR ;;
        CRITICAL) numeric_level=$LOG_LEVEL_CRITICAL ;;
        *) numeric_level=$LOG_LEVEL_INFO ;;
    esac
    
    if [[ $numeric_level -lt $LOG_LEVEL ]]; then
        return 0
    fi
    
    # Format output based on environment
    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        # GitHub Actions format with proper grouping
        echo -e "${emoji} [$(get_timestamp)] [$level] $message"
        
        # Add GitHub Actions annotations for errors/warnings
        case "$level" in
            ERROR|CRITICAL)
                echo "::error::$message"
                ;;
            WARNING)
                echo "::warning::$message"
                ;;
        esac
    else
        # Local terminal format with colors
        echo -e "${color}${emoji} [$(get_timestamp)] [$level] $message${COLOR_RESET}"
    fi
    
    # Also log to file if LOG_FILE is set
    if [[ -n "${LOG_FILE:-}" ]]; then
        echo "[$(get_timestamp)] [$level] $message" >> "$LOG_FILE"
    fi
}

# =============================================================================
# Convenience Functions
# =============================================================================

log_debug() {
    log "DEBUG" "$1" "$EMOJI_DEBUG" "$COLOR_GRAY"
}

log_info() {
    log "INFO" "$1" "$EMOJI_INFO" "$COLOR_CYAN"
}

log_warning() {
    log "WARNING" "$1" "$EMOJI_WARNING" "$COLOR_YELLOW"
}

log_error() {
    log "ERROR" "$1" "$EMOJI_ERROR" "$COLOR_RED"
}

log_critical() {
    log "CRITICAL" "$1" "$EMOJI_CRITICAL" "$COLOR_RED"
}

log_success() {
    log "INFO" "$1" "$EMOJI_SUCCESS" "$COLOR_GREEN"
}

log_section() {
    local title="$1"
    echo ""
    log "INFO" "════════════════════════════════════════════" "" "$COLOR_BLUE"
    log "INFO" "$EMOJI_SECTION $title" "" "$COLOR_BLUE"
    log "INFO" "════════════════════════════════════════════" "" "$COLOR_BLUE"
}

log_subsection() {
    local title="$1"
    echo ""
    log "INFO" "──────────────────────────────" "" "$COLOR_CYAN"
    log "INFO" "$title" "" "$COLOR_CYAN"
    log "INFO" "──────────────────────────────" "" "$COLOR_CYAN"
}

# =============================================================================
# Structured Logging
# =============================================================================

# Log JSON structured data for observability platforms
log_json() {
    local level="$1"
    local event="$2"
    shift 2
    
    local json='{'
    json+='"timestamp":"'$(get_timestamp)'",'
    json+='"level":"'$level'",'
    json+='"event":"'$event'"'
    
    # Add additional key-value pairs
    while [[ $# -gt 0 ]]; do
        local key="$1"
        local value="$2"
        json+=',"'$key'":"'$value'"'
        shift 2 || break
    done
    
    json+='}'
    
    # Output to structured log if configured
    if [[ -n "${STRUCTURED_LOG_FILE:-}" ]]; then
        echo "$json" >> "$STRUCTURED_LOG_FILE"
    fi
    
    # Also log human-readable version
    log "$level" "Event: $event"
}

# =============================================================================
# Progress Indicators
# =============================================================================

# Start a collapsible group (GitHub Actions)
start_group() {
    local title="$1"
    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        echo "::group::$title"
    fi
    log_subsection "$title"
}

# End a collapsible group
end_group() {
    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        echo "::endgroup::"
    fi
}

# Show progress for long-running operations
log_progress() {
    local current="$1"
    local total="$2"
    local operation="$3"
    
    local percentage=$((current * 100 / total))
    log_info "Progress: $current/$total ($percentage%) - $operation"
}

# =============================================================================
# Error Context
# =============================================================================

# Log error with context information
log_error_context() {
    local error_msg="$1"
    local context="${2:-}"
    
    log_error "$error_msg"
    
    if [[ -n "$context" ]]; then
        log_debug "Context: $context"
    fi
    
    # Log stack trace if available
    if [[ ${#BASH_SOURCE[@]} -gt 1 ]]; then
        log_debug "Stack trace:"
        for ((i=1; i<${#BASH_SOURCE[@]}; i++)); do
            log_debug "  at ${BASH_SOURCE[$i]}:${BASH_LINENO[$i-1]}"
        done
    fi
}

# =============================================================================
# Metrics and Telemetry
# =============================================================================

# Record deployment metrics
log_metric() {
    local metric_name="$1"
    local value="$2"
    local unit="${3:-}"
    
    log_json "INFO" "metric" \
        "name" "$metric_name" \
        "value" "$value" \
        "unit" "$unit" \
        "timestamp" "$(get_timestamp)"
    
    # Also send to monitoring service if configured
    if [[ -n "${METRICS_ENDPOINT:-}" ]]; then
        # This would integrate with your monitoring service
        :
    fi
}

# Log deployment event for audit trail
log_deployment_event() {
    local event_type="$1"
    local environment="$2"
    local version="$3"
    local status="$4"
    
    log_json "INFO" "deployment" \
        "type" "$event_type" \
        "environment" "$environment" \
        "version" "$version" \
        "status" "$status" \
        "actor" "${GITHUB_ACTOR:-unknown}" \
        "repository" "${GITHUB_REPOSITORY:-unknown}"
}

# =============================================================================
# Export Functions
# =============================================================================

# Make functions available to subshells
export -f log
export -f log_debug
export -f log_info
export -f log_warning
export -f log_error
export -f log_critical
export -f log_success
export -f log_section
export -f log_subsection
export -f log_json
export -f start_group
export -f end_group
export -f log_progress
export -f log_error_context
export -f log_metric
export -f log_deployment_event