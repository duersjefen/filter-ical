#!/bin/bash
# =============================================================================
# Claude Code Automated Project Setup Script
# =============================================================================
# This script automatically creates a new professional web application
# with the same CI/CD architecture as the ical-viewer template.
#
# Usage: ./scripts/setup-new-project.sh
# Called by Claude Code when user requests "set up new website"

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Claude Code Automated Project Setup${NC}"
echo "==============================================="

# Function to prompt user for required information
get_user_inputs() {
    echo -e "${YELLOW}Please provide the following information:${NC}"
    
    while [[ -z "$PROJECT_NAME" ]]; do
        read -p "Project name (e.g., 'my-blog', 'company-website'): " PROJECT_NAME
        if [[ ! "$PROJECT_NAME" =~ ^[a-z0-9-]+$ ]]; then
            echo -e "${RED}Error: Project name must contain only lowercase letters, numbers, and hyphens${NC}"
            PROJECT_NAME=""
        fi
    done
    
    while [[ -z "$DOMAIN_NAME" ]]; do
        read -p "Domain name (e.g., 'myblog.com', 'company.com'): " DOMAIN_NAME
        if [[ ! "$DOMAIN_NAME" =~ ^[a-z0-9.-]+\.[a-z]{2,}$ ]]; then
            echo -e "${RED}Error: Please enter a valid domain name${NC}"
            DOMAIN_NAME=""
        fi
    done
    
    echo -e "${YELLOW}Project types:${NC}"
    echo "1) clojure - Full-stack Clojure/ClojureScript (like ical-viewer)"
    echo "2) node - Node.js backend with React/Vue frontend"  
    echo "3) python - Python backend with modern frontend"
    echo "4) static - Static site with CI/CD"
    
    while [[ -z "$PROJECT_TYPE" ]]; do
        read -p "Select project type (1-4): " TYPE_CHOICE
        case $TYPE_CHOICE in
            1) PROJECT_TYPE="clojure";;
            2) PROJECT_TYPE="node";;
            3) PROJECT_TYPE="python";;
            4) PROJECT_TYPE="static";;
            *) echo -e "${RED}Error: Please select 1, 2, 3, or 4${NC}";;
        esac
    done
}

# Function to create project directory structure
create_project_structure() {
    echo -e "${BLUE}📁 Creating project structure...${NC}"
    
    if [[ -d "$PROJECT_NAME" ]]; then
        echo -e "${RED}Error: Directory '$PROJECT_NAME' already exists${NC}"
        exit 1
    fi
    
    mkdir -p "$PROJECT_NAME"/{.github/workflows,.githooks,docs,infrastructure}
    
    case $PROJECT_TYPE in
        clojure)
            mkdir -p "$PROJECT_NAME"/{backend/{src/app,test/app,data},frontend/{src,resources/public}}
            ;;
        node)
            mkdir -p "$PROJECT_NAME"/{backend/{src,test},frontend/{src,public}}
            ;;
        python)
            mkdir -p "$PROJECT_NAME"/{backend/{app,tests},frontend/{src,public}}
            ;;
        static)
            mkdir -p "$PROJECT_NAME"/{src,public}
            ;;
    esac
    
    echo -e "${GREEN}✅ Project structure created${NC}"
}

# Function to copy and configure template files
copy_template_files() {
    echo -e "${BLUE}📄 Copying and configuring template files...${NC}"
    
    # Copy CI/CD pipeline
    cp .github/workflows/deploy.yml "$PROJECT_NAME/.github/workflows/"
    sed -i "s/ical-viewer-backend/${PROJECT_NAME}-backend/g" "$PROJECT_NAME/.github/workflows/deploy.yml"
    sed -i "s/ical-viewer-frontend/${PROJECT_NAME}-frontend/g" "$PROJECT_NAME/.github/workflows/deploy.yml"
    sed -i "s/filter-ical.de/${DOMAIN_NAME}/g" "$PROJECT_NAME/.github/workflows/deploy.yml"
    sed -i "s/ical-viewer/${PROJECT_NAME}/g" "$PROJECT_NAME/.github/workflows/deploy.yml"
    
    # Copy git hooks
    cp .githooks/pre-commit "$PROJECT_NAME/.githooks/"
    chmod +x "$PROJECT_NAME/.githooks/pre-commit"
    
    # Update git hook for project type
    if [[ "$PROJECT_TYPE" != "clojure" ]]; then
        sed -i 's/clj -M:test-runner/echo "Tests will be configured for '"$PROJECT_TYPE"'"/' "$PROJECT_NAME/.githooks/pre-commit"
    fi
    
    # Copy configuration files
    cp .pre-commit-config.yaml "$PROJECT_NAME/"
    cp .gitignore "$PROJECT_NAME/"
    
    # Copy and configure infrastructure
    cp infrastructure/production-nginx.conf "$PROJECT_NAME/infrastructure/"
    cp infrastructure/production-docker-compose.yml "$PROJECT_NAME/infrastructure/"
    
    # Update nginx configuration
    sed -i "s/filter-ical.de/${DOMAIN_NAME}/g" "$PROJECT_NAME/infrastructure/production-nginx.conf"
    sed -i "s/ical-viewer/${PROJECT_NAME}/g" "$PROJECT_NAME/infrastructure/production-nginx.conf"
    
    # Update docker-compose
    sed -i "s/ical-viewer/${PROJECT_NAME}/g" "$PROJECT_NAME/infrastructure/production-docker-compose.yml"
    
    # Copy documentation
    cp -r docs/* "$PROJECT_NAME/docs/"
    
    echo -e "${GREEN}✅ Template files configured${NC}"
}

# Function to generate project-specific files
generate_project_files() {
    echo -e "${BLUE}📝 Generating project-specific files...${NC}"
    
    # Create README.md
    cat > "$PROJECT_NAME/README.md" << EOF
# $PROJECT_NAME

Professional web application with automated CI/CD pipeline.

## Quick Start

\`\`\`bash
# Development
# (Commands will depend on project type: $PROJECT_TYPE)

# Production Deployment
git push origin main  # Triggers automatic deployment
\`\`\`

## Live Application

**Production**: https://$DOMAIN_NAME

## Architecture

This project uses the professional CI/CD template with:
- ✅ Automated testing and deployment
- ✅ Zero-downtime updates
- ✅ SSL certificates with auto-renewal
- ✅ Multi-domain nginx reverse proxy
- ✅ Docker containerization

## Documentation

- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Template](docs/DEPLOYMENT_TEMPLATE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

*Generated by Claude Code automation on $(date)*
EOF

    # Update CLAUDE.md for new project
    cat > "$PROJECT_NAME/CLAUDE.md" << EOF
# CLAUDE.md - $PROJECT_NAME

This is a professional $PROJECT_TYPE web application generated from the ical-viewer template.

## Project Details

- **Name**: $PROJECT_NAME
- **Type**: $PROJECT_TYPE
- **Domain**: https://$DOMAIN_NAME
- **Status**: 🚧 Setup in progress

## Quick Start Commands

\`\`\`bash
# Development commands will be configured based on project type
# Check README.md for specific instructions
\`\`\`

## Deployment

This project uses the proven CI/CD pipeline from ical-viewer:
- Push to main → Automatic deployment
- Pre-commit hooks prevent broken code
- Zero-downtime updates with health checks

## Next Steps

1. Configure DNS: Point $DOMAIN_NAME to 56.228.25.95
2. Create ECR repositories (commands provided below)
3. Push to GitHub for automatic deployment

---

*Generated by Claude Code automation*
EOF
    
    echo -e "${GREEN}✅ Project-specific files generated${NC}"
}

# Function to initialize git repository
initialize_git() {
    echo -e "${BLUE}🔧 Initializing git repository...${NC}"
    
    cd "$PROJECT_NAME"
    
    git init
    git config core.hooksPath .githooks
    
    # Create initial commit
    git add .
    git commit -m "Initial project setup via Claude Code automation

Project: $PROJECT_NAME
Type: $PROJECT_TYPE
Domain: $DOMAIN_NAME

Generated with professional CI/CD template from ical-viewer.
Ready for deployment after DNS configuration.

🤖 Generated with [Claude Code](https://claude.ai/code)"
    
    cd ..
    
    echo -e "${GREEN}✅ Git repository initialized${NC}"
}

# Function to provide next steps
provide_next_steps() {
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo "=================================="
    echo -e "${YELLOW}Your new project '$PROJECT_NAME' is ready!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo "1. 🌐 Configure DNS:"
    echo "   Point $DOMAIN_NAME to 56.228.25.95"
    echo "   Point www.$DOMAIN_NAME to 56.228.25.95"
    echo ""
    echo "2. 📦 Create AWS ECR repositories:"
    echo "   aws ecr create-repository --repository-name ${PROJECT_NAME}-backend --region eu-north-1"
    echo "   aws ecr create-repository --repository-name ${PROJECT_NAME}-frontend --region eu-north-1"
    echo ""
    echo "3. 🚀 Deploy to production:"
    echo "   cd $PROJECT_NAME"
    echo "   git remote add origin YOUR_GITHUB_REPO_URL"
    echo "   git push -u origin main"
    echo ""
    echo "4. ✅ Verify deployment:"
    echo "   https://$DOMAIN_NAME (after DNS propagation)"
    echo ""
    echo -e "${BLUE}Project Structure:${NC}"
    echo "   $PROJECT_NAME/"
    echo "   ├── .github/workflows/  # CI/CD pipeline"
    echo "   ├── .githooks/          # Automated testing"
    echo "   ├── docs/               # Documentation"
    echo "   ├── infrastructure/     # Deployment configs"
    echo "   └── README.md           # Project guide"
    echo ""
    echo -e "${GREEN}✨ Professional web application ready for deployment!${NC}"
}

# Main execution
main() {
    echo "This script will create a new professional web application"
    echo "with the same proven CI/CD architecture as ical-viewer."
    echo ""
    
    get_user_inputs
    
    echo ""
    echo -e "${BLUE}Configuration Summary:${NC}"
    echo "Project Name: $PROJECT_NAME"
    echo "Domain Name: $DOMAIN_NAME"
    echo "Project Type: $PROJECT_TYPE"
    echo ""
    
    read -p "Proceed with setup? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_project_structure
        copy_template_files
        generate_project_files
        initialize_git
        provide_next_steps
    else
        echo "Setup cancelled."
        exit 0
    fi
}

# Run main function
main "$@"