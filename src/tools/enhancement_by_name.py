# tools/enhancement_by_name.py

import base64
import re
from typing import Dict, Any, Optional
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session_with_timeout, SAP_URL, SAP_CLIENT

# JSON schema for MCP function-calling
get_enhancement_by_name_definition = {
    "name": "get_enhancement_by_name",
    "description": "📝 ENHANCEMENT BY NAME: Retrieve source code of a specific enhancement implementation by its name and enhancement spot. Use this when you know the exact enhancement spot and implementation name.",
    "parameters": {
        "type": "object",
        "properties": {
            "enhancement_spot": {
                "type": "string",
                "description": "Name of the enhancement spot (e.g., 'enhoxhh')"
            },
            "enhancement_name": {
                "type": "string",
                "description": "Name of the specific enhancement implementation (e.g., 'zpartner_update_pai')"
            }
        },
        "required": ["enhancement_spot", "enhancement_name"]
    }
}

def _parse_enhancement_source_from_xml(xml_data: str) -> str:
    """
    Parses enhancement source XML to extract the source code.
    
    Args:
        xml_data: Raw XML response from ADT
        
    Returns:
        Decoded source code
    """
    try:
        # Look for source code in various possible formats
        
        # Try to find base64 encoded source in <source> or similar tags
        base64_source_regex = r'<(?:source|enh:source)[^>]*>([^<]*)</(?:source|enh:source)>'
        base64_match = re.search(base64_source_regex, xml_data)
        
        if base64_match and base64_match.group(1):
            try:
                # Decode base64 source code
                decoded_source = base64.b64decode(base64_match.group(1)).decode('utf-8')
                return decoded_source
            except Exception as decode_error:
                print(f'Failed to decode base64 source code: {decode_error}')
        
        # Try to find plain text source code
        text_source_regex = r'<(?:source|enh:source)[^>]*>\s*<!\[CDATA\[(.*?)\]\]>\s*</(?:source|enh:source)>'
        text_match = re.search(text_source_regex, xml_data, re.DOTALL)
        
        if text_match and text_match.group(1):
            return text_match.group(1)
        
        # If no specific source tags found, return the entire XML as fallback
        print('Could not find source code in expected format, returning raw XML')
        return xml_data
        
    except Exception as parse_error:
        print(f'Failed to parse enhancement source XML: {parse_error}')
        return xml_data  # Return raw XML as fallback

def get_enhancement_by_name(enhancement_spot: str, enhancement_name: str) -> Dict[str, Any]:
    """
    Retrieve a specific enhancement implementation by name.
    Uses the ADT API endpoint for reading enhancement source code directly.
    
    Args:
        enhancement_spot: Name of the enhancement spot (e.g., 'enhoxhh')
        enhancement_name: Name of the specific enhancement implementation (e.g., 'zpartner_update_pai')
        
    Returns:
        Dictionary with enhancement source code and metadata
    """
    print(f"Getting enhancement: {enhancement_name} from spot: {enhancement_spot}")
    
    if not enhancement_spot:
        raise ValueError("enhancement_spot is required")
    
    if not enhancement_name:
        raise ValueError("enhancement_name is required")
    
    try:
        # Build the ADT URL for the specific enhancement
        # Format: /sap/bc/adt/enhancements/{enhancement_spot}/{enhancement_name}/source/main
        base_url = SAP_URL.rstrip('/')
        url = f"{base_url}/sap/bc/adt/enhancements/{enhancement_spot}/{enhancement_name}/source/main"
        
        print(f"Enhancement URL: {url}")
        
        # Make the request with default timeout
        session = make_session_with_timeout("default")
        response = session.get(
            url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "application/vnd.sap.adt.enhancement.v1+xml"}
        )
        
        response.raise_for_status()
        
        if response.status_code == 200 and response.text:
            # Parse the XML to extract source code
            source_code = _parse_enhancement_source_from_xml(response.text)
            
            enhancement_response = {
                "enhancement_spot": enhancement_spot,
                "enhancement_name": enhancement_name,
                "source_code": source_code,
                "raw_xml": response.text  # Include raw XML for debugging if needed
            }
            
            return enhancement_response
        else:
            raise AdtError(
                response.status_code,
                f"Failed to retrieve enhancement {enhancement_name} from spot {enhancement_spot}. Status: {response.status_code}"
            )
            
    except HTTPError as e:
        if e.response.status_code == 404:
            raise AdtError(404, f"Enhancement '{enhancement_name}' not found in spot '{enhancement_spot}'") from e
        raise AdtError(e.response.status_code, e.response.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error retrieving enhancement: {e}") from e
    except Exception as e:
        raise ConnectionError(f"Error retrieving enhancement: {e}") from e
