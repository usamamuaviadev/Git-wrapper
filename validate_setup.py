#!/usr/bin/env python3
"""
Setup Validation Script

Run this script to validate your GPT Wrapper installation and configuration.
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Print a section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def check_mark(success):
    """Return colored check mark or X."""
    return f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"


def validate_python_version():
    """Check Python version."""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    print(f"{check_mark(is_valid)} Python version: {version.major}.{version.minor}.{version.micro}")
    if not is_valid:
        print(f"  {YELLOW}Warning: Python 3.8+ recommended{RESET}")
    return is_valid


def validate_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    
    deps = {
        'openai': False,
        'requests': False,
        'yaml': False
    }
    
    for package in deps.keys():
        try:
            if package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            deps[package] = True
            print(f"{check_mark(True)} {package} installed")
        except ImportError:
            print(f"{check_mark(False)} {package} NOT installed")
    
    all_installed = all(deps.values())
    if not all_installed:
        print(f"\n{YELLOW}Run: pip install -r requirements.txt{RESET}")
    
    return all_installed


def validate_project_structure():
    """Check if all required files exist."""
    print("Checking project structure...")
    
    required_files = [
        'src/main.py',
        'src/routers/__init__.py',
        'src/routers/router_manager.py',
        'src/routers/openai_router.py',
        'src/routers/local_router.py',
        'src/config/settings.yaml',
        'src/utils/logger.py',
        'src/memory/memory_handler.py',
        'requirements.txt',
        'README.md',
        'docs/system_overview.md'
    ]
    
    all_exist = True
    for filepath in required_files:
        exists = Path(filepath).exists()
        all_exist = all_exist and exists
        status = "✓" if exists else "✗"
        print(f"{check_mark(exists)} {filepath}")
    
    return all_exist


def validate_config():
    """Check configuration file."""
    print("Checking configuration...")
    
    config_path = Path('src/config/settings.yaml')
    if not config_path.exists():
        print(f"{check_mark(False)} settings.yaml not found")
        return False
    
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check required keys
        checks = {
            'active_model exists': 'active_model' in config,
            'active_model valid': config.get('active_model') in ['openai', 'local'],
            'openai config exists': 'openai' in config,
            'local config exists': 'local' in config
        }
        
        for check_name, result in checks.items():
            print(f"{check_mark(result)} {check_name}")
        
        return all(checks.values())
    
    except Exception as e:
        print(f"{check_mark(False)} Error loading config: {e}")
        return False


def validate_api_keys():
    """Check if API keys are configured."""
    print("Checking API keys...")
    
    # Check environment variable
    env_key = os.getenv('OPENAI_API_KEY')
    has_env_key = env_key is not None and len(env_key) > 0
    print(f"{check_mark(has_env_key)} OPENAI_API_KEY environment variable")
    
    # Check .env file
    env_file = Path('.env')
    has_env_file = env_file.exists()
    print(f"{check_mark(has_env_file)} .env file exists")
    
    # Check config file
    try:
        import yaml
        with open('src/config/settings.yaml') as f:
            config = yaml.safe_load(f)
        
        config_key = config.get('openai', {}).get('api_key', '')
        has_config_key = config_key is not None and len(config_key) > 0
        print(f"{check_mark(has_config_key)} API key in settings.yaml")
        
    except:
        has_config_key = False
        print(f"{check_mark(False)} Cannot read settings.yaml")
    
    has_key = has_env_key or has_config_key
    if not has_key:
        print(f"\n{YELLOW}Note: OpenAI API key not configured (required for OpenAI mode){RESET}")
    
    return True  # Not critical for local mode


def validate_ollama():
    """Check if Ollama is accessible."""
    print("Checking Ollama (optional for local mode)...")
    
    try:
        import requests
        response = requests.get('http://localhost:11434/api/version', timeout=2)
        if response.status_code == 200:
            print(f"{check_mark(True)} Ollama server is running")
            version = response.json().get('version', 'unknown')
            print(f"  Version: {version}")
            return True
        else:
            print(f"{check_mark(False)} Ollama responded with status {response.status_code}")
            return False
    except:
        print(f"{check_mark(False)} Ollama not running or not installed")
        print(f"  {YELLOW}Install from: https://ollama.ai{RESET}")
        print(f"  {YELLOW}Start with: ollama serve{RESET}")
        return False


def test_import():
    """Try importing the main modules."""
    print("Testing module imports...")
    
    # Add src to path
    sys.path.insert(0, 'src')
    
    modules = [
        'routers.router_manager',
        'routers.openai_router',
        'routers.local_router',
        'utils.logger',
        'memory.memory_handler'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"{check_mark(True)} {module}")
        except Exception as e:
            print(f"{check_mark(False)} {module}: {e}")
            all_ok = False
    
    return all_ok


def main():
    """Run all validation checks."""
    print(f"{BLUE}GPT Wrapper - Setup Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {}
    
    print_section("1. Python Environment")
    results['python'] = validate_python_version()
    
    print_section("2. Dependencies")
    results['deps'] = validate_dependencies()
    
    print_section("3. Project Structure")
    results['structure'] = validate_project_structure()
    
    print_section("4. Configuration")
    results['config'] = validate_config()
    
    print_section("5. API Keys")
    results['keys'] = validate_api_keys()
    
    print_section("6. Ollama (Local Mode)")
    results['ollama'] = validate_ollama()
    
    print_section("7. Module Imports")
    results['imports'] = test_import()
    
    # Summary
    print_section("Validation Summary")
    
    critical_checks = ['python', 'deps', 'structure', 'config', 'imports']
    optional_checks = ['keys', 'ollama']
    
    critical_pass = all(results[check] for check in critical_checks)
    
    if critical_pass:
        print(f"{GREEN}✓ All critical checks passed!{RESET}")
        print(f"\n{GREEN}Your GPT Wrapper is ready to use!{RESET}\n")
        
        print("Next steps:")
        print("  1. Configure API key for OpenAI mode (if not done)")
        print("  2. Install Ollama for local mode (if desired)")
        print("  3. Run: python src/main.py \"Your prompt here\"")
        print("  4. See QUICKSTART.md for detailed usage\n")
    else:
        print(f"{RED}✗ Some critical checks failed{RESET}")
        print("\nPlease fix the issues above before using GPT Wrapper.\n")
    
    # Optional warnings
    if not results['keys']:
        print(f"{YELLOW}⚠ OpenAI API key not configured (required for OpenAI mode){RESET}")
    
    if not results['ollama']:
        print(f"{YELLOW}⚠ Ollama not available (required for local mode){RESET}")
    
    return 0 if critical_pass else 1


if __name__ == '__main__':
    sys.exit(main())

