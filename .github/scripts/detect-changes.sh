#!/bin/bash
# =============================================================================
# Intelligent Change Detection for Multi-Component Deployments
# =============================================================================
# Framework-agnostic change detection with robust fallback strategies

set -euo pipefail

# =============================================================================
# SMART CHANGE DETECTION FUNCTIONS
# =============================================================================

# Main change detection orchestrator
detect_all_changes() {
    echo "🔍 Analyzing repository changes for targeted deployment..."
    
    # Detect frontend changes
    local frontend_changed=$(detect_component_changes "frontend" "^frontend/|^infrastructure/production-nginx.conf")
    
    # Detect backend changes  
    local backend_changed=$(detect_component_changes "backend" "^backend/")
    
    # Output results for GitHub Actions or local testing
    if [ -n "${GITHUB_OUTPUT:-}" ]; then
        echo "frontend_changed=$frontend_changed" >> "$GITHUB_OUTPUT"
        echo "backend_changed=$backend_changed" >> "$GITHUB_OUTPUT"
    else
        echo "frontend_changed=$frontend_changed"
        echo "backend_changed=$backend_changed"
    fi
    
    # Summary
    echo ""
    echo "📋 Change Detection Summary:"
    echo "   Frontend: $(format_change_result $frontend_changed)"
    echo "   Backend:  $(format_change_result $backend_changed)"
    echo ""
    
    # Return whether any changes were detected
    if [ "$frontend_changed" = "true" ] || [ "$backend_changed" = "true" ]; then
        return 0
    else
        return 1
    fi
}

# Universal component change detection with multiple fallback strategies
detect_component_changes() {
    local component="$1"
    local pattern="$2"
    
    echo "📁 Checking for $component changes (pattern: $pattern)..." >&2
    
    # Strategy 1: Compare with previous commit (ideal case)
    if git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E "$pattern" >/dev/null 2>&1; then
        echo "✅ $component changes detected (HEAD~1 comparison)" >&2
        echo "true"
        return 0
    fi
    
    # Strategy 2: Compare with origin/master (for PRs and shallow clones)
    if git diff --name-only origin/master HEAD 2>/dev/null | grep -E "$pattern" >/dev/null 2>&1; then
        echo "✅ $component changes detected (origin/master comparison)" >&2
        echo "true"
        return 0
    fi
    
    # Strategy 3: Check current commit only (fallback for single commits)
    if git show --name-only HEAD | grep -E "$pattern" >/dev/null 2>&1; then
        echo "✅ $component changes detected (HEAD commit analysis)" >&2
        echo "true"
        return 0
    fi
    
    # Strategy 4: Force update for new/unknown repositories (fail-safe)
    if ! git rev-parse HEAD~1 >/dev/null 2>&1; then
        echo "⚠️ $component change detection uncertain (new repo) - FORCING update for safety" >&2
        echo "true"
        return 0
    fi
    
    # No changes detected
    echo "⏭️ No $component changes detected" >&2
    echo "false"
    return 1
}

# Format change detection result for display
format_change_result() {
    local changed="$1"
    
    if [ "$changed" = "true" ]; then
        echo "UPDATE REQUIRED"
    else
        echo "No changes"
    fi
}

# Advanced change detection for specific file types
detect_infrastructure_changes() {
    local pattern="^infrastructure/|^\.github/workflows/|^docker-compose|^Dockerfile"
    
    if git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E "$pattern" >/dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

detect_config_changes() {
    local pattern="^.*\.conf$|^.*\.yaml$|^.*\.yml$|^.*\.json$"
    
    if git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E "$pattern" >/dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

# Check if deployment can be completely skipped
can_skip_deployment() {
    local frontend_changed="$1"
    local backend_changed="$2"
    
    if [ "$frontend_changed" = "false" ] && [ "$backend_changed" = "false" ]; then
        echo "true"
    else
        echo "false"
    fi
}

# Main execution
main() {
    if detect_all_changes; then
        echo "🚀 Changes detected - deployment required"
        exit 0
    else
        echo "✨ No changes detected - deployment can be skipped"
        exit 0
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi