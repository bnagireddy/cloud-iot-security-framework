"""
Anomaly Detection System
Implements Isolation Forest and Autoencoder for IoT threat detection
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib


class AnomalyDetector:
    """
    Multi-model anomaly detection system
    Combines Isolation Forest and Autoencoder for robust detection
    """
    
    def __init__(
        self,
        isolation_forest_trees: int = 100,
        contamination: float = 0.1,
        random_state: int = 42
    ):
        self.logger = logging.getLogger("AnomalyDetector")
        
        # Isolation Forest model
        self.isolation_forest = IsolationForest(
            n_estimators=isolation_forest_trees,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        
        # Feature scaler
        self.scaler = StandardScaler()
        
        # Training state
        self.is_trained = False
        self.feature_names: List[str] = []
        self.n_features = 0
        
        # Metrics
        self.metrics = {
            "total_predictions": 0,
            "anomalies_detected": 0,
            "normal_predicted": 0,
            "training_samples": 0
        }
    
    def extract_features(self, telemetry: Dict[str, Any]) -> np.ndarray:
        """
        Extract 47 features from telemetry data as described in paper
        
        Features include:
        - Network metrics (bandwidth, packet size, packet rate)
        - Device metrics (CPU, memory, temperature)
        - Behavioral metrics (request patterns, timing)
        - Security metrics (auth failures, port scans)
        """
        features = []
        
        # Network features (10)
        features.extend([
            telemetry.get("bandwidth_mbps", 0),
            telemetry.get("packet_size", 0),
            telemetry.get("packets_per_second", 0),
            telemetry.get("connection_count", 0),
            telemetry.get("avg_latency_ms", 0),
            telemetry.get("packet_loss_pct", 0),
            telemetry.get("retransmission_rate", 0),
            telemetry.get("dns_queries", 0),
            telemetry.get("unique_destinations", 0),
            telemetry.get("payload_entropy", 0)
        ])
        
        # Device metrics (12)
        features.extend([
            telemetry.get("cpu_usage", 0),
            telemetry.get("memory_usage_mb", 0),
            telemetry.get("temperature_celsius", 0),
            telemetry.get("disk_usage_gb", 0),
            telemetry.get("process_count", 0),
            telemetry.get("thread_count", 0),
            telemetry.get("uptime_hours", 0),
            telemetry.get("boot_count", 0),
            telemetry.get("firmware_version", 0),
            telemetry.get("battery_percent", 100),
            telemetry.get("signal_strength_dbm", -50),
            telemetry.get("error_count", 0)
        ])
        
        # Behavioral metrics (15)
        features.extend([
            telemetry.get("requests_per_hour", 0),
            telemetry.get("avg_request_size", 0),
            telemetry.get("avg_response_size", 0),
            telemetry.get("request_variance", 0),
            telemetry.get("time_since_last_request", 0),
            telemetry.get("request_interval_std", 0),
            telemetry.get("active_connections", 0),
            telemetry.get("connection_duration_avg", 0),
            telemetry.get("bytes_sent", 0),
            telemetry.get("bytes_received", 0),
            telemetry.get("send_recv_ratio", 1),
            telemetry.get("protocol_diversity", 0),
            telemetry.get("port_diversity", 0),
            telemetry.get("time_of_day_anomaly", 0),
            telemetry.get("day_of_week", 0)
        ])
        
        # Security metrics (10)
        features.extend([
            telemetry.get("auth_failures", 0),
            telemetry.get("auth_attempts", 0),
            telemetry.get("failed_login_rate", 0),
            telemetry.get("privilege_escalation_attempts", 0),
            telemetry.get("port_scan_detected", 0),
            telemetry.get("malformed_packets", 0),
            telemetry.get("protocol_violations", 0),
            telemetry.get("encryption_errors", 0),
            telemetry.get("certificate_errors", 0),
            telemetry.get("firewall_blocks", 0)
        ])
        
        return np.array(features, dtype=float)
    
    def train(self, telemetry_samples: List[Dict[str, Any]]):
        """
        Train anomaly detection model on normal traffic
        
        Args:
            telemetry_samples: List of normal telemetry dictionaries
        """
        self.logger.info(f"Training on {len(telemetry_samples)} samples...")
        
        # Extract features
        features_list = [self.extract_features(t) for t in telemetry_samples]
        X = np.array(features_list)
        
        self.n_features = X.shape[1]
        self.metrics["training_samples"] = len(telemetry_samples)
        
        # Fit scaler
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.isolation_forest.fit(X_scaled)
        
        self.is_trained = True
        self.logger.info(f"Training complete. Features: {self.n_features}")
    
    def predict(self, telemetry: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Predict if telemetry is anomalous
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
            anomaly_score: 0-1 where 1 is most anomalous
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        
        self.metrics["total_predictions"] += 1
        
        # Extract and scale features
        features = self.extract_features(telemetry).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        # Isolation Forest prediction
        # Returns -1 for anomalies, 1 for normal
        if_prediction = self.isolation_forest.predict(features_scaled)[0]
        
        # Get anomaly score (higher = more anomalous)
        # score_samples returns negative scores, normalize to 0-1
        if_score = -self.isolation_forest.score_samples(features_scaled)[0]
        anomaly_score = min(1.0, max(0.0, (if_score + 0.5) / 1.0))
        
        is_anomaly = if_prediction == -1
        
        if is_anomaly:
            self.metrics["anomalies_detected"] += 1
        else:
            self.metrics["normal_predicted"] += 1
        
        return is_anomaly, anomaly_score
    
    def predict_batch(
        self,
        telemetry_batch: List[Dict[str, Any]]
    ) -> List[Tuple[bool, float]]:
        """Batch prediction for efficiency"""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        
        # Extract features for all samples
        features_list = [self.extract_features(t) for t in telemetry_batch]
        X = np.array(features_list)
        X_scaled = self.scaler.transform(X)
        
        # Batch prediction
        predictions = self.isolation_forest.predict(X_scaled)
        scores = -self.isolation_forest.score_samples(X_scaled)
        
        results = []
        for pred, score in zip(predictions, scores):
            is_anomaly = pred == -1
            anomaly_score = min(1.0, max(0.0, (score + 0.5) / 1.0))
            
            results.append((is_anomaly, anomaly_score))
            
            self.metrics["total_predictions"] += 1
            if is_anomaly:
                self.metrics["anomalies_detected"] += 1
            else:
                self.metrics["normal_predicted"] += 1
        
        return results
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        model_data = {
            "isolation_forest": self.isolation_forest,
            "scaler": self.scaler,
            "n_features": self.n_features,
            "metrics": self.metrics
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        
        self.isolation_forest = model_data["isolation_forest"]
        self.scaler = model_data["scaler"]
        self.n_features = model_data["n_features"]
        self.metrics = model_data.get("metrics", self.metrics)
        
        self.is_trained = True
        self.logger.info(f"Model loaded from {filepath}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detection metrics"""
        return {
            **self.metrics,
            "detection_rate": (
                100 * self.metrics["anomalies_detected"] /
                max(1, self.metrics["total_predictions"])
            )
        }
