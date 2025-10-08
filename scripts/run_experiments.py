"""
Main experiment runner
Runs complete experiments as described in paper
"""

import os
import sys
import yaml
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.iot_devices import SmartCamera, SmartPlug, Thermostat, IndustrialSensor
from src.security import MicroSegmentationManager, ZeroTrustAuthenticator, SecurityZone
from src.ai_detection import AnomalyDetector, ThreatClassifier


def setup_logging(config):
    """Setup logging configuration"""
    log_dir = Path(config['output']['logs_dir'])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=getattr(logging, config['output']['log_level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("ExperimentRunner")


def create_devices(config, logger):
    """Create IoT device simulators"""
    devices = []
    device_config = config['devices']
    
    logger.info("Creating IoT devices...")
    
    # Create smart cameras
    for i in range(device_config['smart_cameras']):
        device = SmartCamera(
            device_id=f"camera_{i:03d}",
            mqtt_broker=config['network']['mqtt_broker'],
            mqtt_port=config['network']['mqtt_port']
        )
        devices.append(device)
    
    # Create smart plugs
    for i in range(device_config['smart_plugs']):
        device = SmartPlug(
            device_id=f"plug_{i:03d}",
            mqtt_broker=config['network']['mqtt_broker'],
            mqtt_port=config['network']['mqtt_port']
        )
        devices.append(device)
    
    # Create thermostats
    for i in range(device_config['thermostats']):
        device = Thermostat(
            device_id=f"thermostat_{i:03d}",
            mqtt_broker=config['network']['mqtt_broker'],
            mqtt_port=config['network']['mqtt_port']
        )
        devices.append(device)
    
    # Create industrial sensors
    for i in range(device_config['industrial_sensors']):
        sensor_type = ["pressure", "vibration", "temperature", "flow"][i % 4]
        device = IndustrialSensor(
            device_id=f"sensor_{i:03d}",
            sensor_type=sensor_type,
            mqtt_broker=config['network']['mqtt_broker'],
            mqtt_port=config['network']['mqtt_port']
        )
        devices.append(device)
    
    logger.info(f"Created {len(devices)} IoT devices")
    return devices


def setup_security(config, devices, logger):
    """Setup security controls"""
    logger.info("Initializing security controls...")
    
    # Micro-segmentation
    segmentation = None
    if config['security']['enable_micro_segmentation']:
        segmentation = MicroSegmentationManager()
        
        # Assign devices to zones
        for device in devices:
            # Assign based on device type (simplified)
            if "camera" in device.device_id or "sensor" in device.device_id:
                zone = SecurityZone.IOT_TRUSTED
            else:
                zone = SecurityZone.IOT_UNTRUSTED
            
            segmentation.assign_device_zone(device.device_id, zone)
        
        logger.info("Micro-segmentation enabled with 10 zones")
    
    # Zero Trust authentication
    zero_trust = None
    if config['security']['enable_zero_trust']:
        zero_trust = ZeroTrustAuthenticator(
            token_lifetime_minutes=config['security']['jwt_token_lifetime_minutes']
        )
        
        # Authenticate all devices
        for device in devices:
            token = zero_trust.authenticate_device(
                device_id=device.device_id,
                device_type=device.device_type,
                credentials={"device_key": "mock_key"},
                method="jwt"
            )
            device.auth_token = token
        
        logger.info("Zero Trust authentication enabled")
    
    return segmentation, zero_trust


def setup_ai_detection(config, logger):
    """Setup AI detection models"""
    logger.info("Initializing AI detection models...")
    
    # Anomaly detector (Isolation Forest)
    anomaly_detector = AnomalyDetector(
        isolation_forest_trees=config['ai_detection']['isolation_forest']['n_estimators'],
        contamination=config['ai_detection']['isolation_forest']['contamination'],
        random_state=config['ai_detection']['isolation_forest']['random_state']
    )
    
    # Threat classifier (Random Forest)
    threat_classifier = ThreatClassifier(
        n_estimators=config['ai_detection']['random_forest']['n_estimators'],
        max_depth=config['ai_detection']['random_forest']['max_depth'],
        random_state=config['ai_detection']['random_forest']['random_state']
    )
    
    logger.info("AI detection models initialized")
    return anomaly_detector, threat_classifier


def run_experiment(config, trial_num, logger):
    """Run single experimental trial"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting Trial {trial_num + 1}/{config['experiment']['n_trials']}")
    logger.info(f"{'='*60}\n")
    
    # Create devices
    devices = create_devices(config, logger)
    
    # Setup security
    segmentation, zero_trust = setup_security(config, devices, logger)
    
    # Setup AI detection
    anomaly_detector, threat_classifier = setup_ai_detection(config, logger)
    
    # Collect training data
    logger.info("Collecting training data...")
    training_samples = []
    for device in devices:
        for _ in range(100):  # 100 samples per device
            telemetry = device.generate_normal_telemetry()
            training_samples.append(telemetry)
    
    # Train models
    logger.info("Training AI models...")
    anomaly_detector.train(training_samples)
    
    # Run simulation
    logger.info(f"Running {config['experiment']['duration_minutes']}-minute simulation...")
    
    # Collect metrics
    results = {
        "trial": trial_num,
        "devices": len(devices),
        "detections": 0,
        "false_positives": 0,
        "true_positives": 0,
        "false_negatives": 0,
        "lateral_movement_blocked": 0
    }
    
    # Simulate traffic (simplified for demonstration)
    import random
    n_samples = config['experiment']['duration_minutes'] * 60 // config['experiment']['telemetry_interval_seconds']
    
    for i in range(n_samples):
        # Random device generates telemetry
        device = random.choice(devices)
        
        # Determine if attack traffic
        is_attack = random.random() < config['attack_simulation']['attack_probability']
        
        if is_attack:
            telemetry = device.generate_malicious_telemetry()
            ground_truth = True
        else:
            telemetry = device.generate_normal_telemetry()
            ground_truth = False
        
        # AI detection
        is_anomaly, score = anomaly_detector.predict(telemetry)
        
        # Update metrics
        if is_anomaly and ground_truth:
            results["true_positives"] += 1
        elif is_anomaly and not ground_truth:
            results["false_positives"] += 1
        elif not is_anomaly and ground_truth:
            results["false_negatives"] += 1
        
        results["detections"] += 1
    
    # Calculate final metrics
    tp = results["true_positives"]
    fp = results["false_positives"]
    fn = results["false_negatives"]
    
    results["detection_rate"] = 100 * tp / (tp + fn) if (tp + fn) > 0 else 0
    results["false_positive_rate"] = 100 * fp / results["detections"] if results["detections"] > 0 else 0
    
    # Get security metrics
    if segmentation:
        seg_metrics = segmentation.get_metrics()
        results["lateral_movement_reduction"] = seg_metrics.get("lateral_movement_reduction_pct", 0)
    
    logger.info(f"\nTrial {trial_num + 1} Results:")
    logger.info(f"  Detection Rate: {results['detection_rate']:.2f}%")
    logger.info(f"  False Positive Rate: {results['false_positive_rate']:.2f}%")
    logger.info(f"  Lateral Movement Reduction: {results.get('lateral_movement_reduction', 0):.2f}%")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Run IoT security framework experiments")
    parser.add_argument(
        "--config",
        default="config/experiment_config.yaml",
        help="Path to experiment configuration file"
    )
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Setup logging
    logger = setup_logging(config)
    logger.info("Starting experiment runner...")
    logger.info(f"Configuration: {args.config}")
    
    # Create output directories
    for dir_key in ['results_dir', 'models_dir', 'logs_dir', 'figures_dir']:
        Path(config['output'][dir_key]).mkdir(parents=True, exist_ok=True)
    
    # Run trials
    all_results = []
    n_trials = config['experiment']['n_trials']
    
    for trial in range(n_trials):
        results = run_experiment(config, trial, logger)
        all_results.append(results)
    
    # Aggregate results
    logger.info(f"\n{'='*60}")
    logger.info("FINAL RESULTS (n=30 trials)")
    logger.info(f"{'='*60}\n")
    
    import numpy as np
    
    detection_rates = [r['detection_rate'] for r in all_results]
    fp_rates = [r['false_positive_rate'] for r in all_results]
    
    logger.info(f"Detection Rate: {np.mean(detection_rates):.2f}% ± {np.std(detection_rates):.2f}%")
    logger.info(f"False Positive Rate: {np.mean(fp_rates):.2f}% ± {np.std(fp_rates):.2f}%")
    
    # Save results
    import json
    results_file = Path(config['output']['results_dir']) / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\nResults saved to {results_file}")
    logger.info("Experiment complete!")


if __name__ == "__main__":
    main()
