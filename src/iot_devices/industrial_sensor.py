"""
Industrial IoT Sensor Simulator
Simulates industrial sensors (pressure, vibration, temperature) for manufacturing
"""

import random
import math
from typing import Dict, Any
from .base_device import IoTDevice


class IndustrialSensor(IoTDevice):
    """Industrial sensor for manufacturing/critical infrastructure"""
    
    def __init__(self, device_id: str, sensor_type: str = "pressure", **kwargs):
        super().__init__(
            device_id=device_id,
            device_type="industrial_sensor",
            **kwargs
        )
        
        # Sensor type: pressure, vibration, temperature, flow
        self.sensor_type = sensor_type
        
        # Baseline values
        if sensor_type == "pressure":
            self.baseline_value = random.uniform(100, 150)  # PSI
            self.unit = "PSI"
        elif sensor_type == "vibration":
            self.baseline_value = random.uniform(0.5, 2.0)  # mm/s
            self.unit = "mm/s"
        elif sensor_type == "temperature":
            self.baseline_value = random.uniform(80, 120)  # Celsius
            self.unit = "°C"
        elif sensor_type == "flow":
            self.baseline_value = random.uniform(50, 100)  # L/min
            self.unit = "L/min"
        else:
            self.baseline_value = random.uniform(0, 100)
            self.unit = "units"
        
        # Operational state
        self.alarm_active = False
        self.calibration_due = random.choice([True, False])
    
    def generate_normal_telemetry(self) -> Dict[str, Any]:
        """Generate normal industrial sensor telemetry"""
        
        # Add realistic noise to baseline
        noise = random.uniform(-5, 5)
        current_value = self.baseline_value + noise
        
        # Periodic variation (simulating normal operation cycles)
        import time
        cycle_variation = math.sin(time.time() / 100) * 10
        current_value += cycle_variation
        
        # Check if alarm should trigger (exceeds thresholds)
        if self.sensor_type == "pressure":
            self.alarm_active = current_value > 180 or current_value < 80
        elif self.sensor_type == "vibration":
            self.alarm_active = current_value > 5.0
        elif self.sensor_type == "temperature":
            self.alarm_active = current_value > 150 or current_value < 60
        elif self.sensor_type == "flow":
            self.alarm_active = current_value < 20 or current_value > 150
        
        return {
            "sensor_type": self.sensor_type,
            "value": round(current_value, 2),
            "unit": self.unit,
            "alarm_active": self.alarm_active,
            "calibration_due": self.calibration_due,
            "sample_rate_hz": random.choice([1, 10, 100]),
            "accuracy_percent": random.uniform(98, 100),
            "battery_percent": random.randint(70, 100),
            "signal_quality": random.uniform(85, 100),
            "uptime_hours": random.uniform(0, 2160),  # Up to 90 days
            "connection_type": random.choice(["ethernet", "rs485", "4-20mA"])
        }
    
    def generate_malicious_telemetry(self) -> Dict[str, Any]:
        """
        Generate malicious telemetry simulating:
        - Sensor spoofing (false readings)
        - Man-in-the-middle attacks
        - Replay attacks
        - Critical infrastructure sabotage
        """
        
        attack_type = random.choice([
            "sensor_spoofing",
            "mitm_attack",
            "replay_attack",
            "sabotage"
        ])
        
        base_telemetry = self.generate_normal_telemetry()
        
        if attack_type == "sensor_spoofing":
            # Report false safe readings while actual values are dangerous
            if self.sensor_type == "pressure":
                base_telemetry["value"] = random.uniform(200, 300)  # Dangerously high
            elif self.sensor_type == "vibration":
                base_telemetry["value"] = random.uniform(10, 20)  # Critical vibration
            elif self.sensor_type == "temperature":
                base_telemetry["value"] = random.uniform(180, 250)  # Overheating
            elif self.sensor_type == "flow":
                base_telemetry["value"] = random.uniform(0, 5)  # Flow stopped
            
            base_telemetry["alarm_active"] = False  # Suppress alarm (attack)
            
        elif attack_type == "mitm_attack":
            # Manipulated data in transit
            base_telemetry["value"] *= random.uniform(0.5, 1.5)
            base_telemetry["accuracy_percent"] = random.uniform(60, 85)
            base_telemetry["_checksum_invalid"] = True
            
        elif attack_type == "replay_attack":
            # Replaying old sensor data
            base_telemetry["value"] = self.baseline_value  # Static value
            base_telemetry["_timestamp_stale"] = True
            base_telemetry["_replay_detected"] = random.choice([True, False])
            
        elif attack_type == "sabotage":
            # Attempting to damage equipment
            if self.sensor_type == "pressure":
                base_telemetry["value"] = random.choice([0, 500])  # Extreme values
            base_telemetry["alarm_active"] = True
            base_telemetry["_emergency_shutdown"] = random.choice([True, False])
        
        base_telemetry["_attack_type"] = attack_type
        base_telemetry["_is_attack"] = True
        
        return base_telemetry
    
    def handle_command(self, command: Dict[str, Any]):
        """Handle commands from cloud"""
        cmd_type = command.get("command")
        
        if cmd_type == "calibrate":
            self.calibration_due = False
            self.logger.info("Sensor calibrated")
            
        elif cmd_type == "reset_alarm":
            self.alarm_active = False
            self.logger.info("Alarm reset")
            
        elif cmd_type == "set_sample_rate":
            sample_rate = command.get("rate_hz", 1)
            self.logger.info(f"Sample rate set to {sample_rate} Hz")
            
        elif cmd_type == "emergency_shutdown":
            self.logger.critical("EMERGENCY SHUTDOWN INITIATED")
            self.is_running = False
            
        elif cmd_type == "quarantine":
            self.logger.warning("Device quarantined by security policy")
            self.is_running = False
            
        else:
            self.logger.warning(f"Unknown command: {cmd_type}")
