"""
Test script for BTP functionality in MCP-ADT project.
Tests JWT authentication, service key parsing, and .env generation.
"""

import os
import json
import tempfile
from src.tools.btp_utils import BtpServiceKey, generate_env_from_service_key
from src.tools.btp_tools import (
    parse_btp_service_key,
    generate_env_from_service_key_json,
    get_btp_connection_status
)


def test_service_key_parsing():
    """Test parsing of BTP service key."""
    print("=== Testing Service Key Parsing ===")
    
    # Sample service key structure (anonymized)
    sample_service_key = {
        "label": "abap-trial-service-broker",
        "credentials": {
            "url": "https://11b69711-9bcb-491b-b504-a9ba7e4b7e97.abap.us10.hana.ondemand.com",
            "username": "DEVELOPER",
            "password": "sample_password", 
            "uaa": {
                "url": "https://2dad4c07trial.authentication.us10.hana.ondemand.com",
                "clientid": "sb-e00a594f-c57f-4614-a75d-e8c475ed26a!b434325|abap-trial-service-broker!b3132",
                "clientsecret": "sample_secret"
            }
        }
    }
    
    try:
        service_key = BtpServiceKey(sample_service_key)
        print(f"✓ ABAP Endpoint: {service_key.abap_endpoint}")
        print(f"✓ OAuth URL: {service_key.oauth_url}")
        print(f"✓ Client ID: {service_key.client_id[:20]}...")
        print(f"✓ Has Client Secret: {bool(service_key.client_secret)}")
        print("✓ Service key parsing successful!")
        return True
    except Exception as e:
        print(f"✗ Service key parsing failed: {e}")
        return False


def test_env_generation():
    """Test .env file generation from service key."""
    print("\n=== Testing .env Generation ===")
    
    sample_service_key = {
        "credentials": {
            "url": "https://sample.abap.region.hana.ondemand.com",
            "uaa": {
                "url": "https://sample.authentication.region.hana.ondemand.com",
                "clientid": "sample-client-id",
                "clientsecret": "sample-secret"
            }
        }
    }
    
    try:
        service_key = BtpServiceKey(sample_service_key)
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Test basic auth generation (since JWT requires actual token endpoint)
        generate_env_from_service_key(
            service_key=service_key,
            username="test_user",
            password="test_pass",
            output_file=temp_path,
            use_jwt=False,  # Use basic auth for testing
            verify_ssl=True,
            timeout=30
        )
        
        # Read and verify generated file
        with open(temp_path, 'r') as f:
            content = f.read()
        
        print("Generated .env content:")
        print(content)
        
        # Cleanup
        os.unlink(temp_path)
        
        print("✓ .env file generation successful!")
        return True
        
    except Exception as e:
        print(f"✗ .env generation failed: {e}")
        return False


def test_mcp_tools():
    """Test MCP tool functions."""
    print("\n=== Testing MCP Tools ===")
    
    sample_json = json.dumps({
        "credentials": {
            "url": "https://sample.abap.region.hana.ondemand.com",
            "uaa": {
                "url": "https://sample.authentication.region.hana.ondemand.com",
                "clientid": "sample-client-id",
                "clientsecret": "sample-secret"
            }
        }
    })
    
    try:
        # Test service key parsing
        result = parse_btp_service_key(sample_json)
        print("Service key parsing result:")
        print(result)
        
        # Test connection status
        status = get_btp_connection_status()
        print("\nConnection status:")
        print(status)
        
        print("✓ MCP tools testing successful!")
        return True
        
    except Exception as e:
        print(f"✗ MCP tools testing failed: {e}")
        return False


def test_current_auth():
    """Test current authentication configuration."""
    print("\n=== Testing Current Authentication ===")
    
    try:
        from tools.utils import SAP_URL, SAP_AUTH_TYPE, VERIFY_SSL, TIMEOUT
        
        print(f"SAP URL: {SAP_URL}")
        print(f"Auth Type: {SAP_AUTH_TYPE}")
        print(f"Verify SSL: {VERIFY_SSL}")
        print(f"Timeout: {TIMEOUT}")
        
        if SAP_AUTH_TYPE == "jwt":
            from tools.utils import SAP_JWT_TOKEN
            print(f"Has JWT Token: {bool(SAP_JWT_TOKEN)}")
            if SAP_JWT_TOKEN:
                print(f"JWT Token (first 50 chars): {SAP_JWT_TOKEN[:50]}...")
        else:
            from tools.utils import SAP_CLIENT, SAP_USER, SAP_PASS
            print(f"Client: {SAP_CLIENT}")
            print(f"User: {SAP_USER}")
            print(f"Has Password: {bool(SAP_PASS)}")
        
        print("✓ Current authentication configuration loaded!")
        return True
        
    except Exception as e:
        print(f"✗ Authentication configuration test failed: {e}")
        return False


def main():
    """Run all BTP functionality tests."""
    print("MCP-ADT BTP Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_service_key_parsing,
        test_env_generation,
        test_mcp_tools,
        test_current_auth
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"✓ Passed: {sum(results)}")
    print(f"✗ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All BTP functionality tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
