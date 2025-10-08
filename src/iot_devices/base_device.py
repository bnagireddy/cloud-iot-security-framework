"""
IoT Device Base Class
Simulates various IoT device types with realistic behaviors
"""

import time
import random
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


class IoTDevice(ABC):
    """Base class for all IoT device types"""
    
    def __init__(
        self,
        device_id: str,
        device_type: str,
        mqtt_broker: str = "localhost",
        mqtt_port: int = 1883,
        enable_encryption: bool = True
    ):
        self.device_id = device_id
        self.device_type = device_type
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.enable_encryption = enable_encryption
        
        # State
        self.is_running = False
        self.is_compromised = False
        self.auth_token: Optional[str] = None
        self.last_auth_time: Optional[datetime] = None
        
        # Security
        if enable_encryption:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
        
        # MQTT Client
        self.client = mqtt.Client(client_id=device_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        # Logging
        self.logger = logging.getLogger(f"IoTDevice.{device_id}")
        
        # Metrics
        self.metrics = {
            "packets_sent": 0,
            "packets_received": 0,
            "auth_attempts": 0,
            "auth_failures": 0,
            "data_sent_bytes": 0
        }
    
    def authenticate(self, auth_server_url: str) -> bool:
        """
        Perform zero trust authentication with cloud service
        """
        try:
            self.metrics["auth_attempts"] += 1
            
            # Generate authentication request
            auth_data = {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "timestamp": datetime.utcnow().isoformat(),
                "public_key": self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode() if self.enable_encryption else None
            }
            
            # In real implementation, send to auth server
            # For simulation, generate mock token
            self.auth_token = self._generate_mock_token()
            self.last_auth_time = datetime.utcnow()
            
            self.logger.info(f"Authentication successful for {self.device_id}")
            return True
            
        except Exception as e:
            self.metrics["auth_failures"] += 1
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def _generate_mock_token(self) -> str:
        """Generate mock JWT token for simulation"""
        import hashlib
        token_data = f"{self.device_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    def connect_to_gateway(self) -> bool:
        """Connect to MQTT gateway"""
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            self.client.loop_start()
            self.is_running = True
            self.logger.info(f"Connected to gateway at {self.mqtt_broker}:{self.mqtt_port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from gateway"""
        self.client.loop_stop()
        self.client.disconnect()
        self.is_running = False
        self.logger.info(f"Disconnected from gateway")
    
    def send_telemetry(self, data: Dict[str, Any]):
        """Send telemetry data to cloud"""
        try:
            # Check if re-authentication needed (every 5 minutes)
            if self.last_auth_time:
                elapsed = (datetime.utcnow() - self.last_auth_time).total_seconds()
                if elapsed > 300:  # 5 minutes
                    self.authenticate(auth_server_url="mock://auth")
            
            # Prepare telemetry payload
            payload = {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "auth_token": self.auth_token
            }
            
            # Publish to MQTT topic
            topic = f"iot/{self.device_type}/{self.device_id}/telemetry"
            message = json.dumps(payload)
            
            self.client.publish(topic, message, qos=1)
            
            # Update metrics
            self.metrics["packets_sent"] += 1
            self.metrics["data_sent_bytes"] += len(message)
            
            self.logger.debug(f"Sent telemetry: {data}")
            
        except Exception as e:
            self.logger.error(f"Failed to send telemetry: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.logger.info("MQTT connection established")
            # Subscribe to command topic
            client.subscribe(f"iot/{self.device_type}/{self.device_id}/commands")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for MQTT messages"""
        try:
            self.metrics["packets_received"] += 1
            payload = json.loads(msg.payload.decode())
            self.handle_command(payload)
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")
    
    def compromise(self):
        """Simulate device compromise"""
        self.is_compromised = True
        self.logger.warning(f"Device {self.device_id} has been compromised!")
    
    def restore(self):
        """Restore compromised device"""
        self.is_compromised = False
        # Re-authenticate after restore
        self.authenticate(auth_server_url="mock://auth")
        self.logger.info(f"Device {self.device_id} has been restored")
    
    @abstractmethod
    def generate_normal_telemetry(self) -> Dict[str, Any]:
        """Generate normal device telemetry (device-specific)"""
        pass
    
    @abstractmethod
    def generate_malicious_telemetry(self) -> Dict[str, Any]:
        """Generate malicious telemetry for attack simulation"""
        pass
    
    @abstractmethod
    def handle_command(self, command: Dict[str, Any]):
        """Handle commands from cloud (device-specific)"""
        pass
    
    def run(self, duration: int = 3600, attack_probability: float = 0.0):
        """
        Run device simulation
        
        Args:
            duration: Simulation duration in seconds
            attack_probability: Probability of generating malicious traffic (0-1)
        """
        if not self.is_running:
            self.connect_to_gateway()
            self.authenticate(auth_server_url="mock://auth")
        
        start_time = time.time()
        
        while time.time() - start_time < duration and self.is_running:
            try:
                # Determine if this is attack traffic
                is_attack = random.random() < attack_probability or self.is_compromised
                
                # Generate and send telemetry
                if is_attack:
                    telemetry = self.generate_malicious_telemetry()
                else:
                    telemetry = self.generate_normal_telemetry()
                
                self.send_telemetry(telemetry)
                
                # Random sleep interval (realistic IoT behavior)
                sleep_time = random.uniform(1, 10)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in run loop: {e}")
        
        self.disconnect()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get device metrics"""
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "is_compromised": self.is_compromised,
            "metrics": self.metrics,
            "uptime_seconds": (datetime.utcnow() - self.last_auth_time).total_seconds() 
                             if self.last_auth_time else 0
        }


# Import serialization for key export
from cryptography.hazmat.primitives import serialization
