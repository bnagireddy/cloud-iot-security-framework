# Cloud-Native Security Framework for IoT Ecosystems

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11.4-blue.svg)
![Status](https://img.shields.io/badge/status-research-orange.svg)

A comprehensive security framework integrating micro-segmentation, zero trust architecture, and AI-based threat detection for cloud-IoT environments.

## 🎯 Overview

This framework addresses critical security challenges in cloud-IoT ecosystems through:

- **Micro-segmentation**: Network isolation to limit lateral movement (85.3% reduction)
- **Zero Trust Architecture**: Continuous authentication and authorization (99.3% success rate)
- **AI-based Threat Detection**: Real-time anomaly detection (96.4% detection rate, 4.2% false positives)

## 📊 Key Results

- **Threat Detection**: 96.4% (±1.5%) with only 4.2% (±1.2%) false positives
- **Lateral Movement Prevention**: 85.3% (±2.7%) reduction
- **Authentication Success**: 99.3% (±0.6%)
- **Detection Latency**: 120ms (±15ms)
- **Containment Time**: 183s (±27s)
- **Performance Overhead**: 4.7ms latency, 8% CPU utilization

## 🏗️ Architecture

```
cloud-iot-security-framework/
├── src/
│   ├── iot_devices/          # IoT device simulators
│   ├── cloud_services/       # Cloud service components
│   ├── security/             # Security controls (micro-seg, zero trust)
│   └── ai_detection/         # AI/ML threat detection models
├── config/                   # Configuration files
├── deployment/               # Docker, Terraform, Ansible scripts
├── scripts/                  # Utility and experiment scripts
├── tests/                    # Unit and integration tests
├── data/                     # Datasets and logs
└── models/                   # Pre-trained AI models
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11.4+
- Docker 24.0.5+
- AWS CLI (for cloud deployment)
- 8GB+ RAM

### Installation

```bash
# Clone repository
git clone https://github.com/bnagireddy/cloud-iot-security-framework.git
cd cloud-iot-security-framework

# Create virtual environment
python -m venv venv
# Linux/Mac: source venv/bin/activate
# Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Linux/Mac: cp config/experiment_config.yaml.example config/experiment_config.yaml
# Windows: copy config\experiment_config.yaml.example config\experiment_config.yaml
# Edit config/experiment_config.yaml with your settings
```

### Running the Framework

```bash
# 1. Start IoT device simulation (500 devices)
python scripts/start_iot_simulation.py --devices 500

# 2. Start cloud services
python scripts/start_cloud_services.py

# 3. Enable security controls
python scripts/enable_security.py --micro-seg --zero-trust --ai-detection

# 4. Run experiments
python scripts/run_experiments.py --trials 30 --duration 24h

# 5. Analyze results
python scripts/analyze_results.py --output results/
```

### Docker Deployment

```bash
# Build containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 Features

### IoT Device Simulation

- **Device Types**: Smart cameras, smart plugs, thermostats, industrial sensors
- **Protocols**: MQTT, CoAP, HTTP/HTTPS
- **Behaviors**: Normal operation, attack simulation
- **Scale**: 100-500 devices per deployment

### Security Controls

#### Micro-Segmentation

- 10 security zones based on device type and sensitivity
- Automated policy enforcement
- Network isolation and traffic filtering
- SDN-based implementation (OpenDaylight)

#### Zero Trust Architecture

- Continuous authentication (every 5 minutes)
- Mutual TLS (mTLS) for all connections
- JWT-based authorization
- Policy engine (Open Policy Agent)

#### AI Threat Detection

- **Anomaly Detection**: Isolation Forest + Autoencoder
- **Classification**: Random Forest + 1D CNN
- **Features**: 47 traffic/behavioral features
- **Training**: 250,000 samples (150k benign, 100k attacks)

### Attack Simulation

- DDoS attacks
- Port scanning
- Malware infection
- Unauthorized access
- Data exfiltration
- Lateral movement
- API abuse
- Reconnaissance

## 📊 Experiments

### Baseline Comparisons

The framework is evaluated against three baselines:

1. **Perimeter Security**: Traditional firewall + Snort IDS
2. **Zero Trust without AI**: ZT + micro-seg without ML
3. **AI with Traditional Segmentation**: ML with VLAN-based segmentation

### Metrics Collected

- Threat detection rate
- False positive rate
- Lateral movement prevention
- Mean time to detect (MTTD)
- Mean time to contain (MTTC)
- Network latency
- CPU/memory utilization
- Scalability (devices, attacks/sec)

## 🔬 Reproducibility

All experiments are fully reproducible:

### Environment Setup

```bash
# Install exact versions
pip install -r requirements-exact.txt

# Verify environment
python tests/smoke_test.py
```

### Dataset Generation

```bash
# Generate synthetic IoT traffic dataset
python scripts/generate_dataset.py --config config/dataset_config.yaml --seed 42 --output data/
```

### Run Experiments

```bash
# Run full experimental suite (n=30 trials)
python scripts/run_baseline_experiments.py --trials 30
python scripts/run_framework_experiments.py --trials 30

# Generate results
python scripts/analyze_results.py --baseline results/baseline/ --framework results/proposed/ --output results/comparison/
```

## 📈 Results Visualization

```bash
# Generate all figures and tables from paper
python scripts/generate_figures.py --output figures/

# Creates:
# - figures/security_comparison.png
# - figures/performance_overhead.png
# - figures/scalability_analysis.png
# - figures/attack_detection_rates.png
```

## 🔒 Security & Privacy

### Data Privacy

- Edge processing priority
- Data anonymization (HMAC-SHA256 pseudonyms)
- Differential privacy (ε=1.0, Laplace mechanism)
- 30-day retention for raw telemetry

### Compliance

- **GDPR**: Data minimization, right to erasure, DPIA template
- **HIPAA**: BAA support, encryption at rest/transit
- **NIST CSF**: Mapped controls
- **ISO 27001**: Alignment with ISMS requirements

### Ethical AI

- Bias mitigation (fairness metrics, diverse training data)
- Explainability (SHAP, LIME)
- Model governance and versioning

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run security tests
pytest tests/security/

# Generate coverage report
pytest --cov=src --cov-report=html
```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/
mypy src/
```

## 📄 Citation

If you use this framework in your research, please cite:

```bibtex
@article{nagireddy2025cloudiot,
  title={Cloud-Native Security Framework for IoT Ecosystems: Integrating Micro-Segmentation, Zero Trust, and AI-Based Threat Detection},
  author={Nagireddy, Bharath Reddy},
  journal={CSSS 6000 Practical Research in Cybersecurity},
  year={2025},
  institution={Webster University}
}
```

## 📞 Contact

- **Author**: Bharath Reddy Nagireddy
- **Institution**: Webster University
- **Email**: bnagireddy@webster.edu
- **GitHub**: [github.com/bnagireddy/cloud-iot-security-framework](https://github.com/bnagireddy/cloud-iot-security-framework)

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Webster University CSSS 6000 program
- Professor Jason Ham
- Open source community (TensorFlow, scikit-learn, OpenDaylight, OPA)

## 🗺️ Roadmap

- [ ] Multi-cloud support (Azure, GCP)
- [ ] Extended device types (healthcare, automotive)
- [ ] Real-world pilot deployment
- [ ] Enhanced explainability dashboard
- [ ] Automated remediation playbooks
- [ ] Federated learning implementation
- [ ] Post-quantum cryptography integration

## 📊 Performance Benchmarks

| Metric                          | Baseline 1 | Baseline 2 | Baseline 3 | **Proposed**     |
| ------------------------------- | ---------- | ---------- | ---------- | ---------------- |
| Detection Rate (%)              | 67.3 ± 3.2 | 78.5 ± 2.8 | 88.2 ± 2.1 | **96.4 ± 1.5\*** |
| False Positive (%)              | 18.7 ± 4.1 | 12.3 ± 2.9 | 8.1 ± 1.8  | **4.2 ± 1.2\***  |
| Lateral Movement Prevention (%) | 22.1 ± 5.3 | 71.4 ± 4.2 | 68.9 ± 3.8 | **85.3 ± 2.7\*** |
| MTTD (seconds)                  | 342 ± 45   | 187 ± 28   | 142 ± 21   | **120 ± 15\***   |
| MTTC (seconds)                  | 876 ± 112  | 245 ± 38   | 298 ± 42   | **183 ± 27\***   |

\*p < 0.001 vs. all baselines (paired t-test, n=30)
