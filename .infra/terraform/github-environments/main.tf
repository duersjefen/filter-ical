# =============================================================================
# Infrastructure as Code: GitHub Environments
# =============================================================================
#
# Industry Best Practice: Terraform for Infrastructure as Code
# Manages GitHub Environments, protection rules, and variables
#
# Usage:
#   terraform init
#   terraform plan
#   terraform apply
#
# =============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

# Configure the GitHub Provider
provider "github" {
  # Uses GITHUB_TOKEN environment variable
  # Generate token at: https://github.com/settings/tokens/new
  # Required scopes: repo, admin:repo_hook, admin:org_hook
}

# =============================================================================
# Variables
# =============================================================================

variable "repository_name" {
  description = "GitHub repository name"
  type        = string
  default     = "ical-viewer"
}

variable "repository_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "duersjefen"
}

variable "production_domain" {
  description = "Production domain name"
  type        = string
  default     = "filter-ical.de"
}

variable "staging_domain" {
  description = "Staging domain name"
  type        = string
  default     = "staging.filter-ical.de"
}

variable "development_domain" {
  description = "Development domain name"
  type        = string
  default     = "dev.filter-ical.de"
}

# =============================================================================
# Repository Data
# =============================================================================

data "github_repository" "repo" {
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# =============================================================================
# Development Environment
# =============================================================================

resource "github_repository_environment" "development" {
  repository  = data.github_repository.repo.name
  environment = "development"
  
  # No protection rules for development (fast iteration)
  # Anyone can deploy to development environment
}

# Note: Environment variables will be set manually in GitHub UI
# github_repository_environment_variable is not supported in this provider version

# =============================================================================
# Staging Environment
# =============================================================================

resource "github_repository_environment" "staging" {
  repository  = data.github_repository.repo.name
  environment = "staging"
  
  # Protected branches only (main/master)
  deployment_branch_policy {
    protected_branches     = true
    custom_branch_policies = false
  }
}

# Note: Environment variables will be set manually in GitHub UI
# github_repository_environment_variable is not supported in this provider version

# =============================================================================
# Production Environment (GitHub Pro required for protection rules)
# =============================================================================

resource "github_repository_environment" "production" {
  repository  = data.github_repository.repo.name
  environment = "production"
  
  # Note: Protection rules require GitHub Pro/Team/Enterprise
  # For free tier, this will create environment without protection
  
  # Uncomment these when you have GitHub Pro:
  # wait_timer = 300  # 5 minutes
  # 
  # reviewers {
  #   users = [data.github_user.current.id]
  # }
  
  deployment_branch_policy {
    protected_branches     = true
    custom_branch_policies = false
  }
}

# Note: Environment variables will be set manually in GitHub UI
# github_repository_environment_variable is not supported in this provider version

# =============================================================================
# Outputs
# =============================================================================

output "environments_created" {
  description = "List of created environments"
  value = [
    github_repository_environment.development.environment,
    github_repository_environment.staging.environment,
    github_repository_environment.production.environment
  ]
}

output "repository_environments_url" {
  description = "URL to view environments in GitHub"
  value = "https://github.com/${var.repository_owner}/${var.repository_name}/settings/environments"
}

output "terraform_state_info" {
  description = "Information about Terraform state"
  value = {
    message = "Environments managed by Terraform - modify via code, not GitHub UI"
    warning = "Direct changes in GitHub UI will be overridden on next terraform apply"
  }
}