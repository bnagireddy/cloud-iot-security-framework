"""
Threat Classification System
Implements Random Forest and 1D CNN for attack type classification
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib


class ThreatClassifier:
    """
    Multi-class threat classifier
    Identifies specific attack types: botnet, data exfiltration, scanning, etc.
    """
    
    # Attack categories as defined in paper
    ATTACK_CATEGORIES = [
        "normal",
        "botnet_ddos",
        "data_exfiltration",
        "scanning",
        "credential_stuffing",
        "command_injection",
        "ransomware",
        "firmware_manipulation",
        "sensor_spoofing",
        "lateral_movement"
    ]
    
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 20,
        random_state: int = 42
    ):
        self.logger = logging.getLogger("ThreatClassifier")
        
        # Random Forest classifier
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            class_weight='balanced'  # Handle class imbalance
        )
        
        # Label encoder
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.ATTACK_CATEGORIES)
        
        # Training state
        self.is_trained = False
        self.n_features = 0
        
        # Metrics per class
        self.metrics = {
            "total_predictions": 0,
            "correct_predictions": 0,
            "class_predictions": {cat: 0 for cat in self.ATTACK_CATEGORIES},
            "class_correct": {cat: 0 for cat in self.ATTACK_CATEGORIES}
        }
    
    def extract_features(self, telemetry: Dict[str, Any]) -> np.ndarray:
        """
        Extract features for classification (same 47 features as anomaly detector)
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
    
    def train(
        self,
        telemetry_samples: List[Dict[str, Any]],
        labels: List[str]
    ):
        """
        Train threat classifier
        
        Args:
            telemetry_samples: List of telemetry dictionaries
            labels: List of attack category labels
        """
        self.logger.info(f"Training on {len(telemetry_samples)} labeled samples...")
        
        # Extract features
        features_list = [self.extract_features(t) for t in telemetry_samples]
        X = np.array(features_list)
        
        # Encode labels
        y = self.label_encoder.transform(labels)
        
        self.n_features = X.shape[1]
        
        # Train Random Forest
        self.classifier.fit(X, y)
        
        self.is_trained = True
        
        # Log class distribution
        unique, counts = np.unique(labels, return_counts=True)
        class_dist = dict(zip(unique, counts))
        self.logger.info(f"Training complete. Class distribution: {class_dist}")
    
    def predict(self, telemetry: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predict attack category
        
        Returns:
            Tuple of (attack_category, confidence)
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        
        self.metrics["total_predictions"] += 1
        
        # Extract features
        features = self.extract_features(telemetry).reshape(1, -1)
        
        # Predict
        prediction_encoded = self.classifier.predict(features)[0]
        prediction_proba = self.classifier.predict_proba(features)[0]
        
        # Decode prediction
        attack_category = self.label_encoder.inverse_transform([prediction_encoded])[0]
        confidence = prediction_proba[prediction_encoded]
        
        # Update metrics
        self.metrics["class_predictions"][attack_category] += 1
        
        return attack_category, confidence
    
    def predict_batch(
        self,
        telemetry_batch: List[Dict[str, Any]]
    ) -> List[Tuple[str, float]]:
        """Batch prediction for efficiency"""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        
        # Extract features
        features_list = [self.extract_features(t) for t in telemetry_batch]
        X = np.array(features_list)
        
        # Batch prediction
        predictions_encoded = self.classifier.predict(X)
        predictions_proba = self.classifier.predict_proba(X)
        
        results = []
        for pred_enc, proba in zip(predictions_encoded, predictions_proba):
            attack_category = self.label_encoder.inverse_transform([pred_enc])[0]
            confidence = proba[pred_enc]
            
            results.append((attack_category, confidence))
            
            self.metrics["total_predictions"] += 1
            self.metrics["class_predictions"][attack_category] += 1
        
        return results
    
    def evaluate(
        self,
        telemetry_samples: List[Dict[str, Any]],
        true_labels: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate classifier on test set
        
        Returns:
            Metrics including accuracy, precision, recall per class
        """
        predictions = [self.predict(t)[0] for t in telemetry_samples]
        
        # Overall accuracy
        correct = sum(1 for pred, true in zip(predictions, true_labels) if pred == true)
        accuracy = 100 * correct / len(true_labels)
        
        # Per-class metrics
        class_metrics = {}
        for category in self.ATTACK_CATEGORIES:
            tp = sum(1 for p, t in zip(predictions, true_labels) if p == category and t == category)
            fp = sum(1 for p, t in zip(predictions, true_labels) if p == category and t != category)
            fn = sum(1 for p, t in zip(predictions, true_labels) if p != category and t == category)
            
            precision = 100 * tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = 100 * tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            class_metrics[category] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": sum(1 for t in true_labels if t == category)
            }
        
        return {
            "overall_accuracy": accuracy,
            "class_metrics": class_metrics,
            "total_samples": len(true_labels)
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from Random Forest"""
        if not self.is_trained:
            return {}
        
        importances = self.classifier.feature_importances_
        
        # Generate feature names (simplified)
        feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        return dict(zip(feature_names, importances))
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        model_data = {
            "classifier": self.classifier,
            "label_encoder": self.label_encoder,
            "n_features": self.n_features,
            "metrics": self.metrics
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        
        self.classifier = model_data["classifier"]
        self.label_encoder = model_data["label_encoder"]
        self.n_features = model_data["n_features"]
        self.metrics = model_data.get("metrics", self.metrics)
        
        self.is_trained = True
        self.logger.info(f"Model loaded from {filepath}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get classification metrics"""
        return {
            **self.metrics,
            "accuracy": (
                100 * self.metrics["correct_predictions"] /
                max(1, self.metrics["total_predictions"])
            )
        }
