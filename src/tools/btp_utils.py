"""
BTP (Business Technology Platform) utilities for SAP authentication and configuration.
Provides functionality to parse BTP service keys and generate .env files.
"""

import json
import os
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class BtpServiceKey:
    """Represents a BTP service key with authentication capabilities."""
    
    def __init__(self, service_key_data: Dict[str, Any]):
        """
        Initialize BTP service key from parsed JSON data.
        
        Args:
            service_key_data: Dictionary containing service key information
        """
        self.data = service_key_data
        self.credentials = service_key_data.get("credentials", {})
        
    @classmethod
    def from_json_file(cls, file_path: str) -> "BtpServiceKey":
        """Load service key from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)
    
    @classmethod
    def from_json_string(cls, json_string: str) -> "BtpServiceKey":
        """Load service key from JSON string."""
        data = json.loads(json_string)
        return cls(data)
    
    @property
    def abap_endpoint(self) -> str:
        """Get the ABAP system endpoint URL."""
        # Support both service key format and destination format
        if "credentials" in self.data:
            # Standard BTP service key format
            return self.credentials.get("url", "")
        else:
            # Destination format (like sk.json)
            return self.data.get("url", "") or self.data.get("endpoints", {}).get("abap", "")
    
    @property
    def oauth_url(self) -> str:
        """Get the OAuth2 token endpoint URL."""
        # Support both service key format and destination format
        if "credentials" in self.data:
            # Standard BTP service key format
            return self.credentials.get("uaa", {}).get("url", "")
        else:
            # Destination format (like sk.json)
            return self.data.get("uaa", {}).get("url", "")
    
    @property
    def client_id(self) -> str:
        """Get the OAuth2 client ID."""
        # Support both service key format and destination format
        if "credentials" in self.data:
            # Standard BTP service key format
            return self.credentials.get("uaa", {}).get("clientid", "")
        else:
            # Destination format (like sk.json)
            return self.data.get("uaa", {}).get("clientid", "")
    
    @property
    def client_secret(self) -> str:
        """Get the OAuth2 client secret."""
        # Support both service key format and destination format
        if "credentials" in self.data:
            # Standard BTP service key format
            return self.credentials.get("uaa", {}).get("clientsecret", "")
        else:
            # Destination format (like sk.json)
            return self.data.get("uaa", {}).get("clientsecret", "")
    
    @property
    def username(self) -> Optional[str]:
        """Get username if available in credentials."""
        return self.credentials.get("username")
    
    @property
    def password(self) -> Optional[str]:
        """Get password if available in credentials."""
        return self.credentials.get("password")


class BtpTokenManager:
    """Manages JWT token authentication for BTP services."""
    
    def __init__(self, service_key: BtpServiceKey, username: str, password: str):
        """
        Initialize token manager with service key and user credentials.
        
        Args:
            service_key: BTP service key instance
            username: BTP user username
            password: BTP user password
        """
        self.service_key = service_key
        self.username = username
        self.password = password
        self._token = None
        self._token_expiry = None
    
    def get_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid JWT token, refreshing if necessary.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Valid JWT token string
        """
        if force_refresh or not self._is_token_valid():
            self._refresh_token()
        return self._token
    
    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._token:
            return False
        
        # For simplicity, we'll refresh tokens proactively
        # In production, you'd decode the JWT and check expiry
        return False
    
    def _refresh_token(self) -> None:
        """Refresh the JWT token using OAuth2 flow."""
        token_url = urljoin(self.service_key.oauth_url, "/oauth/token")
        
        auth = (self.service_key.client_id, self.service_key.client_secret)
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(token_url, auth=auth, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._token = token_data["access_token"]


def generate_env_from_service_key(
    service_key: BtpServiceKey,
    username: str,
    password: str,
    output_file: str,
    use_jwt: bool = True,
    verify_ssl: bool = True,
    timeout: int = 30
) -> None:
    """
    Generate a .env file from BTP service key.
    
    Args:
        service_key: BTP service key instance
        username: BTP username for authentication
        password: BTP password for authentication
        output_file: Path to output .env file
        use_jwt: Whether to use JWT authentication (True) or basic auth (False)
        verify_ssl: Whether to verify SSL certificates
        timeout: Request timeout in seconds
    """
    env_content = []
    
    # Basic connection settings
    env_content.append(f"SAP_URL={service_key.abap_endpoint}")
    env_content.append(f"SAP_VERIFY_SSL={str(verify_ssl).lower()}")
    env_content.append(f"SAP_TIMEOUT={timeout}")
    
    if use_jwt:
        # JWT authentication setup
        env_content.append("SAP_AUTH_TYPE=jwt")
        
        # Get JWT token
        try:
            token_manager = BtpTokenManager(service_key, username, password)
            jwt_token = token_manager.get_token()
            env_content.append(f"SAP_JWT_TOKEN={jwt_token}")
        except Exception as e:
            print(f"Warning: Could not obtain JWT token: {e}")
            print("Falling back to basic authentication configuration...")
            use_jwt = False
    
    if not use_jwt:
        # Basic authentication setup
        env_content.append("SAP_AUTH_TYPE=basic")
        env_content.append(f"SAP_USER={username}")
        env_content.append(f"SAP_PASS={password}")
        # Note: SAP_CLIENT would need to be provided separately for on-premise systems
        env_content.append("# SAP_CLIENT=100  # Add client number for on-premise systems")
    
    # Additional BTP-specific settings
    env_content.extend([
        "",
        "# BTP Service Key Information (for reference)",
        f"# OAuth URL: {service_key.oauth_url}",
        f"# Client ID: {service_key.client_id}",
        "# Client Secret: [REDACTED]",
        ""
    ])
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_content))
    
    print(f"Generated .env file: {output_file}")
    print(f"Authentication type: {'JWT' if use_jwt else 'Basic'}")


def parse_service_key_file(file_path: str) -> BtpServiceKey:
    """
    Parse a BTP service key file and return a BtpServiceKey instance.
    
    Args:
        file_path: Path to the service key JSON file
        
    Returns:
        BtpServiceKey instance
    """
    return BtpServiceKey.from_json_file(file_path)


def parse_service_key_string(json_string: str) -> BtpServiceKey:
    """
    Parse a BTP service key JSON string and return a BtpServiceKey instance.
    
    Args:
        json_string: Service key as JSON string
        
    Returns:
        BtpServiceKey instance
    """
    return BtpServiceKey.from_json_string(json_string)
