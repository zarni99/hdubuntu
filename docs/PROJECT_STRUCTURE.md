# Ubuntu Server Hardening Tool - Project Structure

## 📁 Directory Structure

```
ubuntu-hardening-tool/
├── README.md                           # Main documentation
├── Makefile                           # Project management commands
├── hardening_tool.py                 # Main entry point (executable)
├── requirements.txt                   # Python dependencies
├── ubuntu_hardening_tool_old.py      # Legacy monolithic version (backup)
│
├── config/                           # Configuration files
│   └── config_template.json         # Default configuration template
│
├── src/                             # Source code modules
│   ├── __init__.py                  # Package initialization
│   ├── base_hardening.py            # Base classes and utilities
│   └── hardening_steps/             # Individual hardening step modules
│       ├── __init__.py              # Package initialization
│       ├── step1_os_hardening.py    # Step 1: OS Hardening
│       ├── step2_user_ssh_hardening.py  # Step 2: User & SSH Hardening
│       └── step2_template.py        # Template for future steps
│
├── demos/                           # Demo and test scripts
│   ├── test_demo.sh                 # General demo script
│   └── step2_demo.sh                # Step 2 specific demo
│
├── logs/                            # Log files (auto-created)
│   └── hardening_YYYYMMDD_HHMMSS.log
│
├── results/                         # Results and reports (auto-created)
│   └── stepX_results_YYYYMMDD_HHMMSS.json
│
└── docs/                           # Additional documentation
    └── PROJECT_STRUCTURE.md        # This file
```

## 🔧 Key Components

### Main Entry Point
- **`hardening_tool.py`** - New modular main script
- **`ubuntu_hardening_tool_old.py`** - Legacy monolithic version (backup)

### Core Modules
- **`src/base_hardening.py`** - Base class with common functionality
- **`src/hardening_steps/`** - Individual step implementations

### Configuration
- **`config/config_template.json`** - Default configuration template
- Custom configurations can be placed in the `config/` directory

### Automation
- **`Makefile`** - Project management and common tasks
- **`demos/`** - Demo scripts for testing and demonstration

## 🚀 Usage Examples

### Using Make Commands
```bash
make help          # Show available commands
make install       # Set up the tool
make test          # Validate installation
make demo          # Run demonstrations
make dry-run       # Preview all changes
make step1         # Run Step 1 (requires sudo)
make step2         # Run Step 2 (requires sudo)
make all-steps     # Run all steps (requires sudo)
make clean         # Clean up temporary files
```

### Direct Script Usage
```bash
./hardening_tool.py --help
./hardening_tool.py --step1 --dry-run
./hardening_tool.py --step1 --step2 --config config/custom.json
sudo ./hardening_tool.py --step1 --step2
```

## 📦 Modular Design Benefits

1. **Separation of Concerns** - Each step is in its own module
2. **Maintainability** - Easy to update individual components
3. **Extensibility** - Simple to add new hardening steps
4. **Testability** - Individual modules can be tested separately
5. **Reusability** - Base classes provide common functionality

## 🔄 Adding New Steps

To add a new hardening step:

1. Create `src/hardening_steps/stepX_description.py`
2. Inherit from `BaseHardeningTool`
3. Implement the step logic
4. Add import to `src/hardening_steps/__init__.py`
5. Update `hardening_tool.py` main function
6. Update configuration template if needed
7. Create demo script in `demos/`

## 🛠️ Development Workflow

1. **Setup**: `make install && make dev-setup`
2. **Development**: Edit modules in `src/`
3. **Testing**: `make test && make demo`
4. **Linting**: `make lint`
5. **Formatting**: `make format`
6. **Cleanup**: `make clean`

## 📋 File Responsibilities

| File/Directory | Purpose |
|----------------|---------|
| `hardening_tool.py` | Main entry point, argument parsing, orchestration |
| `src/base_hardening.py` | Common utilities, logging, configuration, prerequisites |
| `src/hardening_steps/step1_*.py` | Step 1 implementation (OS hardening) |
| `src/hardening_steps/step2_*.py` | Step 2 implementation (User & SSH hardening) |
| `config/` | Configuration files and templates |
| `demos/` | Test and demonstration scripts |
| `logs/` | Runtime logs (auto-created) |
| `results/` | Execution results and reports (auto-created) |
| `Makefile` | Project automation and common tasks |