"""
Zero Trust Authenticator
Implements continuous authentication and authorization for IoT devices
"""

import jwt
import time
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
import secrets


@dataclass
class AuthContext:
    """Authentication context for a device"""
    device_id: str
    device_type: str
    auth_method: str  # "jwt", "mtls", "oauth"
    auth_time: datetime
    expires_at: datetime
    trust_score: float  # 0-100
    behavior_normal: bool
    location_verified: bool
    certificate_valid: bool
    
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at
    
    def is_trusted(self, min_trust_score: float = 70.0) -> bool:
        return (
            not self.is_expired() and
            self.trust_score >= min_trust_score and
            self.behavior_normal and
            self.certificate_valid
        )


class ZeroTrustAuthenticator:
    """
    Zero Trust authentication and authorization system
    Implements continuous authentication with trust scoring
    """
    
    def __init__(
        self,
        jwt_secret: str = None,
        token_lifetime_minutes: int = 5,
        ca_cert_path: Optional[str] = None
    ):
        self.logger = logging.getLogger("ZeroTrustAuth")
        
        # JWT configuration
        self.jwt_secret = jwt_secret or secrets.token_hex(32)
        self.token_lifetime = timedelta(minutes=token_lifetime_minutes)
        
        # CA certificate for mTLS
        self.ca_cert = None
        if ca_cert_path:
            with open(ca_cert_path, 'rb') as f:
                self.ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        
        # Active authentication contexts
        self.auth_contexts: Dict[str, AuthContext] = {}
        
        # Trust scoring parameters
        self.trust_decay_rate = 0.1  # Trust degrades over time
        self.anomaly_penalty = 20.0  # Trust penalty for anomalies
        
        # Metrics
        self.metrics = {
            "auth_attempts": 0,
            "auth_success": 0,
            "auth_failures": 0,
            "token_refreshes": 0,
            "trust_violations": 0,
            "mtls_verifications": 0,
            "continuous_auth_checks": 0
        }
    
    def authenticate_device(
        self,
        device_id: str,
        device_type: str,
        credentials: Dict[str, Any],
        method: str = "jwt"
    ) -> Optional[str]:
        """
        Authenticate device and issue token
        
        Returns:
            JWT token if successful, None otherwise
        """
        self.metrics["auth_attempts"] += 1
        
        try:
            # Verify credentials based on method
            if method == "jwt":
                verified = self._verify_jwt_credentials(device_id, credentials)
            elif method == "mtls":
                verified = self._verify_mtls_certificate(credentials.get("certificate"))
            elif method == "oauth":
                verified = self._verify_oauth_token(credentials.get("token"))
            else:
                self.logger.error(f"Unknown auth method: {method}")
                self.metrics["auth_failures"] += 1
                return None
            
            if not verified:
                self.metrics["auth_failures"] += 1
                self.logger.warning(f"Authentication failed for {device_id}")
                return None
            
            # Create authentication context
            auth_time = datetime.utcnow()
            auth_context = AuthContext(
                device_id=device_id,
                device_type=device_type,
                auth_method=method,
                auth_time=auth_time,
                expires_at=auth_time + self.token_lifetime,
                trust_score=100.0,  # Start with full trust
                behavior_normal=True,
                location_verified=True,  # Simplified for simulation
                certificate_valid=True if method == "mtls" else True
            )
            
            self.auth_contexts[device_id] = auth_context
            
            # Generate JWT token
            token_payload = {
                "device_id": device_id,
                "device_type": device_type,
                "auth_method": method,
                "iat": int(auth_time.timestamp()),
                "exp": int((auth_time + self.token_lifetime).timestamp()),
                "trust_score": auth_context.trust_score
            }
            
            token = jwt.encode(token_payload, self.jwt_secret, algorithm="HS256")
            
            self.metrics["auth_success"] += 1
            self.logger.info(f"Device {device_id} authenticated via {method}")
            
            return token
            
        except Exception as e:
            self.metrics["auth_failures"] += 1
            self.logger.error(f"Authentication error: {e}")
            return None
    
    def _verify_jwt_credentials(self, device_id: str, credentials: Dict) -> bool:
        """Verify JWT credentials (simplified for simulation)"""
        # In production: verify against device registry, check API keys, etc.
        return "device_key" in credentials
    
    def _verify_mtls_certificate(self, cert_pem: Optional[bytes]) -> bool:
        """Verify mTLS certificate"""
        if not cert_pem or not self.ca_cert:
            return False
        
        try:
            self.metrics["mtls_verifications"] += 1
            
            # Load device certificate
            device_cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
            
            # Verify certificate is not expired
            now = datetime.utcnow()
            if now < device_cert.not_valid_before or now > device_cert.not_valid_after:
                return False
            
            # In production: verify signature chain with CA
            # For simulation, accept all non-expired certs
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate verification failed: {e}")
            return False
    
    def _verify_oauth_token(self, token: Optional[str]) -> bool:
        """Verify OAuth token (simplified)"""
        # In production: verify with OAuth provider
        return token is not None and len(token) > 0
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
    
    def continuous_authentication_check(
        self,
        device_id: str,
        behavior_data: Dict[str, Any]
    ) -> bool:
        """
        Perform continuous authentication check
        Updates trust score based on device behavior
        
        Returns:
            True if device still trusted, False if trust violated
        """
        self.metrics["continuous_auth_checks"] += 1
        
        context = self.auth_contexts.get(device_id)
        if not context:
            self.logger.warning(f"No auth context for {device_id}")
            return False
        
        # Check if token expired
        if context.is_expired():
            self.logger.warning(f"Auth expired for {device_id}")
            return False
        
        # Update trust score based on behavior
        anomaly_detected = behavior_data.get("anomaly_score", 0) > 0.5
        
        if anomaly_detected:
            context.trust_score -= self.anomaly_penalty
            context.behavior_normal = False
            self.logger.warning(
                f"Anomaly detected for {device_id}, trust score: {context.trust_score}"
            )
        else:
            # Gradual trust decay over time (requires re-auth)
            time_since_auth = (datetime.utcnow() - context.auth_time).total_seconds()
            decay = self.trust_decay_rate * (time_since_auth / 60)  # Per minute
            context.trust_score = max(0, context.trust_score - decay)
        
        # Check trust threshold
        trusted = context.is_trusted(min_trust_score=70.0)
        
        if not trusted:
            self.metrics["trust_violations"] += 1
            self.logger.warning(
                f"Trust violation for {device_id}: score={context.trust_score}"
            )
        
        return trusted
    
    def refresh_token(self, device_id: str) -> Optional[str]:
        """Refresh authentication token"""
        context = self.auth_contexts.get(device_id)
        
        if not context:
            return None
        
        # Only refresh if device is trusted
        if not context.is_trusted(min_trust_score=70.0):
            return None
        
        # Update expiration
        auth_time = datetime.utcnow()
        context.auth_time = auth_time
        context.expires_at = auth_time + self.token_lifetime
        
        # Generate new token
        token_payload = {
            "device_id": device_id,
            "device_type": context.device_type,
            "auth_method": context.auth_method,
            "iat": int(auth_time.timestamp()),
            "exp": int(context.expires_at.timestamp()),
            "trust_score": context.trust_score
        }
        
        token = jwt.encode(token_payload, self.jwt_secret, algorithm="HS256")
        
        self.metrics["token_refreshes"] += 1
        self.logger.info(f"Token refreshed for {device_id}")
        
        return token
    
    def revoke_authentication(self, device_id: str):
        """Revoke device authentication"""
        if device_id in self.auth_contexts:
            del self.auth_contexts[device_id]
            self.logger.warning(f"Authentication revoked for {device_id}")
    
    def get_trust_score(self, device_id: str) -> Optional[float]:
        """Get current trust score for device"""
        context = self.auth_contexts.get(device_id)
        return context.trust_score if context else None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get authentication metrics"""
        return {
            **self.metrics,
            "active_sessions": len(self.auth_contexts),
            "auth_success_rate": (
                100 * self.metrics["auth_success"] / 
                max(1, self.metrics["auth_attempts"])
            ),
            "avg_trust_score": (
                sum(c.trust_score for c in self.auth_contexts.values()) / 
                max(1, len(self.auth_contexts))
            )
        }
