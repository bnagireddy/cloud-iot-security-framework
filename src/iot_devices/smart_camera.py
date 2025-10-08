"""
Smart Camera IoT Device Simulator
Simulates IP security camera with video analytics
"""

import random
import time
from typing import Dict, Any
from .base_device import IoTDevice


class SmartCamera(IoTDevice):
    """Smart Security Camera with video analytics"""
    
    def __init__(self, device_id: str, **kwargs):
        super().__init__(
            device_id=device_id,
            device_type="smart_camera",
            **kwargs
        )
        
        # Camera-specific state
        self.resolution = "1920x1080"
        self.fps = 30
        self.motion_detected = False
        self.recording = False
        self.night_mode = False
        
        # Normal behavior patterns
        self.normal_bandwidth_mbps = random.uniform(2.0, 5.0)
        self.normal_packet_size = random.randint(1200, 1500)
    
    def generate_normal_telemetry(self) -> Dict[str, Any]:
        """Generate normal camera telemetry"""
        
        # Simulate realistic camera behavior
        self.motion_detected = random.random() < 0.15  # 15% chance of motion
        self.recording = self.motion_detected or random.random() < 0.3
        self.night_mode = random.random() < 0.4  # 40% chance night mode
        
        return {
            "resolution": self.resolution,
            "fps": self.fps + random.randint(-2, 2),
            "bandwidth_mbps": self.normal_bandwidth_mbps + random.uniform(-0.5, 0.5),
            "packet_size": self.normal_packet_size + random.randint(-100, 100),
            "motion_detected": self.motion_detected,
            "recording": self.recording,
            "night_mode": self.night_mode,
            "cpu_usage": random.uniform(20, 45),
            "temperature_celsius": random.uniform(35, 50),
            "memory_usage_mb": random.randint(180, 250),
            "storage_used_gb": random.uniform(10, 50),
            "connection_type": "wifi" if random.random() < 0.7 else "ethernet",
            "signal_strength_dbm": random.randint(-70, -30) if random.random() < 0.7 else None
        }
    
    def generate_malicious_telemetry(self) -> Dict[str, Any]:
        """
        Generate malicious telemetry simulating various attacks:
        - Data exfiltration (high bandwidth)
        - Botnet participation (abnormal packet patterns)
        - Resource exhaustion
        - Reconnaissance scanning
        """
        
        attack_type = random.choice([
            "data_exfiltration",
            "botnet_ddos",
            "resource_exhaustion",
            "scanning"
        ])
        
        base_telemetry = self.generate_normal_telemetry()
        
        if attack_type == "data_exfiltration":
            # Abnormally high bandwidth usage
            base_telemetry["bandwidth_mbps"] = random.uniform(15.0, 30.0)
            base_telemetry["packet_size"] = random.randint(2500, 4000)
            base_telemetry["recording"] = True
            
        elif attack_type == "botnet_ddos":
            # Many small packets (DDoS participation)
            base_telemetry["bandwidth_mbps"] = random.uniform(8.0, 12.0)
            base_telemetry["packet_size"] = random.randint(64, 256)
            base_telemetry["cpu_usage"] = random.uniform(70, 95)
            
        elif attack_type == "resource_exhaustion":
            # Resource exhaustion attack
            base_telemetry["cpu_usage"] = random.uniform(85, 99)
            base_telemetry["memory_usage_mb"] = random.randint(450, 512)
            base_telemetry["temperature_celsius"] = random.uniform(65, 80)
            
        elif attack_type == "scanning":
            # Network scanning behavior
            base_telemetry["bandwidth_mbps"] = random.uniform(6.0, 10.0)
            base_telemetry["packet_size"] = random.randint(40, 100)
            base_telemetry["connection_type"] = "ethernet"
        
        # Add attack indicator (for ground truth)
        base_telemetry["_attack_type"] = attack_type
        base_telemetry["_is_attack"] = True
        
        return base_telemetry
    
    def handle_command(self, command: Dict[str, Any]):
        """Handle commands from cloud"""
        cmd_type = command.get("command")
        
        if cmd_type == "start_recording":
            self.recording = True
            self.logger.info("Started recording")
            
        elif cmd_type == "stop_recording":
            self.recording = False
            self.logger.info("Stopped recording")
            
        elif cmd_type == "set_resolution":
            self.resolution = command.get("resolution", self.resolution)
            self.logger.info(f"Resolution changed to {self.resolution}")
            
        elif cmd_type == "enable_night_mode":
            self.night_mode = True
            self.logger.info("Night mode enabled")
            
        elif cmd_type == "disable_night_mode":
            self.night_mode = False
            self.logger.info("Night mode disabled")
            
        elif cmd_type == "quarantine":
            # Security response - isolate device
            self.logger.warning("Device quarantined by security policy")
            self.is_running = False
            
        else:
            self.logger.warning(f"Unknown command: {cmd_type}")
