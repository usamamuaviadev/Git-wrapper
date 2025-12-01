#!/usr/bin/env python3
"""
Setup Validation Script

Run this script to validate your GPT Wrapper installation and configuration.
Tests both OpenAI and Ollama routes if available.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

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


def print_status(status, message):
    """Print a status message with color coding."""
    status_map = {
        "OK": f"{GREEN}✓ OK{RESET}",
        "SKIPPED": f"{YELLOW}⊘ SKIPPED{RESET}",
        "FAILED": f"{RED}✗ FAILED{RESET}"
    }
    status_symbol = status_map.get(status, status)
    print(f"{status_symbol} {message}")


def validate_python_version():
    """Check Python version."""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    print(f"{GREEN if is_valid else RED}{'✓' if is_valid else '✗'}{RESET} Python version: {version.major}.{version.minor}.{version.micro}")
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
            print(f"{GREEN}✓{RESET} {package} installed")
        except ImportError:
            print(f"{RED}✗{RESET} {package} NOT installed")
    
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
        'README.md'
    ]
    
    all_exist = True
    for filepath in required_files:
        exists = Path(filepath).exists()
        all_exist = all_exist and exists
        status = "✓" if exists else "✗"
        color = GREEN if exists else RED
        print(f"{color}{status}{RESET} {filepath}")
    
    return all_exist


def validate_config():
    """Check configuration file."""
    print("Checking configuration...")
    
    config_path = Path('src/config/settings.yaml')
    if not config_path.exists():
        print(f"{RED}✗{RESET} settings.yaml not found")
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
            color = GREEN if result else RED
            symbol = "✓" if result else "✗"
            print(f"{color}{symbol}{RESET} {check_name}")
        
        return all(checks.values())
    
    except Exception as e:
        print(f"{RED}✗{RESET} Error loading config: {e}")
        return False


def validate_api_keys():
    """Check if API keys are configured."""
    print("Checking API keys...")
    
    # Check environment variable
    env_key = os.getenv('OPENAI_API_KEY')
    has_env_key = env_key is not None and len(env_key) > 0
    color = GREEN if has_env_key else YELLOW
    symbol = "✓" if has_env_key else "⊘"
    print(f"{color}{symbol}{RESET} OPENAI_API_KEY environment variable")
    
    # Check .env file
    env_file = Path('.env')
    has_env_file = env_file.exists()
    color = GREEN if has_env_file else YELLOW
    symbol = "✓" if has_env_file else "⊘"
    print(f"{color}{symbol}{RESET} .env file exists")
    
    # Check config file
    try:
        import yaml
        with open('src/config/settings.yaml') as f:
            config = yaml.safe_load(f)
        
        config_key = config.get('openai', {}).get('api_key', '')
        has_config_key = config_key is not None and len(config_key) > 0
        color = GREEN if has_config_key else YELLOW
        symbol = "✓" if has_config_key else "⊘"
        print(f"{color}{symbol}{RESET} API key in settings.yaml")
        
    except:
        has_config_key = False
        print(f"{YELLOW}⊘{RESET} Cannot read settings.yaml")
    
    has_key = has_env_key or has_config_key
    if not has_key:
        print(f"\n{YELLOW}Note: OpenAI API key not configured (required for OpenAI mode){RESET}")
    
    return has_key


def validate_ollama():
    """Check if Ollama is accessible."""
    print("Checking Ollama connection...")
    
    try:
        import requests
        response = requests.get('http://localhost:11434/api/version', timeout=2)
        if response.status_code == 200:
            print(f"{GREEN}✓{RESET} Ollama server is running")
            version = response.json().get('version', 'unknown')
            print(f"  Version: {version}")
            return True
        else:
            print(f"{RED}✗{RESET} Ollama responded with status {response.status_code}")
            return False
    except:
        print(f"{YELLOW}⊘{RESET} Ollama not running or not installed")
        print(f"  {YELLOW}Install from: https://ollama.ai{RESET}")
        print(f"  {YELLOW}Start with: ollama serve{RESET}")
        return False


def test_openai_route():
    """Test OpenAI route if API key is available."""
    print("Testing OpenAI route...")
    
    # Check if API key exists
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            import yaml
            with open('src/config/settings.yaml') as f:
                config = yaml.safe_load(f)
            api_key = config.get('openai', {}).get('api_key', '')
        except:
            pass
    
    if not api_key or len(api_key.strip()) == 0:
        print_status("SKIPPED", "OpenAI API key not found")
        return "SKIPPED"
    
    try:
        from routers.router_manager import load_config
        config = load_config()
        
        # Temporarily set to OpenAI to test
        original_model = config.get('active_model', 'openai')
        if original_model != 'openai':
            config['active_model'] = 'openai'
        
        # Test with a simple prompt
        test_prompt = "Say 'OK' if you can read this."
        from routers.openai_router import query_openai
        
        response = query_openai(test_prompt, config['openai'])
        
        if response and len(response.strip()) > 0:
            print_status("OK", f"OpenAI route working (response length: {len(response)} chars)")
            return "OK"
        else:
            print_status("FAILED", "OpenAI returned empty response")
            return "FAILED"
            
    except Exception as e:
        print_status("FAILED", f"OpenAI route error: {str(e)[:100]}")
        return "FAILED"


def test_ollama_route():
    """Test Ollama route if available."""
    print("Testing Ollama route...")
    
    # First check if Ollama is running
    try:
        import requests
        response = requests.get('http://localhost:11434/api/version', timeout=2)
        if response.status_code != 200:
            print_status("FAILED", "Ollama server not accessible")
            return "FAILED"
    except:
        print_status("FAILED", "Cannot connect to Ollama server")
        return "FAILED"
    
    try:
        from routers.router_manager import load_config
        config = load_config()
        
        # Check if model exists
        model_name = config.get('local', {}).get('model_name', 'llama2')
        
        # Test with a simple prompt
        test_prompt = "Say 'OK' if you can read this."
        from routers.local_router import query_ollama
        
        response = query_ollama(test_prompt, config['local'])
        
        if response and len(response.strip()) > 0:
            print_status("OK", f"Ollama route working with model '{model_name}' (response length: {len(response)} chars)")
            return "OK"
        else:
            print_status("FAILED", "Ollama returned empty response")
            return "FAILED"
            
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            model_name = config.get('local', {}).get('model_name', 'unknown')
            print_status("FAILED", f"Model '{model_name}' not found. Run: ollama pull {model_name}")
        else:
            print_status("FAILED", f"Ollama route error: {error_msg[:100]}")
        return "FAILED"


def test_import():
    """Try importing the main modules."""
    print("Testing module imports...")
    
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
            print(f"{GREEN}✓{RESET} {module}")
        except Exception as e:
            print(f"{RED}✗{RESET} {module}: {e}")
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
    
    print_section("6. Module Imports")
    results['imports'] = test_import()
    
    print_section("7. Ollama Connection")
    results['ollama_connection'] = validate_ollama()
    
    print_section("8. Route Testing")
    results['openai_route'] = test_openai_route()
    results['ollama_route'] = test_ollama_route()
    
    # Summary
    print_section("Validation Summary")
    
    critical_checks = ['python', 'deps', 'structure', 'config', 'imports']
    optional_checks = ['keys', 'ollama_connection']
    route_checks = ['openai_route', 'ollama_route']
    
    critical_pass = all(results[check] for check in critical_checks)
    
    # Print route summary
    print(f"\n{RESET}Route Status:")
    openai_status = results.get('openai_route', 'SKIPPED')
    ollama_status = results.get('ollama_route', 'FAILED')
    print_status(openai_status, f"OpenAI route: {openai_status}")
    print_status(ollama_status, f"Local route: {ollama_status}")
    
    if critical_pass:
        print(f"\n{GREEN}✓ All critical checks passed!{RESET}")
        print(f"\n{GREEN}Your GPT Wrapper is ready to use!{RESET}\n")
        
        print("Next steps:")
        if results.get('openai_route') != 'OK':
            print("  1. Configure OpenAI API key for OpenAI mode (if desired)")
        if results.get('ollama_route') != 'OK':
            print("  2. Install and start Ollama for local mode (if desired)")
        print("  3. Run: python src/main.py \"Your prompt here\"")
        print("  4. Try interactive mode: python src/main.py --interactive")
        print("  5. See QUICKSTART.md for detailed usage\n")
    else:
        print(f"\n{RED}✗ Some critical checks failed{RESET}")
        print("\nPlease fix the issues above before using GPT Wrapper.\n")
    
    # Optional warnings
    if not results.get('keys'):
        print(f"{YELLOW}⚠ OpenAI API key not configured (required for OpenAI mode){RESET}")
    
    if not results.get('ollama_connection'):
        print(f"{YELLOW}⚠ Ollama not available (required for local mode){RESET}")
    
    return 0 if critical_pass else 1


if __name__ == '__main__':
    sys.exit(main())
