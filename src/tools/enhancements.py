# tools/enhancements.py

import base64
import re
from typing import Dict, List, Any, Optional
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for MCP function-calling
get_enhancements_definition = {
    "name": "get_enhancements",
    "description": "Retrieve enhancement implementations for ABAP programs/includes with auto-detection of object type.",
    "parameters": {
        "type": "object",
        "properties": {
            "object_name": {
                "type": "string",
                "description": "Name of the ABAP program or include (e.g. 'RSPARAM' or 'RSBTABSP')."
            },
            "program": {
                "type": "string",
                "description": "Optional manual program context for includes (if auto-detection fails)."
            }
        },
        "required": ["object_name"]
    }
}

class EnhancementImplementation:
    """Class representing an enhancement implementation."""
    def __init__(self, name: str, type_: str, source_code: Optional[str] = None, description: Optional[str] = None):
        self.name = name
        self.type = type_
        self.source_code = source_code
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "source_code": self.source_code,
            "description": self.description
        }

def _parse_enhancements_from_xml(xml_data: str) -> List[EnhancementImplementation]:
    """
    Parse enhancement XML to extract enhancement implementations with their source code.
    """
    enhancements = []
    
    try:
        # Extract <enh:source> elements which contain the base64 encoded enhancement source code
        source_regex = r'<enh:source[^>]*>([^<]*)</enh:source>'
        matches = re.finditer(source_regex, xml_data)
        
        index = 0
        for match in matches:
            enhancement = EnhancementImplementation(
                name=f"enhancement_{index + 1}",  # Default name if not found in attributes
                type_="enhancement"
            )
            
            # Try to find enhancement name and type from parent elements or attributes
            source_start = match.start()
            # Look backwards for parent enhancement element with name/type attributes
            before_source = xml_data[:source_start]
            
            name_match = re.search(r'adtcore:name="([^"]*)"[^>]*$', before_source)
            type_match = re.search(r'adtcore:type="([^"]*)"[^>]*$', before_source)
            
            if name_match and name_match.group(1):
                enhancement.name = name_match.group(1)
            
            if type_match and type_match.group(1):
                enhancement.type = type_match.group(1)
            
            # Extract and decode the base64 source code
            base64_source = match.group(1)
            if base64_source:
                try:
                    # Decode base64 source code
                    decoded_source = base64.b64decode(base64_source).decode('utf-8')
                    enhancement.source_code = decoded_source
                except Exception as decode_error:
                    print(f"Failed to decode source code for enhancement {enhancement.name}: {decode_error}")
                    enhancement.source_code = base64_source  # Keep original if decode fails
            
            enhancements.append(enhancement)
            index += 1
        
        print(f"Parsed {len(enhancements)} enhancement implementations")
        return enhancements
        
    except Exception as parse_error:
        print(f"Failed to parse enhancement XML: {parse_error}")
        return []

def _determine_object_type_and_path(object_name: str, manual_program_context: Optional[str] = None, session=None) -> Dict[str, Any]:
    """
    Determine if an object is a program or include and return appropriate URL path.
    """
    base_url = SAP_URL.rstrip('/')
    
    try:
        # First try as a program
        program_url = f"{base_url}/sap/bc/adt/programs/programs/{object_name}"
        try:
            response = session.get(
                program_url,
                params={"sap-client": SAP_CLIENT},
                headers={"Accept": "application/vnd.sap.adt.programs.v3+xml"}
            )
            if response.status_code == 200:
                print(f"{object_name} is a program")
                return {
                    "type": "program",
                    "base_path": f"/sap/bc/adt/programs/programs/{object_name}/source/main/enhancements/elements"
                }
        except Exception as program_error:
            print(f"{object_name} is not a program, trying as include...")
        
        # Try as include
        include_url = f"{base_url}/sap/bc/adt/programs/includes/{object_name}"
        response = session.get(
            include_url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "application/vnd.sap.adt.programs.includes.v2+xml"}
        )
        
        if response.status_code == 200:
            print(f"{object_name} is an include")
            
            context = None
            # Use manual program context if provided
            if manual_program_context:
                context = f"/sap/bc/adt/programs/programs/{manual_program_context}"
                print(f"Using manual program context for include {object_name}: {context}")
            else:
                # Auto-determine context from metadata
                xml_data = response.text
                context_match = re.search(r'include:contextRef[^>]+adtcore:uri="([^"]+)"', xml_data)
                if context_match and context_match.group(1):
                    context = context_match.group(1)
                    print(f"Found auto-determined context for include {object_name}: {context}")
                else:
                    raise AdtError(
                        400,
                        f"Could not determine parent program context for include: {object_name}. "
                        f"No contextRef found in metadata. Consider providing the 'program' parameter manually."
                    )
            
            return {
                "type": "include",
                "base_path": f"/sap/bc/adt/programs/includes/{object_name}/source/main/enhancements/elements",
                "context": context
            }
        
        raise AdtError(
            400,
            f"Could not determine object type for: {object_name}. "
            f"Object is neither a valid program nor include."
        )
        
    except Exception as error:
        if isinstance(error, AdtError):
            raise error
        print(f"Failed to determine object type for {object_name}: {error}")
        raise AdtError(
            400,
            f"Failed to determine object type for: {object_name}. {str(error)}"
        )

def get_enhancements(object_name: str, program: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve enhancement implementations for ABAP programs/includes.
    Automatically determines if object is a program or include and handles accordingly.
    """
    print(f"Getting enhancements for object: {object_name}")
    if program:
        print(f"With manual program context: {program}")
    
    if not object_name:
        raise ValueError("object_name is required")

    session = make_session()
    
    try:
        # Determine object type and get appropriate path and context
        object_info = _determine_object_type_and_path(object_name, program, session)
        
        # Build URL based on object type
        base_url = SAP_URL.rstrip('/')
        url = f"{base_url}{object_info['base_path']}"
        
        # Add context parameter only for includes
        if object_info["type"] == "include" and object_info.get("context"):
            url += f"?context={object_info['context']}"
            print(f"Using context for include: {object_info['context']}")
        
        print(f"Final enhancement URL: {url}")
        
        # Make the request
        response = session.get(
            url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "application/vnd.sap.adt.enhancement.v1+xml"}
        )
        
        response.raise_for_status()
        
        if response.status_code == 200 and response.text:
            # Parse the XML to extract enhancement implementations
            enhancements = _parse_enhancements_from_xml(response.text)
            
            enhancement_response = {
                "object_name": object_name,
                "object_type": object_info["type"],
                "context": object_info.get("context"),
                "enhancements": [enh.to_dict() for enh in enhancements],
                "enhancement_count": len(enhancements)
            }
            
            return enhancement_response
        else:
            raise AdtError(response.status_code, f"Failed to retrieve enhancements. Status: {response.status_code}")
            
    except HTTPError as e:
        if e.response.status_code == 404:
            raise AdtError(404, f"Enhancements not found for object '{object_name}'") from e
        raise AdtError(e.response.status_code, e.response.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error retrieving enhancements: {e}") from e
