#!/bin/bash

# Ubuntu Server Hardening Tool - Modular Structure Demo
# This script demonstrates the new modular architecture and features

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "hardening_tool.py" ]]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_header "UBUNTU SERVER HARDENING TOOL - MODULAR DEMO"

print_info "This demo showcases the new modular architecture of the Ubuntu Server Hardening Tool"
print_info "The tool has been reorganized into a clean, maintainable structure"

# Show project structure
print_header "PROJECT STRUCTURE"
print_info "New modular project layout:"
echo ""
tree -I '__pycache__|*.pyc' || ls -la

# Show available make commands
print_header "AVAILABLE MAKE COMMANDS"
print_info "The tool now includes a Makefile for easy project management:"
echo ""
make help

# Test the help functionality
print_header "MAIN SCRIPT HELP"
print_info "Testing the new main script help functionality:"
echo ""
./hardening_tool.py --help

# Test module imports
print_header "MODULE VALIDATION"
print_info "Testing that all modules can be imported successfully:"
echo ""
python3 -c "
import sys
sys.path.append('src')
try:
    from base_hardening import BaseHardeningTool
    from hardening_steps import Step1_OSHardening, Step2_UserSSHHardening
    print('✅ All modules imported successfully')
    print('✅ BaseHardeningTool class available')
    print('✅ Step1_OSHardening class available') 
    print('✅ Step2_UserSSHHardening class available')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Test configuration loading
print_header "CONFIGURATION VALIDATION"
print_info "Testing configuration file loading:"
echo ""
if [[ -f "config/config_template.json" ]]; then
    print_success "Configuration template found at config/config_template.json"
    python3 -c "
import json
try:
    with open('config/config_template.json', 'r') as f:
        config = json.load(f)
    print('✅ Configuration file is valid JSON')
    print(f'✅ Found {len(config.get(\"users\", []))} user configurations')
    print(f'✅ SSH allowed users: {config.get(\"ssh_allowed_users\", [])}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
else
    print_error "Configuration template not found"
fi

# Test dry-run functionality
print_header "DRY-RUN DEMONSTRATION"
print_info "Testing dry-run mode (safe to run without sudo):"
print_warning "Note: This will show privilege errors, which is expected behavior"
echo ""

# Test individual steps
print_info "Testing Step 1 dry-run:"
./hardening_tool.py --step1 --dry-run || true

echo ""
print_info "Testing Step 2 dry-run:"
./hardening_tool.py --step2 --dry-run || true

# Show make dry-run
print_header "MAKE DRY-RUN DEMONSTRATION"
print_info "Testing make dry-run command:"
echo ""
make dry-run || true

# Show directory structure after execution
print_header "OUTPUT DIRECTORIES"
print_info "Checking generated output directories:"
echo ""

if [[ -d "logs" ]]; then
    print_success "Logs directory exists"
    ls -la logs/ 2>/dev/null || print_info "No log files yet"
else
    print_info "Logs directory will be created on first run"
fi

if [[ -d "results" ]]; then
    print_success "Results directory exists"
    ls -la results/ 2>/dev/null || print_info "No result files yet"
else
    print_info "Results directory will be created on first run"
fi

# Show modular benefits
print_header "MODULAR ARCHITECTURE BENEFITS"
print_info "The new structure provides:"
echo ""
echo "🏗️  Modular Design:"
echo "   • Separate modules for each hardening step"
echo "   • Base class for common functionality"
echo "   • Easy to extend and maintain"
echo ""
echo "📁 Organized File Structure:"
echo "   • Source code in src/ directory"
echo "   • Configuration files in config/ directory"
echo "   • Logs and results in separate directories"
echo "   • Documentation in docs/ directory"
echo ""
echo "🛠️  Development Tools:"
echo "   • Makefile for project management"
echo "   • Automated testing and validation"
echo "   • Code quality tools (lint, format)"
echo ""
echo "🔧 Easy Usage:"
echo "   • Simple make commands"
echo "   • Clear help documentation"
echo "   • Consistent interface"

# Show next steps
print_header "NEXT STEPS"
print_info "To use the hardening tool:"
echo ""
echo "1. 📋 Review configuration:"
echo "   nano config/config_template.json"
echo ""
echo "2. 🧪 Test with dry-run:"
echo "   make dry-run"
echo ""
echo "3. 🚀 Run hardening (requires sudo):"
echo "   sudo make step1      # OS Hardening"
echo "   sudo make step2      # User & SSH Hardening"
echo "   sudo make all-steps  # Both steps"
echo ""
echo "4. 📊 Check results:"
echo "   ls -la results/"
echo "   ls -la logs/"

print_header "DEMO COMPLETED"
print_success "The modular Ubuntu Server Hardening Tool is ready for use!"
print_info "For more information, see docs/PROJECT_STRUCTURE.md"

echo ""