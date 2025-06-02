# tools/search_objects.py

import xml.etree.ElementTree as ET
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

get_search_objects_definition = {
    "name": "get_search_objects",
    "description": "Perform a quick ADT object search and return matching repository objects.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search string, wildcard allowed (e.g. 'ZCL_' or 'ZCL_*')."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return.",
                "default": 100
            }
        },
        "required": ["query"]
    }
}

def get_search_objects(
    query: str,
    max_results: int = 100
) -> list[dict]:
    """
    Executes a quickSearch via the ADT Search API and returns a list of matching objects.
    Each dict contains: objectName, objectType, packageName, and uri.

    - Ensures exactly one trailing '*' wildcard.
    - Tries 'application/vnd.sap.adt.search.v2+xml' first; on 406 retries with NO Accept header.
    - Raises AdtError on HTTP errors; ConnectionError on network failures.
    """
    print(f"Searching for objects matching '{query}'")  
    if not query:
        raise ValueError("query is required")

    pattern = query.rstrip('*') + '*'
    session = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = f"{base}/sap/bc/adt/repository/informationsystem/search"
    params   = {
        "sap-client": SAP_CLIENT,
        "operation":  "quickSearch",
        "query":      pattern,
        "maxResults": str(max_results)
    }

    # 1) Preferred media type
    resp = session.get(
        endpoint,
        params=params,
        headers={"Accept": "application/vnd.sap.adt.search.v2+xml"}
    )

    # 2) If not acceptable, retry without any Accept header
    if resp.status_code == 406:
        resp = session.get(endpoint, params=params)

    # 3) Error handling
    try:
        resp.raise_for_status()
    except HTTPError as e:
        raise AdtError(resp.status_code, resp.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error during search: {e}") from e
    
    # 4) Parse the XML with proper namespace handling
    ns = {"adtcore": "http://www.sap.com/adt/core"}
    
    # Create the fully qualified attribute names with namespace
    uri_attr = "{http://www.sap.com/adt/core}uri"
    type_attr = "{http://www.sap.com/adt/core}type"
    name_attr = "{http://www.sap.com/adt/core}name"
    package_attr = "{http://www.sap.com/adt/core}packageName"
    desc_attr = "{http://www.sap.com/adt/core}description"
    
    root = ET.fromstring(resp.text)
    results = []
    
    # Find all objectReference elements
    for obj_ref in root.findall(".//adtcore:objectReference", ns):
        # Extract attributes using their fully qualified names
        results.append({
            "objectName": obj_ref.attrib.get(name_attr),
            "objectType": obj_ref.attrib.get(type_attr),
            "packageName": obj_ref.attrib.get(package_attr),
            "uri": obj_ref.attrib.get(uri_attr),
            "description": obj_ref.attrib.get(desc_attr)  # Added description
        })
    
    return results