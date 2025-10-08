# Quick Start Guide

## Installation (2 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run setup script
python setup.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir data models results logs figures
```

## Running Your First Experiment (1 minute)

```bash
# Run demo experiment
python scripts/run_experiments.py

# Expected output:
# - Training IoT detection models
# - Simulating 40 devices (cameras, plugs, thermostats, sensors)
# - Running 30 trials for statistical significance
# - Results: ~96% detection rate, ~4% false positives
```

## Quick Configuration

Edit `config/experiment_config.yaml`:

```yaml
# Reduce devices for faster testing
devices:
  smart_cameras: 5
  smart_plugs: 5
  thermostats: 5
  industrial_sensors: 5

# Shorter experiment duration
experiment:
  duration_minutes: 10
  n_trials: 3 # Reduce for quick test
```

## Docker Deployment (Production)

```bash
cd deployment
docker-compose up -d

# Access services:
# - Grafana: http://localhost:3000 (admin/admin)
# - Kibana: http://localhost:5601
# - Prometheus: http://localhost:9090
```

## Testing Individual Components

### Test IoT Device Simulation

```python
from src.iot_devices import SmartCamera

camera = SmartCamera("test_cam")
camera.connect_to_gateway()
camera.authenticate("mock://auth")

# Generate normal telemetry
normal_data = camera.generate_normal_telemetry()
print(f"Normal: {normal_data}")

# Simulate attack
attack_data = camera.generate_malicious_telemetry()
print(f"Attack: {attack_data}")
```

### Test Security Controls

```python
from src.security import MicroSegmentationManager, SecurityZone

# Create segmentation manager
segmentation = MicroSegmentationManager()

# Assign devices to zones
segmentation.assign_device_zone("camera_001", SecurityZone.IOT_TRUSTED)
segmentation.assign_device_zone("camera_002", SecurityZone.IOT_UNTRUSTED)

# Test lateral movement blocking
allowed = segmentation.evaluate_traffic(
    src_device="camera_001",
    dst_device="camera_002",
    protocol="tcp",
    port=22
)
print(f"Lateral movement allowed: {allowed}")  # Should be False
```

### Test AI Detection

```python
from src.ai_detection import AnomalyDetector
from src.iot_devices import SmartCamera

# Create detector
detector = AnomalyDetector()

# Generate training data
camera = SmartCamera("train_cam")
training_data = [camera.generate_normal_telemetry() for _ in range(100)]

# Train
detector.train(training_data)

# Test detection
normal = camera.generate_normal_telemetry()
attack = camera.generate_malicious_telemetry()

is_normal_anomaly, score1 = detector.predict(normal)
is_attack_anomaly, score2 = detector.predict(attack)

print(f"Normal classified as anomaly: {is_normal_anomaly} (score: {score1:.2f})")
print(f"Attack classified as anomaly: {is_attack_anomaly} (score: {score2:.2f})")
```

## Common Issues

### Import Errors

```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Verify Python path
python -c "import sys; print(sys.executable)"
```

### Missing Dependencies

```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Permission Errors (Docker)

```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Then log out and back in
```

## What's Next?

1. **Customize Configuration**: Edit `config/experiment_config.yaml` to match your needs
2. **Generate Datasets**: Use `scripts/generate_dataset.py` (coming soon)
3. **Run Full Experiments**: Execute all 30 trials with paper specifications
4. **Deploy to Cloud**: Use Terraform scripts in `deployment/terraform/` (coming soon)
5. **Analyze Results**: View generated figures in `figures/` directory

## Performance Benchmarks

Expected performance on typical hardware:

| Component                   | Time    | Memory |
| --------------------------- | ------- | ------ |
| Setup                       | 2-3 min | -      |
| Training (100 samples)      | 5 sec   | 200 MB |
| Inference (1000 samples)    | 1 sec   | 150 MB |
| Full Experiment (30 trials) | 45 min  | 500 MB |

## Support

- 📖 Full documentation: See README.md
- 🐛 Issues: Check experiment logs in `logs/`
- 📧 Questions: Refer to paper for implementation details

## Success Indicators

✓ All dependencies installed  
✓ Smoke test passes  
✓ Device simulation works  
✓ AI models train successfully  
✓ Security controls active  
✓ Experiments run to completion
