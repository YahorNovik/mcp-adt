"""
BTP-specific MCP tools for service key parsing and .env generation.
"""

from src.tools.btp_utils import (
    parse_service_key_file,
    parse_service_key_string,
    generate_env_from_service_key,
    BtpServiceKey
)
import json
import os


def generate_env_from_service_key_file(
    service_key_file: str,
    username: str,
    password: str,
    output_file: str = "btp_generated.env",
    use_jwt: bool = True,
    verify_ssl: bool = True,
    timeout: int = 30
) -> str:
    """
    Generate .env file from BTP service key file.
    
    Args:
        service_key_file: Path to the BTP service key JSON file
        username: BTP username for authentication
        password: BTP password for authentication  
        output_file: Output .env file name (default: btp_generated.env)
        use_jwt: Use JWT authentication (default: True)
        verify_ssl: Verify SSL certificates (default: True)
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        Success message with file location
    """
    try:
        service_key = parse_service_key_file(service_key_file)
        generate_env_from_service_key(
            service_key=service_key,
            username=username,
            password=password,
            output_file=output_file,
            use_jwt=use_jwt,
            verify_ssl=verify_ssl,
            timeout=timeout
        )
        return f"Successfully generated .env file: {output_file}"
    except Exception as e:
        return f"Error generating .env file: {str(e)}"


def generate_env_from_service_key_json(
    service_key_json: str,
    username: str,
    password: str,
    output_file: str = "btp_generated.env",
    use_jwt: bool = True,
    verify_ssl: bool = True,
    timeout: int = 30
) -> str:
    """
    Generate .env file from BTP service key JSON string.
    
    Args:
        service_key_json: BTP service key as JSON string
        username: BTP username for authentication
        password: BTP password for authentication
        output_file: Output .env file name (default: btp_generated.env)
        use_jwt: Use JWT authentication (default: True)
        verify_ssl: Verify SSL certificates (default: True)
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        Success message with file location
    """
    try:
        service_key = parse_service_key_string(service_key_json)
        generate_env_from_service_key(
            service_key=service_key,
            username=username,
            password=password,
            output_file=output_file,
            use_jwt=use_jwt,
            verify_ssl=verify_ssl,
            timeout=timeout
        )
        return f"Successfully generated .env file: {output_file}"
    except Exception as e:
        return f"Error generating .env file: {str(e)}"


def parse_btp_service_key(service_key_input: str) -> str:
    """
    Parse and analyze a BTP service key (file path or JSON string).
    
    Args:
        service_key_input: Either a file path to service key JSON or the JSON string itself
        
    Returns:
        Parsed service key information
    """
    try:
        # Try to parse as file path first
        if os.path.isfile(service_key_input):
            service_key = parse_service_key_file(service_key_input)
            source = f"file: {service_key_input}"
        else:
            # Try to parse as JSON string
            service_key = parse_service_key_string(service_key_input)
            source = "JSON string"
        
        # Extract key information
        info = {
            "source": source,
            "abap_endpoint": service_key.abap_endpoint,
            "oauth_url": service_key.oauth_url,
            "client_id": service_key.client_id,
            "has_client_secret": bool(service_key.client_secret),
            "has_username": bool(service_key.username),
            "has_password": bool(service_key.password)
        }
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        return f"Error parsing service key: {str(e)}"


def get_btp_connection_status() -> str:
    """
    Check current BTP connection configuration and status.
    
    Returns:
        Current BTP configuration status
    """
    try:
        from src.tools.utils import SAP_URL, SAP_AUTH_TYPE, SAP_JWT_TOKEN, SAP_USER, VERIFY_SSL, TIMEOUT
        
        status = {
            "sap_url": SAP_URL,
            "auth_type": SAP_AUTH_TYPE,
            "verify_ssl": VERIFY_SSL,
            "timeout": TIMEOUT,
            "has_jwt_token": bool(SAP_JWT_TOKEN) if SAP_AUTH_TYPE == "jwt" else "N/A",
            "has_basic_auth": bool(SAP_USER) if SAP_AUTH_TYPE == "basic" else "N/A"
        }
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return f"Error checking BTP connection status: {str(e)}"
