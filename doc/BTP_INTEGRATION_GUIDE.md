# BTP (Business Technology Platform) Integration Guide

This document describes the BTP functionality added to the MCP-ADT project, including JWT authentication and utilities for generating .env files from BTP service keys.

## Overview

The BTP integration provides:

1. **JWT Token Authentication** - Support for BTP session token authentication
2. **Service Key Parsing** - Parse and analyze BTP service keys
3. **Automatic .env Generation** - Generate configuration files from service keys
4. **Dual Authentication Support** - Both basic auth (on-premise) and JWT (BTP)

## Configuration

### Authentication Types

The system supports two authentication methods:

#### Basic Authentication (On-Premise/Traditional)
```bash
SAP_AUTH_TYPE=basic
SAP_URL=https://your-sap-system.com:8000
SAP_CLIENT=100
SAP_USER=your_username
SAP_PASS=your_password
SAP_VERIFY_SSL=true
SAP_TIMEOUT=30
```

#### JWT Authentication (BTP)
```bash
SAP_AUTH_TYPE=jwt
SAP_URL=https://your-abap-system.abap.region.hana.ondemand.com
SAP_JWT_TOKEN=eyJhbGciOiJSUzI1NiIsImp...
SAP_VERIFY_SSL=true
SAP_TIMEOUT=30
```

## MCP Tools

### 1. generate_env_from_service_key_file_mcp

Generate .env file from a BTP service key file.

**Parameters:**
- `service_key_file` (string): Path to the BTP service key JSON file
- `username` (string): BTP username for authentication
- `password` (string): BTP password for authentication
- `output_file` (string, optional): Output .env file name (default: "btp_generated.env")
- `use_jwt` (boolean, optional): Use JWT authentication (default: true)
- `verify_ssl` (boolean, optional): Verify SSL certificates (default: true)
- `timeout` (integer, optional): Request timeout in seconds (default: 30)

**Example:**
```python
generate_env_from_service_key_file_mcp(
    service_key_file="my-service-key.json",
    username="myuser@company.com",
    password="mypassword",
    output_file="btp_production.env"
)
```

### 2. generate_env_from_service_key_json_mcp

Generate .env file from a BTP service key JSON string.

**Parameters:**
- `service_key_json` (string): BTP service key as JSON string
- `username` (string): BTP username for authentication
- `password` (string): BTP password for authentication
- `output_file` (string, optional): Output .env file name (default: "btp_generated.env")
- `use_jwt` (boolean, optional): Use JWT authentication (default: true)
- `verify_ssl` (boolean, optional): Verify SSL certificates (default: true)
- `timeout` (integer, optional): Request timeout in seconds (default: 30)

### 3. parse_btp_service_key_mcp

Parse and analyze a BTP service key to extract connection information.

**Parameters:**
- `service_key_input` (string): Either a file path to service key JSON or the JSON string itself

**Returns:** JSON object with parsed service key information including endpoints, client IDs, etc.

### 4. get_btp_connection_status_mcp

Check current BTP connection configuration and authentication status.

**Parameters:** None

**Returns:** JSON object with current configuration status.

## CLI Utility

### btp_env_generator.py

A standalone command-line utility for generating .env files from BTP service keys.

#### Basic Usage

```bash
# Generate from service key file
python btp_env_generator.py --service-key service-key.json --username myuser --prompt-password

# Generate from JSON string
python btp_env_generator.py --service-key-json '{"credentials": {...}}' --username myuser --password mypass

# Use basic auth instead of JWT
python btp_env_generator.py --service-key service-key.json --username myuser --no-jwt --prompt-password

# Specify output file
python btp_env_generator.py --service-key service-key.json --username myuser --output my-btp.env --prompt-password
```

#### Command Line Options

- `--service-key, -k`: Path to BTP service key JSON file
- `--service-key-json, -j`: BTP service key as JSON string
- `--username, -u`: BTP username for authentication
- `--password, -p`: BTP password for authentication
- `--prompt-password`: Prompt for password interactively (more secure)
- `--output, -o`: Output .env file name (default: btp_generated.env)
- `--no-jwt`: Use basic authentication instead of JWT
- `--no-ssl-verify`: Disable SSL certificate verification
- `--timeout`: Request timeout in seconds (default: 30)

## Service Key Structure

BTP service keys should have the following structure:

```json
{
  "label": "abap-trial-service-broker",
  "credentials": {
    "url": "https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.abap.region.hana.ondemand.com",
    "username": "DEVELOPER",
    "password": "user_password",
    "uaa": {
      "url": "https://subdomain.authentication.region.hana.ondemand.com",
      "clientid": "sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!bxxxxxx|abap-trial-service-broker!bxxxx",
      "clientsecret": "client_secret_value"
    }
  }
}
```

## Authentication Flow

### JWT Authentication Process

1. **Service Key Parsing**: Extract OAuth endpoint and client credentials
2. **Token Request**: Use OAuth2 password flow to obtain JWT token
3. **Token Usage**: Include JWT token in Authorization header for API calls
4. **Token Refresh**: Automatically refresh tokens when needed

### Basic Authentication Process

1. **Direct Authentication**: Use username/password for each API call
2. **Client Parameter**: Include SAP client number in requests (for on-premise)

## Error Handling

The BTP utilities include comprehensive error handling:

- **Invalid Service Keys**: Clear error messages for malformed JSON or missing fields
- **Authentication Failures**: Detailed error reporting for OAuth and credential issues
- **Network Errors**: Timeout and SSL verification error handling
- **File Operations**: File not found and permission error handling

## Security Considerations

1. **Password Handling**: Use `--prompt-password` for interactive password entry
2. **Token Storage**: JWT tokens in .env files should be treated as sensitive
3. **Service Key Protection**: Keep service key files secure and never commit to version control
4. **SSL Verification**: Keep SSL verification enabled unless absolutely necessary

## Testing

Run the BTP functionality tests:

```bash
python test_btp_features.py
```

This will test:
- Service key parsing
- .env file generation
- MCP tool functions
- Current authentication configuration

## Troubleshooting

### Common Issues

1. **JWT Token Expired**: Regenerate .env file with fresh token
2. **SSL Certificate Errors**: Use `--no-ssl-verify` for testing (not recommended for production)
3. **Service Key Format**: Ensure service key JSON is properly formatted
4. **Network Connectivity**: Check firewall and proxy settings for BTP endpoints

### Debug Steps

1. Check connection status: Use `get_btp_connection_status_mcp()`
2. Parse service key first: Use `parse_btp_service_key_mcp()` to verify format
3. Test basic auth fallback: Set `use_jwt=False` for troubleshooting
4. Verify endpoints: Ensure BTP system URLs are accessible

## Integration Examples

### Example 1: Generate .env from Downloaded Service Key

```bash
# Download service key from BTP cockpit as service-key.json
python btp_env_generator.py --service-key service-key.json --username myuser@company.com --prompt-password --output production.env
```

### Example 2: Use in MCP Tool

```python
# Parse service key to understand structure
result = parse_btp_service_key_mcp("service-key.json")
print(result)

# Generate .env file with specific settings
generate_env_from_service_key_file_mcp(
    service_key_file="service-key.json",
    username="developer@company.com",
    password="secure_password",
    output_file="btp_dev.env",
    use_jwt=True,
    verify_ssl=True
)

# Check final configuration
status = get_btp_connection_status_mcp()
print(status)
```

## Migration from TypeScript

This Python implementation provides equivalent functionality to the TypeScript version with:

- **Enhanced Error Handling**: More detailed error messages and validation
- **CLI Utility**: Standalone command-line tool for .env generation
- **MCP Integration**: Native integration with MCP server tools
- **Flexible Authentication**: Support for both JWT and basic authentication
- **Comprehensive Testing**: Full test suite for all BTP functionality
