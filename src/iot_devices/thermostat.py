"""
Smart Thermostat IoT Device Simulator
Simulates HVAC controller with temperature/humidity sensing
"""

import random
from typing import Dict, Any
from .base_device import IoTDevice


class Thermostat(IoTDevice):
    """Smart Thermostat with HVAC control"""
    
    def __init__(self, device_id: str, **kwargs):
        super().__init__(
            device_id=device_id,
            device_type="thermostat",
            **kwargs
        )
        
        # Thermostat-specific state
        self.current_temp = random.uniform(18, 24)
        self.target_temp = random.uniform(20, 23)
        self.humidity = random.uniform(40, 60)
        self.mode = random.choice(["heat", "cool", "auto", "off"])
        self.fan_running = random.choice([True, False])
        
        # HVAC system
        self.hvac_running = False
    
    def generate_normal_telemetry(self) -> Dict[str, Any]:
        """Generate normal thermostat telemetry"""
        
        # Simulate temperature changes
        if self.mode == "heat" and self.current_temp < self.target_temp:
            self.hvac_running = True
            self.current_temp += random.uniform(0, 0.5)
        elif self.mode == "cool" and self.current_temp > self.target_temp:
            self.hvac_running = True
            self.current_temp -= random.uniform(0, 0.5)
        else:
            self.hvac_running = random.random() < 0.2
            self.current_temp += random.uniform(-0.2, 0.2)
        
        # Keep temperature in realistic range
        self.current_temp = max(15, min(30, self.current_temp))
        
        # Humidity fluctuates
        self.humidity += random.uniform(-2, 2)
        self.humidity = max(30, min(70, self.humidity))
        
        return {
            "current_temp_celsius": round(self.current_temp, 1),
            "target_temp_celsius": round(self.target_temp, 1),
            "humidity_percent": round(self.humidity, 1),
            "mode": self.mode,
            "hvac_running": self.hvac_running,
            "fan_running": self.fan_running or self.hvac_running,
            "energy_usage_kwh": random.uniform(0.5, 2.5) if self.hvac_running else random.uniform(0, 0.1),
            "runtime_minutes_today": random.randint(0, 480),
            "filter_life_percent": random.randint(20, 100),
            "connection_type": "wifi",
            "signal_strength_dbm": random.randint(-70, -30)
        }
    
    def generate_malicious_telemetry(self) -> Dict[str, Any]:
        """
        Generate malicious telemetry simulating:
        - Ransomware (temperature manipulation)
        - Physical damage attacks
        - Data manipulation
        - DoS attacks
        """
        
        attack_type = random.choice([
            "ransomware_temp_manipulation",
            "physical_damage",
            "data_manipulation",
            "dos_attack"
        ])
        
        base_telemetry = self.generate_normal_telemetry()
        
        if attack_type == "ransomware_temp_manipulation":
            # Extreme temperature settings
            base_telemetry["target_temp_celsius"] = random.choice([10, 35])
            base_telemetry["hvac_running"] = True
            base_telemetry["energy_usage_kwh"] = random.uniform(5.0, 10.0)
            
        elif attack_type == "physical_damage":
            # Rapid cycling to damage HVAC
            base_telemetry["hvac_running"] = random.choice([True, False])
            base_telemetry["_hvac_cycles_per_hour"] = random.randint(50, 200)
            base_telemetry["energy_usage_kwh"] = random.uniform(4.0, 8.0)
            
        elif attack_type == "data_manipulation":
            # False sensor readings
            base_telemetry["current_temp_celsius"] = random.uniform(-10, 50)
            base_telemetry["humidity_percent"] = random.uniform(0, 100)
            base_telemetry["filter_life_percent"] = random.randint(-50, 150)
            
        elif attack_type == "dos_attack":
            # Flood cloud with requests
            base_telemetry["_requests_per_second"] = random.randint(100, 1000)
            self.metrics["packets_sent"] += random.randint(500, 2000)
        
        base_telemetry["_attack_type"] = attack_type
        base_telemetry["_is_attack"] = True
        
        return base_telemetry
    
    def handle_command(self, command: Dict[str, Any]):
        """Handle commands from cloud"""
        cmd_type = command.get("command")
        
        if cmd_type == "set_temperature":
            self.target_temp = command.get("temperature", self.target_temp)
            self.logger.info(f"Target temperature set to {self.target_temp}°C")
            
        elif cmd_type == "set_mode":
            self.mode = command.get("mode", self.mode)
            self.logger.info(f"Mode changed to {self.mode}")
            
        elif cmd_type == "fan_on":
            self.fan_running = True
            self.logger.info("Fan turned ON")
            
        elif cmd_type == "fan_off":
            self.fan_running = False
            self.logger.info("Fan turned OFF")
            
        elif cmd_type == "quarantine":
            self.logger.warning("Device quarantined by security policy")
            self.mode = "off"
            self.is_running = False
            
        else:
            self.logger.warning(f"Unknown command: {cmd_type}")
