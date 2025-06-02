import os
from dotenv import load_dotenv
from typing import Optional, Union

load_dotenv()

class AdtError(Exception):
    """Wraps ADT HTTP errors with status and message."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"ADT Error {status_code}: {message}")
        self.status_code = status_code

# Load global SAP connection settings once
SAP_URL    = os.getenv("SAP_URL")
SAP_CLIENT = os.getenv("SAP_CLIENT")
SAP_USER   = os.getenv("SAP_USER")
SAP_PASS   = os.getenv("SAP_PASS")
SAP_AUTH_TYPE = os.getenv("SAP_AUTH_TYPE", "basic").lower()
SAP_JWT_TOKEN = os.getenv("SAP_JWT_TOKEN")
VERIFY_SSL = os.getenv("SAP_VERIFY_SSL", "true").lower() == "true"

# Legacy timeout for backward compatibility
TIMEOUT    = int(os.getenv("SAP_TIMEOUT", "30"))

# Timeout configuration
def get_timeout_config() -> dict:
    """Get timeout configuration from environment variables with fallback defaults.
    
    Returns:
        dict: Dictionary with timeout values in seconds
    """
    default_timeout = int(os.getenv("SAP_TIMEOUT_DEFAULT", "45"))
    csrf_timeout = int(os.getenv("SAP_TIMEOUT_CSRF", "15"))
    long_timeout = int(os.getenv("SAP_TIMEOUT_LONG", "60"))
    
    return {
        "default": default_timeout,
        "csrf": csrf_timeout,
        "long": long_timeout
    }


def get_timeout(timeout_type: Union[str, int] = "default") -> int:
    """Get timeout value for specific operation type.
    
    Args:
        timeout_type: Type of operation ('default', 'csrf', 'long') or custom number
        
    Returns:
        int: Timeout value in seconds
    """
    if isinstance(timeout_type, int):
        return timeout_type
    
    config = get_timeout_config()
    return config.get(timeout_type, config["default"])


def validate_configuration():
    """
    Validate authentication configuration.
    Call this function before making SAP connections.
    """
    # Validate authentication configuration
    if SAP_AUTH_TYPE == "jwt":
        if not all([SAP_URL, SAP_JWT_TOKEN]):
            raise EnvironmentError(
                "For JWT authentication, please set SAP_URL and SAP_JWT_TOKEN environment variables"
            )
    elif SAP_AUTH_TYPE == "basic":
        if not all([SAP_URL, SAP_CLIENT, SAP_USER, SAP_PASS]):
            raise EnvironmentError(
                "For basic authentication, please set SAP_URL, SAP_CLIENT, SAP_USER, and SAP_PASS environment variables"
            )
    else:
        raise EnvironmentError(
            f"Unsupported authentication type: {SAP_AUTH_TYPE}. Supported types: 'basic', 'jwt'"
        )


def make_session(timeout_type: Union[str, int] = "default"):
    """
    Creates and configures a requests.Session for ADT calls using global settings.
    Supports both basic authentication and JWT token authentication.
    
    Args:
        timeout_type: Type of operation ('default', 'csrf', 'long') or custom number in seconds
    
    Note: This function imports requests only when needed to avoid import issues.
    """
    import requests  # Import only when needed
    
    # Validate configuration before creating session
    validate_configuration()
    
    session = requests.Session()
    session.verify = VERIFY_SSL
    session.timeout = get_timeout(timeout_type)
    
    if SAP_AUTH_TYPE == "jwt":
        # Use JWT token authentication
        session.headers.update({
            "Authorization": f"Bearer {SAP_JWT_TOKEN}",
            "Content-Type": "application/xml",
            "Accept": "application/xml"
        })
    else:
        # Use basic authentication (default)
        session.auth = (SAP_USER, SAP_PASS)
        session.params = {"sap-client": SAP_CLIENT}
    
    return session


def make_session_with_timeout(timeout_type: Union[str, int] = "default"):
    """
    Simplified session creation function that uses configurable timeouts.
    This is equivalent to the Node.js makeAdtRequestWithTimeout functionality.
    
    Args:
        timeout_type: Timeout type ('default', 'csrf', 'long') or custom number in seconds
        
    Returns:
        requests.Session: Configured session with appropriate timeout
    """
    return make_session(timeout_type)
