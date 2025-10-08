#!/usr/bin/env python3
"""
Quick Setup Script for Cloud-Native IoT Security Framework
Automates environment setup and dependency installation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {message}")
    print("="*70 + "\n")


def run_command(command, description, check=True):
    """Run shell command with error handling"""
    print(f"→ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"  {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.11 or higher required")
        return False


def check_docker():
    """Check if Docker is installed"""
    print_header("Checking Docker Installation")
    
    if run_command("docker --version", "Checking Docker", check=False):
        if run_command("docker-compose --version", "Checking Docker Compose", check=False):
            print("✓ Docker and Docker Compose are installed")
            return True
    
    print("⚠ Docker not found. Docker deployment will not be available.")
    return False


def create_virtual_environment():
    """Create Python virtual environment"""
    print_header("Setting up Virtual Environment")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("Virtual environment already exists")
        return True
    
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    print("✓ Virtual environment created")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    # Determine pip path based on OS
    if platform.system() == "Windows":
        pip_path = "venv\\Scripts\\pip.exe"
        python_path = "venv\\Scripts\\python.exe"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip
    run_command(f"{python_path} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing Python packages"):
        return False
    
    print("✓ Dependencies installed successfully")
    return True


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        "data",
        "models",
        "results",
        "logs",
        "figures"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}/")
    
    return True


def run_smoke_test():
    """Run basic smoke test"""
    print_header("Running Smoke Test")
    
    # Determine python path
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python.exe"
    else:
        python_path = "venv/bin/python"
    
    test_code = """
import sys
sys.path.insert(0, 'src')

# Test imports
from iot_devices import SmartCamera, SmartPlug
from security import MicroSegmentationManager, ZeroTrustAuthenticator
from ai_detection import AnomalyDetector, ThreatClassifier

print('✓ All imports successful')

# Quick functionality test
camera = SmartCamera('test_camera')
telemetry = camera.generate_normal_telemetry()
print(f'✓ Device simulation works: {len(telemetry)} features')

detector = AnomalyDetector()
print('✓ AI models initialized')

print('\\n✓ Smoke test PASSED')
"""
    
    result = subprocess.run(
        [python_path, "-c", test_code],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print("✗ Smoke test failed")
        print(result.stderr)
        return False


def print_next_steps(has_docker):
    """Print next steps"""
    print_header("Setup Complete!")
    
    print("Next Steps:\n")
    
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"1. Activate virtual environment:")
    print(f"   {activate_cmd}\n")
    
    print("2. Run quick demo:")
    print("   python scripts/run_experiments.py --config config/experiment_config.yaml\n")
    
    print("3. View configuration:")
    print("   config/experiment_config.yaml\n")
    
    if has_docker:
        print("4. Deploy with Docker (optional):")
        print("   cd deployment")
        print("   docker-compose up -d\n")
    
    print("For more information, see README.md")
    print("\n" + "="*70 + "\n")


def main():
    """Main setup function"""
    print_header("Cloud-Native IoT Security Framework - Setup")
    print("This script will set up your development environment\n")
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Run setup steps
    if not check_python_version():
        sys.exit(1)
    
    has_docker = check_docker()
    
    if not create_virtual_environment():
        print("\n✗ Setup failed: Could not create virtual environment")
        sys.exit(1)
    
    if not install_dependencies():
        print("\n✗ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    if not create_directories():
        print("\n✗ Setup failed: Could not create directories")
        sys.exit(1)
    
    if not run_smoke_test():
        print("\n⚠ Setup completed with warnings: Smoke test failed")
        print("  You may need to install additional dependencies")
    
    print_next_steps(has_docker)


if __name__ == "__main__":
    main()
