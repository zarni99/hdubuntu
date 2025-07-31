# Ubuntu Server Hardening Tool - Makefile
# CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS

.PHONY: help install test clean demo step1 step2 step3 step4 all-steps dry-run

# Default target
help:
	@echo "Ubuntu Server Hardening Tool - Available Commands:"
	@echo ""
	@echo "  make install     - Install dependencies and set up the tool"
	@echo "  make test        - Run tests and validation"
	@echo "  make demo        - Run demonstration scripts"
	@echo "  make clean       - Clean up logs and temporary files"
	@echo ""
	@echo "  make step1       - Run Step 1: OS Hardening (requires sudo)"
	@echo "  make step2       - Run Step 2: User & SSH Hardening (requires sudo)"
	@echo "  make step3       - Run Step 3: Firewall & Network Security (requires sudo)"
	@echo "  make step4       - Run Step 4: Kernel & Sysctl Hardening (requires sudo)"
	@echo "  make all-steps   - Run all hardening steps (requires sudo)"
	@echo "  make dry-run     - Preview all changes without executing"
	@echo ""
	@echo "  make help        - Show this help message"

# Install dependencies and set up the tool
install:
	@echo "Setting up Ubuntu Hardening Tool..."
	@sudo apt update
	@sudo apt install -y python3 python3-pip ufw
	@chmod +x hardening_tool.py
	@chmod +x demos/*.sh
	@echo "✓ Installation completed!"

# Run tests and validation
test:
	@echo "Running tool validation..."
	@python3 -c "import sys; sys.path.append('src'); from hardening_steps import Step1_OSHardening, Step2_UserSSHHardening, Step3_NetworkSecurity, Step4_KernelSysctlHardening; print('✓ All modules imported successfully')"
	@./hardening_tool.py --help > /dev/null && echo "✓ Main script is functional"
	@echo "✓ All tests passed!"

# Run demonstration scripts
demo:
	@echo "Running demonstration scripts..."
	@./demos/test_demo.sh
	@echo ""
	@./demos/step2_demo.sh
	@echo ""
	@./demos/step4_demo.sh
	@echo ""
	@./demos/modular_demo.sh

# Clean up logs and temporary files
clean:
	@echo "Cleaning up temporary files..."
	@rm -f logs/*.log
	@rm -f results/*.json
	@rm -f *.log
	@rm -f *_results_*.json
	@echo "✓ Cleanup completed!"

# Run Step 1: OS Hardening (requires sudo)
step1:
	@echo "Running Step 1: Operating System Hardening..."
	@sudo ./hardening_tool.py --step1

# Run Step 2: User & SSH Hardening (requires sudo)
step2:
	@echo "Running Step 2: User and SSH Hardening..."
	@sudo ./hardening_tool.py --step2

# Run Step 3: Firewall & Network Security (requires sudo)
step3:
	@echo "Running Step 3: Firewall and Network Security..."
	@sudo ./hardening_tool.py --step3

# Run Step 4: Kernel & Sysctl Hardening (requires sudo)
step4:
	@echo "Running Step 4: Kernel and Sysctl Hardening..."
	@sudo ./hardening_tool.py --step4

# Run all hardening steps (requires sudo)
all-steps:
	@echo "Running all hardening steps..."
	@sudo ./hardening_tool.py --step1 --step2 --step3 --step4

# Preview all changes without executing
dry-run:
	@echo "Previewing all hardening changes (dry-run mode)..."
	@./hardening_tool.py --step1 --step2 --step3 --step4 --dry-run --log-level INFO

# Development targets
dev-setup:
	@echo "Setting up development environment..."
	@pip3 install --user black flake8 pytest
	@echo "✓ Development tools installed!"

lint:
	@echo "Running code linting..."
	@python3 -m flake8 src/ hardening_tool.py --max-line-length=120
	@echo "✓ Linting completed!"

format:
	@echo "Formatting code..."
	@python3 -m black src/ hardening_tool.py --line-length=120
	@echo "✓ Code formatting completed!"