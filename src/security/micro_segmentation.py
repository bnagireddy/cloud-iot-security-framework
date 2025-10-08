"""
Micro-segmentation Manager
Implements network micro-segmentation with 10 security zones
"""

import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SecurityZone(Enum):
    """Security zones for micro-segmentation"""
    EXTERNAL = "external"
    DMZ = "dmz"
    CLOUD_GATEWAY = "cloud_gateway"
    IOT_TRUSTED = "iot_trusted"
    IOT_UNTRUSTED = "iot_untrusted"
    IOT_QUARANTINE = "iot_quarantine"
    MANAGEMENT = "management"
    DATA_PROCESSING = "data_processing"
    AI_ANALYTICS = "ai_analytics"
    ADMIN = "admin"


@dataclass
class NetworkPolicy:
    """Network segmentation policy"""
    name: str
    source_zone: SecurityZone
    dest_zone: SecurityZone
    allowed_protocols: List[str]
    allowed_ports: List[int]
    action: str  # "allow" or "deny"
    priority: int
    enabled: bool = True
    
    def matches(self, src: SecurityZone, dst: SecurityZone, protocol: str, port: int) -> bool:
        """Check if traffic matches this policy"""
        return (
            self.source_zone == src and
            self.dest_zone == dst and
            (protocol in self.allowed_protocols or "*" in self.allowed_protocols) and
            (port in self.allowed_ports or 0 in self.allowed_ports)  # 0 = any port
        )


class MicroSegmentationManager:
    """
    Manages network micro-segmentation policies
    Implements zero trust network architecture with 10 security zones
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MicroSegmentation")
        
        # Device zone assignments
        self.device_zones: Dict[str, SecurityZone] = {}
        
        # Default policies (zero trust: deny by default)
        self.policies: List[NetworkPolicy] = []
        self._initialize_default_policies()
        
        # Traffic logs for analysis
        self.traffic_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "packets_allowed": 0,
            "packets_denied": 0,
            "zone_violations": 0,
            "lateral_movement_blocked": 0
        }
    
    def _initialize_default_policies(self):
        """Initialize default micro-segmentation policies"""
        
        # IoT Trusted -> Cloud Gateway (telemetry upload)
        self.policies.append(NetworkPolicy(
            name="iot_trusted_to_gateway",
            source_zone=SecurityZone.IOT_TRUSTED,
            dest_zone=SecurityZone.CLOUD_GATEWAY,
            allowed_protocols=["mqtt", "coap", "https"],
            allowed_ports=[1883, 5683, 8883, 443],
            action="allow",
            priority=100
        ))
        
        # Cloud Gateway -> Data Processing
        self.policies.append(NetworkPolicy(
            name="gateway_to_processing",
            source_zone=SecurityZone.CLOUD_GATEWAY,
            dest_zone=SecurityZone.DATA_PROCESSING,
            allowed_protocols=["https", "grpc"],
            allowed_ports=[443, 50051],
            action="allow",
            priority=100
        ))
        
        # Data Processing -> AI Analytics
        self.policies.append(NetworkPolicy(
            name="processing_to_ai",
            source_zone=SecurityZone.DATA_PROCESSING,
            dest_zone=SecurityZone.AI_ANALYTICS,
            allowed_protocols=["https", "grpc"],
            allowed_ports=[443, 50051, 8080],
            action="allow",
            priority=100
        ))
        
        # AI Analytics -> Data Processing (threat alerts)
        self.policies.append(NetworkPolicy(
            name="ai_to_processing",
            source_zone=SecurityZone.AI_ANALYTICS,
            dest_zone=SecurityZone.DATA_PROCESSING,
            allowed_protocols=["https"],
            allowed_ports=[443],
            action="allow",
            priority=100
        ))
        
        # Management -> All zones (admin access)
        for zone in SecurityZone:
            if zone not in [SecurityZone.EXTERNAL, SecurityZone.IOT_QUARANTINE]:
                self.policies.append(NetworkPolicy(
                    name=f"management_to_{zone.value}",
                    source_zone=SecurityZone.MANAGEMENT,
                    dest_zone=zone,
                    allowed_protocols=["ssh", "https"],
                    allowed_ports=[22, 443],
                    action="allow",
                    priority=90
                ))
        
        # Admin -> Management
        self.policies.append(NetworkPolicy(
            name="admin_to_management",
            source_zone=SecurityZone.ADMIN,
            dest_zone=SecurityZone.MANAGEMENT,
            allowed_protocols=["ssh", "https"],
            allowed_ports=[22, 443],
            action="allow",
            priority=95
        ))
        
        # DENY IoT-to-IoT lateral movement (zero trust)
        for src_zone in [SecurityZone.IOT_TRUSTED, SecurityZone.IOT_UNTRUSTED]:
            for dst_zone in [SecurityZone.IOT_TRUSTED, SecurityZone.IOT_UNTRUSTED]:
                if src_zone != dst_zone:
                    self.policies.append(NetworkPolicy(
                        name=f"deny_{src_zone.value}_to_{dst_zone.value}",
                        source_zone=src_zone,
                        dest_zone=dst_zone,
                        allowed_protocols=["*"],
                        allowed_ports=[0],
                        action="deny",
                        priority=200  # High priority deny
                    ))
        
        # DENY quarantine zone (complete isolation)
        for zone in SecurityZone:
            if zone != SecurityZone.IOT_QUARANTINE:
                self.policies.append(NetworkPolicy(
                    name=f"deny_quarantine_to_{zone.value}",
                    source_zone=SecurityZone.IOT_QUARANTINE,
                    dest_zone=zone,
                    allowed_protocols=["*"],
                    allowed_ports=[0],
                    action="deny",
                    priority=300  # Highest priority
                ))
    
    def assign_device_zone(self, device_id: str, zone: SecurityZone):
        """Assign device to security zone"""
        self.device_zones[device_id] = zone
        self.logger.info(f"Device {device_id} assigned to zone {zone.value}")
    
    def get_device_zone(self, device_id: str) -> Optional[SecurityZone]:
        """Get device's current zone"""
        return self.device_zones.get(device_id)
    
    def quarantine_device(self, device_id: str):
        """Move device to quarantine zone"""
        old_zone = self.device_zones.get(device_id)
        self.device_zones[device_id] = SecurityZone.IOT_QUARANTINE
        self.logger.warning(
            f"Device {device_id} quarantined (was in {old_zone.value if old_zone else 'unknown'})"
        )
    
    def restore_device(self, device_id: str, zone: SecurityZone = SecurityZone.IOT_UNTRUSTED):
        """Restore device from quarantine"""
        if self.device_zones.get(device_id) == SecurityZone.IOT_QUARANTINE:
            self.device_zones[device_id] = zone
            self.logger.info(f"Device {device_id} restored to {zone.value}")
    
    def evaluate_traffic(
        self,
        src_device: str,
        dst_device: str,
        protocol: str,
        port: int
    ) -> bool:
        """
        Evaluate if traffic should be allowed based on micro-segmentation policies
        
        Returns:
            True if allowed, False if denied
        """
        src_zone = self.device_zones.get(src_device)
        dst_zone = self.device_zones.get(dst_device)
        
        if not src_zone or not dst_zone:
            self.logger.warning(f"Unknown zone for {src_device} or {dst_device}")
            self.metrics["packets_denied"] += 1
            return False
        
        # Find matching policies (sorted by priority)
        matching_policies = [
            p for p in sorted(self.policies, key=lambda x: x.priority, reverse=True)
            if p.enabled and p.matches(src_zone, dst_zone, protocol, port)
        ]
        
        if matching_policies:
            policy = matching_policies[0]  # Highest priority
            allowed = policy.action == "allow"
            
            if allowed:
                self.metrics["packets_allowed"] += 1
            else:
                self.metrics["packets_denied"] += 1
                
                # Track lateral movement attempts
                if src_zone in [SecurityZone.IOT_TRUSTED, SecurityZone.IOT_UNTRUSTED]:
                    if dst_zone in [SecurityZone.IOT_TRUSTED, SecurityZone.IOT_UNTRUSTED]:
                        self.metrics["lateral_movement_blocked"] += 1
                        self.logger.warning(
                            f"Lateral movement blocked: {src_device} -> {dst_device}"
                        )
            
            # Log traffic
            self.traffic_log.append({
                "src_device": src_device,
                "dst_device": dst_device,
                "src_zone": src_zone.value,
                "dst_zone": dst_zone.value,
                "protocol": protocol,
                "port": port,
                "policy": policy.name,
                "action": policy.action,
                "allowed": allowed
            })
            
            return allowed
        
        # No matching policy - default deny (zero trust)
        self.metrics["packets_denied"] += 1
        self.metrics["zone_violations"] += 1
        self.logger.warning(
            f"No policy match (default deny): {src_device}({src_zone.value}) -> "
            f"{dst_device}({dst_zone.value}) [{protocol}:{port}]"
        )
        
        return False
    
    def add_policy(self, policy: NetworkPolicy):
        """Add custom segmentation policy"""
        self.policies.append(policy)
        self.logger.info(f"Added policy: {policy.name}")
    
    def remove_policy(self, policy_name: str):
        """Remove policy by name"""
        self.policies = [p for p in self.policies if p.name != policy_name]
        self.logger.info(f"Removed policy: {policy_name}")
    
    def get_zone_devices(self, zone: SecurityZone) -> List[str]:
        """Get all devices in a zone"""
        return [dev for dev, z in self.device_zones.items() if z == zone]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get segmentation metrics"""
        return {
            **self.metrics,
            "total_devices": len(self.device_zones),
            "zones": {
                zone.value: len(self.get_zone_devices(zone))
                for zone in SecurityZone
            },
            "lateral_movement_reduction_pct": (
                100 * self.metrics["lateral_movement_blocked"] / 
                max(1, self.metrics["packets_denied"])
            )
        }
