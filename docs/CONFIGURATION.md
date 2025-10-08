# Configuration Guide

This guide provides detailed information about configuring the Cloud-Native Security Framework for IoT Ecosystems. All configuration files are located in the `config/` directory and use YAML format.

## Table of Contents

- [Configuration Files Overview](#configuration-files-overview)
- [Experiment Configuration](#experiment-configuration)
- [Dataset Configuration](#dataset-configuration)
- [Security Configuration](#security-configuration)
- [Cloud Provider Configuration](#cloud-provider-configuration)
- [Logging and Monitoring Configuration](#logging-and-monitoring-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Environment Variables](#environment-variables)
- [Configuration Best Practices](#configuration-best-practices)
- [Configuration Examples](#configuration-examples)

---

## Configuration Files Overview

### Main Configuration Files

| File                     | Purpose                                                          | Location       |
| ------------------------ | ---------------------------------------------------------------- | -------------- |
| `experiment_config.yaml` | Main experiment parameters, security settings, attack simulation | `config/`      |
| `dataset_config.yaml`    | Dataset generation and augmentation settings                     | `config/`      |
| `logging_config.yaml`    | Logging levels, outputs, and formats                             | `config/`      |
| `cloud_config.yaml`      | Cloud provider settings (AWS, Azure, GCP)                        | `config/`      |
| `.env`                   | Environment variables and secrets                                | Root directory |
| `docker-compose.yaml`    | Docker container configuration                                   | Root directory |

### Configuration File Structure

```
config/
├── experiment_config.yaml      # Main experiment settings
├── dataset_config.yaml         # Dataset generation
├── logging_config.yaml         # Logging configuration
├── cloud_config.yaml           # Cloud provider settings
├── network_config.yaml         # Network topology
└── model_config.yaml           # AI model parameters
```

---

## Experiment Configuration

**File:** `config/experiment_config.yaml`

This is the primary configuration file for running security experiments.

### Random Seed

```yaml
# Random seed for reproducibility (as per research paper)
random_seed: 42
```

**Purpose:** Ensures reproducible results across multiple experiment runs.

### Device Configuration

```yaml
devices:
  smart_cameras: 10 # Number of smart camera devices
  smart_plugs: 10 # Number of smart plug devices
  thermostats: 10 # Number of thermostat devices
  industrial_sensors: 10 # Number of industrial sensor devices
  total_devices: 40 # Total device count (auto-calculated)
```

**Scaling Recommendations:**

- **Small-scale testing:** 10-50 devices
- **Medium-scale simulation:** 100-200 devices
- **Full-scale deployment:** 500+ devices (as reported in paper)

**Performance Impact:**

- Each device consumes ~10-20MB RAM
- Network bandwidth increases linearly with device count
- 500 devices require ~8-16GB RAM

### Network Configuration

```yaml
network:
  mqtt_broker: "localhost" # MQTT broker address
  mqtt_port: 1883 # MQTT port (1883 standard, 8883 for TLS)
  coap_port: 5683 # CoAP port (5683 standard, 5684 for DTLS)
  http_port: 8080 # HTTP REST API port
  websocket_port: 9001 # WebSocket port for real-time updates

  # Network topology
  topology: "star" # Options: star, mesh, hybrid

  # Quality of Service
  mqtt_qos: 1 # MQTT QoS level (0, 1, or 2)

  # Network constraints
  bandwidth_limit_mbps: 100 # Maximum bandwidth per device
  latency_ms: 50 # Simulated network latency
  packet_loss_rate: 0.01 # Packet loss rate (1%)
```

**Network Topology Options:**

- `star`: All devices connect to central broker (default)
- `mesh`: Direct device-to-device communication
- `hybrid`: Combination of star and mesh

### Security Configuration

```yaml
security:
  # Enable/disable security controls
  enable_micro_segmentation: true
  enable_zero_trust: true
  enable_ai_detection: true

  # Zero Trust parameters
  jwt_token_lifetime_minutes: 5 # Token expiration (paper uses 5 min)
  min_trust_score: 70.0 # Minimum trust score threshold

  # Mutual TLS
  mtls_enabled: true
  cert_renewal_days: 90

  # Micro-segmentation zones (10 zones as per paper)
  zones:
    - external # External internet-facing
    - dmz # Demilitarized zone
    - cloud_gateway # Cloud ingress/egress
    - iot_trusted # Verified IoT devices
    - iot_untrusted # New/unverified devices
    - iot_quarantine # Potentially compromised devices
    - management # Management interfaces
    - data_processing # Data analytics zone
    - ai_analytics # AI/ML processing zone
    - admin # Administrative access

  # Zone policies
  zone_policies:
    iot_trusted:
      allowed_outbound: ["cloud_gateway", "data_processing"]
      allowed_inbound: ["cloud_gateway"]
      isolation_level: "strict"

    iot_quarantine:
      allowed_outbound: [] # No outbound allowed
      allowed_inbound: ["management"]
      isolation_level: "complete"

  # Rate limiting
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    burst_size: 20
```

**Security Levels:**

- `strict`: Only explicitly allowed connections
- `moderate`: Allow common protocols, block suspicious
- `relaxed`: Allow most traffic, log anomalies
- `complete`: Total isolation (quarantine)

### AI Detection Configuration

```yaml
ai_detection:
  # Model selection
  models:
    anomaly_detection: "isolation_forest" # Options: isolation_forest, autoencoder, both
    classification: "random_forest" # Options: random_forest, cnn, ensemble

  # Isolation Forest parameters (Anomaly Detection)
  isolation_forest:
    n_estimators: 100 # Number of trees
    contamination: 0.1 # Expected proportion of anomalies (10%)
    max_samples: 256 # Samples to draw for each tree
    random_state: 42 # Random seed
    n_jobs: -1 # Use all CPU cores

  # Autoencoder parameters (Anomaly Detection)
  autoencoder:
    encoding_dim: 14 # Compressed representation size
    epochs: 100
    batch_size: 32
    learning_rate: 0.001
    reconstruction_threshold: 0.02

  # Random Forest parameters (Classification)
  random_forest:
    n_estimators: 200 # Number of trees (paper uses 200)
    max_depth: 20 # Maximum tree depth
    min_samples_split: 2 # Minimum samples to split
    min_samples_leaf: 1 # Minimum samples per leaf
    random_state: 42
    n_jobs: -1
    class_weight: "balanced" # Handle imbalanced classes

  # 1D CNN parameters (Classification)
  cnn_1d:
    filters: [64, 128, 256] # Conv layer filters
    kernel_size: 3 # Convolution kernel size
    pool_size: 2 # Max pooling size
    dense_units: [128, 64] # Dense layer sizes
    dropout_rate: 0.3 # Dropout for regularization
    epochs: 50
    batch_size: 64
    learning_rate: 0.0001

  # LSTM parameters (Sequence modeling)
  lstm:
    units: [128, 64] # LSTM layer units
    sequence_length: 10 # Time steps to look back
    dropout: 0.2
    recurrent_dropout: 0.2
    epochs: 50
    batch_size: 64

  # Feature extraction
  n_features: 47 # Total features (as per paper)

  # Feature categories
  features:
    network: # 15 network features
      - packet_size
      - bandwidth
      - latency
      - jitter
      - packet_loss
      - connection_count
      - protocol_distribution
      - port_diversity
      - dns_query_count
      - ssl_ratio
      - http_method_distribution
      - payload_entropy
      - inter_arrival_time
      - flow_duration
      - bytes_per_flow

    behavioral: # 20 behavioral features
      - request_rate
      - error_rate
      - auth_failures
      - api_usage_pattern
      - time_of_day_pattern
      - geolocation_changes
      - device_fingerprint_stability
      - firmware_version_changes
      - unusual_commands
      - data_volume_anomaly
      - connection_pattern_change
      - sleep_wake_pattern
      - sensor_reading_variance
      - actuator_usage_frequency
      - cloud_sync_frequency
      - peer_communication_count
      - protocol_violations
      - certificate_changes
      - privilege_escalation_attempts
      - configuration_changes

    device: # 12 device features
      - cpu_usage
      - memory_usage
      - storage_usage
      - temperature
      - battery_level
      - uptime
      - reboot_frequency
      - process_count
      - network_interface_count
      - running_services
      - installed_apps_count
      - device_type_encoding

  # Detection thresholds
  anomaly_threshold: 0.5 # Anomaly score threshold
  confidence_threshold: 0.7 # Classification confidence threshold
  ensemble_weight_anomaly: 0.4 # Weight for anomaly detection
  ensemble_weight_classification: 0.6 # Weight for classification

  # Model retraining
  retrain_interval_hours: 24 # Retrain every 24 hours
  min_new_samples: 1000 # Minimum samples to trigger retraining
  performance_threshold: 0.90 # Retrain if accuracy drops below 90%
```

**Model Selection Guide:**

- **Isolation Forest:** Fast, good for real-time detection, handles high-dimensional data
- **Autoencoder:** Better at detecting complex anomalies, requires more training
- **Random Forest:** Robust, interpretable, good for classification
- **CNN:** Excellent for pattern recognition, requires more data
- **LSTM:** Best for temporal patterns, higher computational cost

### Attack Simulation Configuration

```yaml
attack_simulation:
  # Attack probability (10% of traffic as per paper)
  attack_probability: 0.10

  # Attack type distribution (must sum to 1.0)
  attack_types:
    botnet_ddos: 0.15 # DDoS via botnet
    data_exfiltration: 0.15 # Unauthorized data export
    scanning: 0.15 # Port/network scanning
    credential_stuffing: 0.10 # Brute force login attempts
    command_injection: 0.10 # Command injection attacks
    ransomware: 0.10 # Ransomware simulation
    firmware_manipulation: 0.10 # Firmware tampering
    sensor_spoofing: 0.10 # False sensor data
    lateral_movement: 0.05 # Lateral movement attempts

  # Attack intensity levels
  intensity:
    low:
      traffic_multiplier: 2
      duration_minutes: 5
    medium:
      traffic_multiplier: 5
      duration_minutes: 15
    high:
      traffic_multiplier: 10
      duration_minutes: 30

  # Adversarial attack parameters
  adversarial:
    enable: true # Enable adversarial attacks

    # Evasion techniques
    evasion_techniques:
      - "slow_rate" # Slow-rate attacks to evade detection
      - "traffic_padding" # Add benign traffic to mask attacks
      - "timing_manipulation" # Manipulate timing patterns
      - "fragmentation" # Fragment attack payloads
      - "encryption" # Encrypt malicious traffic

    # Mimicry attacks
    mimicry_probability: 0.3 # 30% of attacks attempt mimicry
    mimicry_target_device: "thermostat" # Device to mimic

    # Attack sophistication
    sophistication_level: "medium" # Options: low, medium, high, apt

  # Attack scheduling
  schedule:
    random: true # Random attack timing
    peak_hours: [9, 17] # Peak attack hours (9 AM - 5 PM)
    off_hours_probability: 0.3 # Lower probability during off-hours
```

**Attack Intensity Recommendations:**

- **Development/Testing:** Use `low` intensity
- **Research Experiments:** Use `medium` intensity (paper default)
- **Stress Testing:** Use `high` intensity

### Experiment Parameters

```yaml
experiment:
  # Experiment metadata
  name: "cloud_iot_security_evaluation"
  description: "Evaluating integrated security framework"
  researcher: "Bharat Nagireddy"

  # Duration
  duration_minutes: 60 # Single trial duration
  warmup_minutes: 5 # Warmup period before data collection
  cooldown_minutes: 2 # Cooldown after experiment

  # Data collection
  telemetry_interval_seconds: 5 # Collect metrics every 5 seconds
  logging_level: "INFO" # DEBUG, INFO, WARNING, ERROR
  save_raw_data: true # Save raw telemetry data
  save_aggregated_data: true # Save aggregated statistics

  # Number of trials for statistical significance
  n_trials: 30 # Paper uses 30 trials

  # Train/validation/test split
  train_ratio: 0.6 # 60% training
  validation_ratio: 0.2 # 20% validation
  test_ratio: 0.2 # 20% testing

  # Cross-validation
  cross_validation:
    enabled: true
    n_folds: 5 # 5-fold cross-validation
    stratified: true # Preserve class distribution

  # Metrics to collect
  metrics:
    - detection_rate
    - false_positive_rate
    - false_negative_rate
    - precision
    - recall
    - f1_score
    - accuracy
    - auc_roc
    - detection_latency
    - containment_time
    - lateral_movement_reduction
    - auth_success_rate
    - cpu_utilization
    - memory_utilization
    - network_overhead

  # Reporting
  generate_plots: true
  plot_format: "png" # Options: png, pdf, svg
  generate_report: true
  report_format: "markdown" # Options: markdown, html, pdf

  # Output directories
  output:
    results_dir: "data/results"
    logs_dir: "data/logs"
    plots_dir: "data/plots"
    models_dir: "models/trained"
```

---

## Dataset Configuration

**File:** `config/dataset_config.yaml`

Configuration for generating synthetic IoT security datasets.

### Dataset Metadata

```yaml
dataset:
  name: "iot_security_dataset"
  version: "1.0"
  description: "Synthetic IoT security dataset with normal and attack traffic"
  output_dir: "./data/datasets"

  # Total samples
  total_samples: 100000 # 100K samples (paper uses 250K)

  # Class distribution (must sum to 1.0)
  class_distribution:
    normal: 0.70 # 70% normal traffic
    botnet_ddos: 0.05 # 5% DDoS attacks
    data_exfiltration: 0.05
    scanning: 0.05
    credential_stuffing: 0.03
    command_injection: 0.03
    ransomware: 0.03
    firmware_manipulation: 0.02
    sensor_spoofing: 0.02
    lateral_movement: 0.02
```

### Device Distribution

```yaml
device_distribution:
  smart_camera: 0.25 # 25% smart cameras
  smart_plug: 0.25 # 25% smart plugs
  thermostat: 0.25 # 25% thermostats
  industrial_sensor: 0.25 # 25% industrial sensors
```

### Data Augmentation

```yaml
augmentation:
  # SMOTE for minority classes
  enable_smote: true
  smote_k_neighbors: 5 # K-neighbors for SMOTE
  smote_target_ratio: 0.8 # Target ratio for minority classes

  # Gaussian noise injection
  enable_noise: true
  noise_level: 0.05 # 5% noise
  noise_type: "gaussian" # Options: gaussian, uniform, salt_pepper

  # Time-based augmentation
  enable_temporal: true
  time_shift_range: 300 # ±5 minutes
  time_scale_range: [0.9, 1.1] # ±10% time scaling

  # Feature augmentation
  enable_feature_augmentation: true
  feature_drop_probability: 0.1 # Randomly drop 10% of features
  feature_noise_std: 0.02 # Feature-specific noise
```

### Feature Generation

```yaml
features:
  # Network features (realistic ranges)
  network:
    bandwidth_range: [0.5, 30.0] # Mbps
    packet_size_range: [64, 4096] # bytes
    latency_range: [1, 500] # milliseconds
    jitter_range: [0, 100] # milliseconds
    packet_loss_range: [0.0, 0.1] # 0-10%
    connection_count_range: [1, 50] # concurrent connections

  # Device features
  device:
    cpu_range: [0, 100] # percent
    memory_range: [0, 512] # MB
    temperature_range: [20, 90] # Celsius
    battery_range: [0, 100] # percent
    uptime_range: [0, 8640000] # seconds (100 days max)

  # Security features
  security:
    auth_failure_range: [0, 50] # failed attempts
    port_scan_range: [0, 100] # scanned ports
    malformed_packet_range: [0, 20] # malformed packets
```

### Data Quality

```yaml
quality:
  # Missing values
  missing_value_ratio: 0.02 # 2% missing values
  missing_mechanism: "MCAR" # MCAR, MAR, or MNAR

  # Outliers
  outlier_ratio: 0.01 # 1% outliers
  outlier_method: "isolation_forest"

  # Label noise
  label_noise_ratio: 0.005 # 0.5% label noise

  # Data validation
  validate_ranges: true
  validate_distributions: true
  remove_duplicates: true
```

### Data Splits

```yaml
splits:
  train: 0.6 # 60% training
  validation: 0.2 # 20% validation
  test: 0.2 # 20% testing

  # Stratified split to preserve class distribution
  stratified: true
  random_state: 42
```

### Privacy-Preserving

```yaml
privacy:
  # Differential privacy
  enable_dp: true
  epsilon: 1.0 # Privacy budget
  delta: 0.00001 # Failure probability
  sensitivity: 1.0 # Query sensitivity

  # Anonymization
  anonymize_device_ids: true
  anonymize_ip_addresses: true
  anonymize_locations: true

  # K-anonymity
  k_anonymity: 5 # k=5 anonymity
```

### Export Formats

```yaml
export:
  formats:
    - csv # CSV format
    - parquet # Parquet (compressed)
    - hdf5 # HDF5 (large datasets)
    - tfrecord # TensorFlow format

  compression: "gzip" # Options: gzip, bz2, xz, none

  # Include metadata
  include_metadata: true
  metadata_format: "json"
```

---

## Security Configuration

### Micro-Segmentation Configuration

**File:** `config/security/micro_segmentation.yaml`

```yaml
micro_segmentation:
  # SDN Controller
  sdn_controller: "opendaylight" # Options: opendaylight, onos, ryu
  controller_url: "http://localhost:8181"
  controller_username: "admin"
  controller_password: "${SDN_PASSWORD}" # From environment variable

  # Zone Configuration
  zones:
    external:
      id: 1
      description: "External internet-facing zone"
      trust_level: 0
      isolation: "strict"
      allowed_protocols: ["HTTPS"]
      firewall_rules:
        - action: "deny"
          source: "*"
          destination: "internal"
          protocol: "*"

    iot_trusted:
      id: 4
      description: "Trusted IoT devices"
      trust_level: 70
      isolation: "moderate"
      allowed_protocols: ["MQTT", "CoAP", "HTTPS"]
      firewall_rules:
        - action: "allow"
          source: "iot_trusted"
          destination: "cloud_gateway"
          protocol: "MQTT"
        - action: "deny"
          source: "iot_trusted"
          destination: "iot_trusted"
          protocol: "*" # Prevent lateral movement

  # Dynamic zone assignment
  dynamic_assignment:
    enabled: true
    reassessment_interval_minutes: 15
    trust_score_threshold: 70

  # Traffic monitoring
  monitoring:
    log_all_traffic: true
    alert_on_violations: true
    blocked_traffic_retention_days: 30
```

### Zero Trust Configuration

**File:** `config/security/zero_trust.yaml`

```yaml
zero_trust:
  # Authentication
  authentication:
    method: "mutual_tls" # Options: mutual_tls, oauth2, api_key
    cert_authority: "internal_ca"
    cert_validity_days: 90
    cert_renewal_threshold_days: 30

    # JWT configuration
    jwt:
      algorithm: "RS256" # RSA with SHA-256
      token_lifetime_minutes: 5
      refresh_enabled: true
      refresh_lifetime_hours: 24
      issuer: "cloud-iot-security-framework"
      audience: "iot-devices"

  # Authorization
  authorization:
    policy_engine: "open_policy_agent" # OPA
    policy_server_url: "http://localhost:8181"

    # Role-based access control (RBAC)
    rbac:
      enabled: true
      roles:
        device_admin:
          permissions:
            - "device:read"
            - "device:write"
            - "device:delete"
        device_operator:
          permissions:
            - "device:read"
            - "device:execute"
        device_viewer:
          permissions:
            - "device:read"

  # Continuous verification
  continuous_verification:
    enabled: true
    verification_interval_minutes: 5
    trust_scoring:
      enabled: true
      factors:
        - device_health: 0.3
        - behavior_analysis: 0.3
        - location_consistency: 0.2
        - time_of_day: 0.1
        - firmware_integrity: 0.1

      thresholds:
        trusted: 80
        moderate: 50
        untrusted: 30

  # Least privilege
  least_privilege:
    enabled: true
    default_deny: true # Deny by default
    privilege_escalation_detection: true
```

---

## Cloud Provider Configuration

**File:** `config/cloud_config.yaml`

### AWS Configuration

```yaml
aws:
  # Credentials (use environment variables or IAM roles)
  region: "us-east-1"
  access_key_id: "${AWS_ACCESS_KEY_ID}"
  secret_access_key: "${AWS_SECRET_ACCESS_KEY}"

  # Services
  services:
    # IoT Core
    iot_core:
      enabled: true
      endpoint: "${AWS_IOT_ENDPOINT}"
      thing_group: "cloud-iot-devices"
      policy_name: "IoTDevicePolicy"

    # Lambda
    lambda:
      enabled: true
      runtime: "python3.11"
      timeout: 300
      memory_mb: 1024
      functions:
        - name: "ThreatDetection"
          handler: "lambda_function.lambda_handler"
          code_uri: "src/ai_detection/"

    # S3
    s3:
      enabled: true
      bucket_name: "cloud-iot-security-data"
      encryption: "AES256"
      versioning: true

    # CloudWatch
    cloudwatch:
      enabled: true
      log_group: "/aws/iot/security-framework"
      retention_days: 30
      metrics_namespace: "IoTSecurity"

    # DynamoDB
    dynamodb:
      enabled: true
      table_name: "IoTDeviceState"
      billing_mode: "PAY_PER_REQUEST"

    # VPC
    vpc:
      enabled: true
      cidr_block: "10.0.0.0/16"
      subnets:
        - "10.0.1.0/24" # Public subnet
        - "10.0.2.0/24" # Private subnet
```

### Azure Configuration

```yaml
azure:
  # Credentials
  subscription_id: "${AZURE_SUBSCRIPTION_ID}"
  tenant_id: "${AZURE_TENANT_ID}"
  client_id: "${AZURE_CLIENT_ID}"
  client_secret: "${AZURE_CLIENT_SECRET}"

  # Location
  location: "eastus"
  resource_group: "cloud-iot-security-rg"

  # Services
  services:
    # IoT Hub
    iot_hub:
      enabled: true
      name: "cloud-iot-security-hub"
      sku: "S1"
      partition_count: 4

    # Azure Functions
    functions:
      enabled: true
      app_name: "iot-security-functions"
      runtime: "python"
      runtime_version: "3.11"

    # Blob Storage
    storage:
      enabled: true
      account_name: "iotsecuritydata"
      container_name: "telemetry"
      replication: "LRS"

    # Cosmos DB
    cosmosdb:
      enabled: true
      account_name: "iot-security-db"
      database_name: "IoTSecurity"
      consistency_level: "Session"
```

### Google Cloud Platform Configuration

```yaml
gcp:
  # Credentials
  project_id: "${GCP_PROJECT_ID}"
  credentials_file: "${GOOGLE_APPLICATION_CREDENTIALS}"

  # Location
  region: "us-central1"
  zone: "us-central1-a"

  # Services
  services:
    # IoT Core
    iot_core:
      enabled: true
      registry_id: "cloud-iot-devices"
      pubsub_topic: "iot-telemetry"

    # Cloud Functions
    cloud_functions:
      enabled: true
      runtime: "python311"
      memory_mb: 256

    # Cloud Storage
    storage:
      enabled: true
      bucket_name: "cloud-iot-security-data"
      storage_class: "STANDARD"

    # BigQuery
    bigquery:
      enabled: true
      dataset_id: "iot_security"
      location: "US"
```

---

## Logging and Monitoring Configuration

**File:** `config/logging_config.yaml`

```yaml
logging:
  # Global logging level
  level: "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL

  # Log format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"

  # Outputs
  outputs:
    console:
      enabled: true
      level: "INFO"
      colorize: true

    file:
      enabled: true
      level: "DEBUG"
      path: "data/logs/framework.log"
      max_size_mb: 100
      backup_count: 5
      rotation: "size" # Options: size, time

    syslog:
      enabled: false
      level: "WARNING"
      host: "localhost"
      port: 514
      facility: "local0"

    elasticsearch:
      enabled: true
      level: "INFO"
      host: "localhost"
      port: 9200
      index: "iot-security-logs"

  # Component-specific logging
  components:
    iot_devices: "INFO"
    security: "DEBUG"
    ai_detection: "INFO"
    cloud_services: "WARNING"
    attack_simulation: "DEBUG"

  # Structured logging
  structured:
    enabled: true
    format: "json"
    include_fields:
      - timestamp
      - level
      - component
      - device_id
      - event_type
      - message

# Monitoring Configuration
monitoring:
  # Prometheus
  prometheus:
    enabled: true
    port: 9090
    scrape_interval: "15s"
    metrics:
      - cpu_usage
      - memory_usage
      - network_throughput
      - detection_rate
      - false_positive_rate
      - latency

  # Grafana
  grafana:
    enabled: true
    port: 3000
    dashboards:
      - "Security Overview"
      - "Device Health"
      - "Threat Detection"
      - "Performance Metrics"

  # Alerts
  alerts:
    enabled: true
    channels:
      - email
      - slack
      - webhook

    rules:
      - name: "High CPU Usage"
        condition: "cpu_usage > 80"
        severity: "warning"
        duration: "5m"

      - name: "Attack Detected"
        condition: "threat_score > 0.8"
        severity: "critical"
        duration: "1m"

      - name: "Device Offline"
        condition: "device_status == offline"
        severity: "warning"
        duration: "10m"
```

---

## Advanced Configuration

### Model Configuration

**File:** `config/model_config.yaml`

```yaml
models:
  # Model versioning
  versioning:
    enabled: true
    backend: "mlflow" # Options: mlflow, dvc, custom
    tracking_uri: "http://localhost:5000"

  # Model registry
  registry:
    enabled: true
    default_stage: "staging" # Options: staging, production, archived

  # Ensemble configuration
  ensemble:
    enabled: true
    voting: "soft" # Options: hard, soft
    weights:
      isolation_forest: 0.3
      random_forest: 0.4
      cnn_1d: 0.3

  # Model optimization
  optimization:
    quantization: false # Reduce model size
    pruning: false # Remove unnecessary weights
    knowledge_distillation: false

  # Explainability
  explainability:
    enabled: true
    methods:
      - "shap"
      - "lime"
    generate_reports: true
```

### Network Topology Configuration

**File:** `config/network_config.yaml`

```yaml
network_topology:
  # Topology type
  type: "hierarchical" # Options: flat, hierarchical, mesh

  # Network layers
  layers:
    edge:
      devices: ["smart_camera", "smart_plug", "thermostat"]
      gateway: "edge_gateway"

    fog:
      servers: 3
      processing: ["preprocessing", "local_analytics"]

    cloud:
      regions: ["us-east-1", "eu-west-1"]
      services: ["ai_detection", "data_storage"]

  # Bandwidth allocation
  bandwidth:
    edge_to_fog: "10Mbps"
    fog_to_cloud: "100Mbps"
    device_to_edge: "1Mbps"

  # Network simulation
  simulation:
    enabled: true
    latency_model: "uniform" # Options: uniform, normal, custom
    congestion_model: "token_bucket"
```

---

## Environment Variables

**File:** `.env`

```bash
# Application
APP_ENV=development  # development, staging, production
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=iot_security
DB_USER=postgres
DB_PASSWORD=your-db-password

# AWS
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_IOT_ENDPOINT=your-iot-endpoint.iot.us-east-1.amazonaws.com

# Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# GCP
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=iot_user
MQTT_PASSWORD=your-mqtt-password

# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

**Note:** Never commit the `.env` file to version control. Use `.env.example` as a template.

---

## Configuration Best Practices

### 1. Security

✅ **DO:**

- Use environment variables for sensitive data
- Encrypt configuration files containing secrets
- Rotate secrets regularly
- Use separate configurations for dev/staging/prod
- Enable audit logging for configuration changes

❌ **DON'T:**

- Hardcode credentials in configuration files
- Commit `.env` files to version control
- Share production credentials
- Use default passwords

### 2. Performance

✅ **DO:**

- Start with conservative resource limits
- Profile and adjust based on metrics
- Use connection pooling
- Enable caching where appropriate
- Monitor resource utilization

❌ **DON'T:**

- Over-allocate resources unnecessarily
- Disable rate limiting in production
- Ignore memory leaks
- Skip performance testing

### 3. Reproducibility

✅ **DO:**

- Set random seeds for experiments
- Version control configuration files
- Document configuration changes
- Use configuration validation
- Maintain configuration backups

❌ **DON'T:**

- Modify configurations without tracking
- Use different configs across trials
- Skip configuration validation
- Forget to document custom settings

### 4. Maintainability

✅ **DO:**

- Use descriptive configuration names
- Add comments to complex settings
- Group related configurations
- Use configuration inheritance
- Validate configurations on startup

❌ **DON'T:**

- Create overly complex configurations
- Duplicate configuration values
- Use cryptic abbreviations
- Skip configuration documentation

---

## Configuration Examples

### Example 1: Development Environment

```yaml
# config/experiment_config.yaml (Development)
random_seed: 42

devices:
  smart_cameras: 5
  smart_plugs: 5
  thermostats: 5
  industrial_sensors: 5
  total_devices: 20 # Small scale for testing

security:
  enable_micro_segmentation: true
  enable_zero_trust: true
  enable_ai_detection: true

ai_detection:
  isolation_forest:
    n_estimators: 50 # Reduced for faster training

attack_simulation:
  attack_probability: 0.05 # Lower for testing

experiment:
  duration_minutes: 10 # Short duration
  n_trials: 3 # Fewer trials
  logging_level: "DEBUG"
```

### Example 2: Production Environment

```yaml
# config/experiment_config.yaml (Production)
random_seed: 42

devices:
  smart_cameras: 125
  smart_plugs: 125
  thermostats: 125
  industrial_sensors: 125
  total_devices: 500 # Full scale

security:
  enable_micro_segmentation: true
  enable_zero_trust: true
  enable_ai_detection: true

ai_detection:
  isolation_forest:
    n_estimators: 100
    n_jobs: -1 # Use all cores

attack_simulation:
  attack_probability: 0.10

experiment:
  duration_minutes: 1440 # 24 hours
  n_trials: 30
  logging_level: "INFO"
```

### Example 3: Stress Testing

```yaml
# config/experiment_config.yaml (Stress Test)
devices:
  total_devices: 1000 # High device count

attack_simulation:
  attack_probability: 0.30 # High attack rate
  intensity: high

network:
  bandwidth_limit_mbps: 10 # Constrained bandwidth
  latency_ms: 200 # High latency
  packet_loss_rate: 0.05 # 5% packet loss
```

---

## Configuration Validation

To validate your configuration:

```bash
# Validate configuration files
python scripts/validate_config.py

# Validate specific file
python scripts/validate_config.py --file config/experiment_config.yaml

# Show configuration summary
python scripts/show_config.py --verbose
```

---

## Troubleshooting Configuration Issues

### Issue: Configuration file not found

**Error:** `FileNotFoundError: config/experiment_config.yaml not found`

**Solution:**

```bash
# Copy example configuration
cp config/experiment_config.yaml.example config/experiment_config.yaml
```

### Issue: Invalid YAML syntax

**Error:** `yaml.scanner.ScannerError: while scanning`

**Solution:**

- Check for proper indentation (use spaces, not tabs)
- Validate YAML syntax: https://www.yamllint.com/
- Use a YAML validator: `python scripts/validate_yaml.py config/`

### Issue: Environment variable not set

**Error:** `KeyError: 'AWS_ACCESS_KEY_ID'`

**Solution:**

```bash
# Set environment variable
export AWS_ACCESS_KEY_ID=your-key

# Or create .env file
echo "AWS_ACCESS_KEY_ID=your-key" >> .env
```

### Issue: Configuration value out of range

**Error:** `ValueError: attack_probability must be between 0 and 1`

**Solution:**

- Review valid ranges in this documentation
- Run configuration validation: `python scripts/validate_config.py`

---

## Additional Resources

- **Configuration Templates:** See `config/*.yaml.example` files
- **Schema Definitions:** See `config/schemas/` for JSON schemas
- **Migration Guide:** See `docs/CONFIG_MIGRATION.md` for version upgrades
- **API Documentation:** See `docs/API.md` for programmatic configuration

---
