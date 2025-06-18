import os
from dotenv import load_dotenv
from typing import Optional, Union
from .destination import get_final_url

load_dotenv()

class AdtError(Exception):
    """Wraps ADT HTTP errors with status and message."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"ADT Error {status_code}: {message}")
        self.status_code = status_code

# Load global SAP connection settings once
SAP_URL       = os.getenv("SAP_URL")
SAP_CLIENT    = os.getenv("SAP_CLIENT")
SAP_USER      = os.getenv("SAP_USER")
SAP_PASS      = os.getenv("SAP_PASS")
SAP_AUTH_TYPE = os.getenv("SAP_AUTH_TYPE", "basic").lower()
SAP_JWT_TOKEN = os.getenv("SAP_JWT_TOKEN")
VERIFY_SSL    = os.getenv("SAP_VERIFY_SSL", "true").lower() == "true"

# Legacy timeout for backward compatibility
TIMEOUT       = int(os.getenv("SAP_TIMEOUT", "30"))

def get_timeout_config() -> dict:
    """Get timeout configuration from environment variables with fallback defaults."""
    default_timeout = int(os.getenv("SAP_TIMEOUT_DEFAULT", "45"))
    csrf_timeout    = int(os.getenv("SAP_TIMEOUT_CSRF", "15"))
    long_timeout    = int(os.getenv("SAP_TIMEOUT_LONG", "60"))
    return {
        "default": default_timeout,
        "csrf":    csrf_timeout,
        "long":    long_timeout
    }

def get_timeout(timeout_type: Union[str, int] = "default") -> int:
    """Get timeout value for specific operation type."""
    if isinstance(timeout_type, int):
        print(f"[DEBUG] Using custom numeric timeout: {timeout_type}s")
        return timeout_type

    config = get_timeout_config()
    timeout = config.get(timeout_type, config["default"])
    print(f"[DEBUG] Timeout for '{timeout_type}': {timeout}s")
    return timeout

def validate_configuration():
    """Validate authentication configuration before creating any session."""
    print("[DEBUG] Validating SAP configuration...")
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
    print(f"[DEBUG] Configuration validated: auth_type={SAP_AUTH_TYPE}, verify_ssl={VERIFY_SSL}")

def make_session(timeout_type: Union[str, int] = "default"):
    """
    Creates and configures a requests.Session for ADT calls using global settings.
    Supports both basic authentication and JWT token authentication.
    """
    import requests  # import lazily to avoid startup overhead

    print("[DEBUG] Entering make_session()")
    validate_configuration()

    session = requests.Session()
    session.verify = VERIFY_SSL
    session.timeout = get_timeout(timeout_type)
    print(f"[DEBUG] Session created: verify_ssl={session.verify}, timeout={session.timeout}s")

    if SAP_AUTH_TYPE == "jwt":
        print("[DEBUG] Setting up JWT authentication headers")
        session.headers.update({
            "Authorization": f"Bearer {SAP_JWT_TOKEN}",
            "Content-Type":  "application/xml",
            "Accept":        "application/xml"
        })
        print(f"[DEBUG] Headers: {session.headers}")
    else:
        print("[DEBUG] Setting up BASIC authentication")
        session.auth = (SAP_USER, SAP_PASS)
        session.params = {"sap-client": SAP_CLIENT}
        print(f"[DEBUG] Auth tuple: {session.auth}, params: {session.params}")

    print("[DEBUG] make_session() complete; returning session")
    return session

def make_session_with_timeout(timeout_type: Union[str, int] = "default"):
    """
    Simplified session creation using configurable timeouts.
    """
    print(f"[DEBUG] make_session_with_timeout() called with timeout_type={timeout_type}")
    return make_session(timeout_type)
