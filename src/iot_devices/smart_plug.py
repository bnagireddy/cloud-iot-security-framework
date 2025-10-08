"""
Smart Plug IoT Device Simulator
Simulates smart power outlet with energy monitoring
"""

import random
from typing import Dict, Any
from .base_device import IoTDevice


class SmartPlug(IoTDevice):
    """Smart Power Outlet with energy monitoring"""
    
    def __init__(self, device_id: str, **kwargs):
        super().__init__(
            device_id=device_id,
            device_type="smart_plug",
            **kwargs
        )
        
        # Plug-specific state
        self.is_on = random.choice([True, False])
        self.power_watts = 0 if not self.is_on else random.uniform(50, 150)
        self.voltage = 120.0
        self.current_amps = self.power_watts / self.voltage if self.is_on else 0
        
        # Schedule (simulate timed on/off)
        self.schedule_enabled = random.choice([True, False])
    
    def generate_normal_telemetry(self) -> Dict[str, Any]:
        """Generate normal smart plug telemetry"""
        
        # Simulate realistic on/off patterns
        if random.random() < 0.05:  # 5% chance to toggle
            self.is_on = not self.is_on
        
        if self.is_on:
            self.power_watts = random.uniform(50, 150)
            self.current_amps = self.power_watts / self.voltage
        else:
            self.power_watts = random.uniform(0, 2)  # Phantom load
            self.current_amps = self.power_watts / self.voltage
        
        return {
            "is_on": self.is_on,
            "power_watts": round(self.power_watts, 2),
            "voltage": self.voltage + random.uniform(-2, 2),
            "current_amps": round(self.current_amps, 3),
            "energy_kwh_today": random.uniform(0.5, 3.0),
            "temperature_celsius": random.uniform(25, 40),
            "uptime_hours": random.uniform(0, 168),
            "schedule_enabled": self.schedule_enabled,
            "connection_type": "wifi",
            "signal_strength_dbm": random.randint(-75, -35)
        }
    
    def generate_malicious_telemetry(self) -> Dict[str, Any]:
        """
        Generate malicious telemetry simulating:
        - Command injection
        - Credential stuffing
        - Firmware manipulation
        - Power cycling attacks
        """
        
        attack_type = random.choice([
            "command_injection",
            "credential_stuffing",
            "firmware_manipulation",
            "power_cycling_attack"
        ])
        
        base_telemetry = self.generate_normal_telemetry()
        
        if attack_type == "command_injection":
            # Unusual command patterns
            base_telemetry["_suspicious_commands"] = random.randint(50, 200)
            base_telemetry["uptime_hours"] = random.uniform(0, 1)  # Recently rebooted
            
        elif attack_type == "credential_stuffing":
            # Multiple failed auth attempts (in metrics)
            self.metrics["auth_failures"] = random.randint(10, 50)
            base_telemetry["_auth_failures"] = self.metrics["auth_failures"]
            
        elif attack_type == "firmware_manipulation":
            # Abnormal behavior post-firmware change
            base_telemetry["power_watts"] = random.uniform(200, 500)  # Abnormally high
            base_telemetry["temperature_celsius"] = random.uniform(60, 80)
            
        elif attack_type == "power_cycling_attack":
            # Rapid on/off cycles (stress attack)
            base_telemetry["_power_cycles_per_hour"] = random.randint(100, 500)
            base_telemetry["temperature_celsius"] = random.uniform(50, 70)
        
        base_telemetry["_attack_type"] = attack_type
        base_telemetry["_is_attack"] = True
        
        return base_telemetry
    
    def handle_command(self, command: Dict[str, Any]):
        """Handle commands from cloud"""
        cmd_type = command.get("command")
        
        if cmd_type == "turn_on":
            self.is_on = True
            self.power_watts = random.uniform(50, 150)
            self.logger.info("Plug turned ON")
            
        elif cmd_type == "turn_off":
            self.is_on = False
            self.power_watts = 0
            self.logger.info("Plug turned OFF")
            
        elif cmd_type == "toggle":
            self.is_on = not self.is_on
            self.logger.info(f"Plug toggled to {'ON' if self.is_on else 'OFF'}")
            
        elif cmd_type == "set_schedule":
            self.schedule_enabled = command.get("enabled", True)
            self.logger.info(f"Schedule {'enabled' if self.schedule_enabled else 'disabled'}")
            
        elif cmd_type == "quarantine":
            self.logger.warning("Device quarantined by security policy")
            self.is_running = False
            
        else:
            self.logger.warning(f"Unknown command: {cmd_type}")
