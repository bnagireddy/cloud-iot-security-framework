# Installation Guide

This guide provides detailed installation instructions for the Cloud-Native Security Framework for IoT Ecosystems.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Method 1: Local Installation (Recommended for Development)](#method-1-local-installation-recommended-for-development)
  - [Method 2: Docker Installation (Recommended for Production)](#method-2-docker-installation-recommended-for-production)
  - [Method 3: Cloud Deployment](#method-3-cloud-deployment)
- [Post-Installation Configuration](#post-installation-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11
- **Python**: 3.11.4 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space
- **Network**: Stable internet connection for cloud services

### Software Dependencies

- **Docker**: 24.0.5+ (for containerized deployment)
- **Docker Compose**: 2.20.0+
- **Git**: 2.30.0+
- **AWS CLI**: 2.x (optional, for AWS deployment)
- **Azure CLI**: 2.x (optional, for Azure deployment)
- **Google Cloud SDK**: (optional, for GCP deployment)

### Hardware Recommendations

- **CPU**: 4+ cores (8+ recommended for full simulation)
- **GPU**: Optional, but recommended for AI model training
- **Network**: 100 Mbps+ for cloud integration

---

## Installation Methods

### Method 1: Local Installation (Recommended for Development)

#### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/bnagireddy/cloud-iot-security-framework.git
cd cloud-iot-security-framework
```

#### Step 2: Set Up Python Virtual Environment

**Linux/macOS:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you encounter execution policy errors, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (Command Prompt):**

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 4: Configure Environment Variables

**Linux/macOS:**

```bash
# Copy example environment file
cp config/experiment_config.yaml.example config/experiment_config.yaml

# Edit configuration (use your preferred editor)
nano config/experiment_config.yaml
```

**Windows:**

```powershell
# Copy example environment file
copy config\experiment_config.yaml.example config\experiment_config.yaml

# Edit configuration (use your preferred editor)
notepad config\experiment_config.yaml
```

#### Step 5: Initialize Data Directories

```bash
# Create necessary directories
mkdir -p data/logs
mkdir -p data/datasets
mkdir -p data/results
mkdir -p models/pretrained
```

**Windows (PowerShell):**

```powershell
# Create necessary directories
New-Item -ItemType Directory -Force -Path data\logs
New-Item -ItemType Directory -Force -Path data\datasets
New-Item -ItemType Directory -Force -Path data\results
New-Item -ItemType Directory -Force -Path models\pretrained
```

#### Step 6: Run Setup Script

```bash
# Run automated setup
python setup.py
```

This script will:

- Verify Python version
- Check all dependencies
- Create required directories
- Download pre-trained models (if available)
- Validate configuration files

---

### Method 2: Docker Installation (Recommended for Production)

#### Step 1: Install Docker

**Linux (Ubuntu/Debian):**

```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**

- Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- Start Docker Desktop from Applications

**Windows:**

- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Ensure WSL 2 is enabled
- Start Docker Desktop

#### Step 2: Clone Repository

```bash
git clone https://github.com/bnagireddy/cloud-iot-security-framework.git
cd cloud-iot-security-framework
```

#### Step 3: Configure Docker Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # Linux/macOS
notepad .env  # Windows
```

#### Step 4: Build Docker Images

```bash
# Build all containers
docker-compose build

# This will build:
# - IoT device simulator containers
# - Cloud service containers
# - Security control containers
# - AI detection service containers
```

#### Step 5: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

#### Step 6: Initialize Database and Services

```bash
# Run initialization script inside container
docker-compose exec security-framework python scripts/initialize.py
```

---

### Method 3: Cloud Deployment

#### AWS Deployment

**Prerequisites:**

- AWS account with appropriate permissions
- AWS CLI configured with credentials

**Step 1: Configure AWS CLI**

```bash
# Configure AWS credentials
aws configure

# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

**Step 2: Deploy Infrastructure with Terraform**

```bash
cd deployment/terraform/aws

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan

# Deploy infrastructure
terraform apply

# Note: This will create:
# - EC2 instances for IoT simulation
# - Lambda functions for security controls
# - S3 buckets for data storage
# - CloudWatch for monitoring
```

**Step 3: Deploy Application**

```bash
# Use provided deployment script
cd ../../..
bash deployment/scripts/deploy_aws.sh

# Or use Ansible
cd deployment/ansible
ansible-playbook -i inventory/aws.ini deploy_aws.yml
```

#### Azure Deployment

**Prerequisites:**

- Azure account with subscription
- Azure CLI installed

```bash
# Login to Azure
az login

# Create resource group
az group create --name cloud-iot-security --location eastus

# Deploy using ARM template
cd deployment/azure
az deployment group create \
  --resource-group cloud-iot-security \
  --template-file deployment_template.json \
  --parameters @parameters.json
```

#### Google Cloud Platform (GCP) Deployment

**Prerequisites:**

- GCP account with project
- Google Cloud SDK installed

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy using deployment manager
cd deployment/gcp
gcloud deployment-manager deployments create iot-security \
  --config deployment.yaml
```

---

## Post-Installation Configuration

### 1. Configure Experiment Parameters

Edit `config/experiment_config.yaml`:

```yaml
simulation:
  num_devices: 500
  duration_hours: 24
  attack_scenarios:
    - DDoS
    - Man-in-the-Middle
    - Device Compromise

security:
  micro_segmentation:
    enabled: true
    isolation_level: strict

  zero_trust:
    enabled: true
    auth_interval_minutes: 5

  ai_detection:
    enabled: true
    model_path: models/pretrained/lstm_threat_detector.h5
    threshold: 0.85

cloud:
  provider: aws # aws, azure, or gcp
  region: us-east-1
```

### 2. Set Up Logging

Edit `config/logging_config.yaml`:

```yaml
logging:
  level: INFO
  outputs:
    - console
    - file
    - elasticsearch

  file:
    path: data/logs/framework.log
    max_size_mb: 100
    backup_count: 5
```

### 3. Configure Cloud Credentials

**AWS:**

```bash
# Create .aws/credentials file
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
EOF
```

**Azure:**

```bash
# Login and set subscription
az login
az account set --subscription YOUR_SUBSCRIPTION_ID
```

**GCP:**

```bash
# Set up service account
gcloud auth application-default login
```

---

## Verification

### 1. Verify Python Installation

```bash
# Check Python version
python --version
# Expected: Python 3.11.4 or higher

# Verify installed packages
pip list | grep -E "tensorflow|scikit-learn|paho-mqtt"
```

**Windows:**

```powershell
python --version
pip list | Select-String -Pattern "tensorflow|scikit-learn|paho-mqtt"
```

### 2. Run Health Check

```bash
# Run health check script
python scripts/health_check.py

# Expected output:
# ✓ Python version: OK
# ✓ Dependencies: OK
# ✓ Configuration files: OK
# ✓ Data directories: OK
# ✓ Cloud connectivity: OK
# ✓ AI models: OK
```

### 3. Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Expected: All tests pass (90%+ coverage)
```

### 4. Test Individual Components

```bash
# Test IoT device simulator
python -m src.iot_devices.device_simulator --test

# Test security controls
python -m src.security.micro_segmentation --test

# Test AI detection
python -m src.ai_detection.threat_detector --test
```

### 5. Verify Docker Installation (if using Docker)

```bash
# Check running containers
docker-compose ps

# Expected output: All services in "Up" state

# Check logs for errors
docker-compose logs | grep -i error
```

---

## Troubleshooting

### Common Issues

#### 1. Python Version Issues

**Problem:** `Python version 3.11.4 or higher required`

**Solution:**

```bash
# Install Python 3.11+ using pyenv (Linux/macOS)
curl https://pyenv.run | bash
pyenv install 3.11.4
pyenv global 3.11.4

# Or download from python.org for Windows
```

#### 2. Dependency Installation Failures

**Problem:** `ERROR: Could not install packages due to an EnvironmentError`

**Solution:**

```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# If specific package fails (e.g., tensorflow)
pip install tensorflow==2.13.0 --no-cache-dir
```

#### 3. TensorFlow Installation Issues

**Problem:** TensorFlow fails to install or import

**Solution (CPU-only):**

```bash
# Install CPU version
pip install tensorflow-cpu==2.13.0
```

**Solution (GPU):**

```bash
# Ensure CUDA and cuDNN are installed
# Then install GPU version
pip install tensorflow==2.13.0
```

#### 4. Docker Permission Issues (Linux)

**Problem:** `permission denied while trying to connect to Docker daemon`

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart docker service
sudo systemctl restart docker

# Re-login or run
newgrp docker
```

#### 5. Port Conflicts

**Problem:** `Error: Port 8080 is already in use`

**Solution:**

```bash
# Find process using port
# Linux/macOS:
lsof -i :8080

# Windows:
netstat -ano | findstr :8080

# Kill process or change port in config/experiment_config.yaml
```

#### 6. AWS Credentials Issues

**Problem:** `Unable to locate credentials`

**Solution:**

```bash
# Reconfigure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Windows:**

```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

#### 7. Memory Issues

**Problem:** `MemoryError` or system slowdown during simulation

**Solution:**

```yaml
# Reduce simulation scale in config/experiment_config.yaml
simulation:
  num_devices: 100 # Reduce from 500
  batch_size: 10 # Reduce batch processing
```

#### 8. Module Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**

```bash
# Add project root to PYTHONPATH
# Linux/macOS:
export PYTHONPATH="${PYTHONPATH}:/path/to/cloud-iot-security-framework"

# Windows:
$env:PYTHONPATH="C:\path\to\cloud-iot-security-framework"

# Or install in development mode
pip install -e .
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**

   ```bash
   cat data/logs/framework.log
   # Windows: type data\logs\framework.log
   ```

2. **Enable debug mode:**

   ```yaml
   # In config/logging_config.yaml
   logging:
     level: DEBUG
   ```

3. **Run diagnostics:**

   ```bash
   python scripts/diagnose.py --verbose
   ```

4. **Check documentation:**

   - See [README.md](../README.md) for overview
   - See [QUICKSTART.md](QUICKSTART.md) for basic usage
   - See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup

5. **Community support:**
   - Open an issue on GitHub
   - Check existing issues for solutions
   - Contact the maintainers

---

## Next Steps

After successful installation:

1. **Quick Start:** Follow the [QUICKSTART.md](QUICKSTART.md) guide for basic usage
2. **Configuration:** Review [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for detailed configuration options
3. **Experiments:** See [EXPERIMENTS.md](EXPERIMENTS.md) for running security experiments
4. **Development:** Read [CONTRIBUTING.md](../CONTRIBUTING.md) if you plan to contribute

---

## Additional Resources

- **Documentation:** [docs/](.)
- **API Reference:** [API.md](API.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Performance Tuning:** [PERFORMANCE.md](PERFORMANCE.md)
- **Security Best Practices:** [SECURITY.md](SECURITY.md)

---

**Last Updated:** October 8, 2025  
**Version:** 1.0.0  
**Maintainer:** Bharat Nagireddy
