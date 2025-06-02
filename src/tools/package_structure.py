import xmltodict
import time
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT, SAP_AUTH_TYPE

# JSON schema for Gemini function‐calling
get_package_structure_definition = {
    "name": "get_package_structure",
    "description": "Retrieve the list of objects in an ABAP package via the ADT repository nodestructure service.",
    "parameters": {
        "type": "object",
        "properties": {
            "package_name": {
                "type": "string",
                "description": "Name of the ABAP package (e.g. 'ZMY_PACKAGE')."
            }
        },
        "required": ["package_name"]
    }
}

def get_package_structure(package_name: str) -> list[dict]:
    """
    Fetches the structure (objects) under an ABAP package via ADT.
    
    Working version using requests automatic cookie handling.
    Fixed the cookie issue: use only cookie values without path, secure, HttpOnly attributes.
    
    Args:
        package_name: Name of the ABAP package (e.g. 'ZMY_PACKAGE')
    
    Returns:
        List of dictionaries with keys: OBJECT_TYPE, OBJECT_NAME, OBJECT_DESCRIPTION, OBJECT_URI
    
    Raises:
        ValueError: If package_name is empty
        AdtError: On HTTP errors
        ConnectionError: On network failures
    """
    print(f"Fetching package structure for {package_name}")
    if not package_name:
        raise ValueError("package_name is required")

    session = make_session()
    base_url = SAP_URL.rstrip('/')
    endpoint = f"{base_url}/sap/bc/adt/repository/nodestructure"
    
    params = {
        "parent_type": "DEVC/K",
        "parent_name": package_name,
        "withShortDescriptions": True
    }
    
    headers = {
        "Accept": "application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.RepositoryObjectTreeContent"
    }
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    
    try:
        # Отримуємо CSRF токен
        csrf_url = f"{base_url}/sap/bc/adt/discovery"
        csrf_resp = session.get(
            csrf_url,
            headers={"x-csrf-token": "fetch", "Accept": "application/atomsvc+xml"},
            timeout=10
        )
        
        token = csrf_resp.headers.get("x-csrf-token")
        print(f"CSRF token: {token}")
        
        if not token:
            raise ConnectionError("No CSRF token in response headers")
        
        headers_with_csrf = headers.copy()
        headers_with_csrf["x-csrf-token"] = token
        
        # КЛЮЧОВЕ ВИПРАВЛЕННЯ: Використовуємо requests автоматичні cookies 
        # (БЕЗ атрибутів path, secure, HttpOnly)
        if session.cookies:
            auto_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
            headers_with_csrf["Cookie"] = auto_cookies
            print(f"Auto cookies: {len(auto_cookies)} chars")
        
        # Add client header if needed
        if SAP_CLIENT:
            headers_with_csrf["X-SAP-Client"] = SAP_CLIENT
        
        print(f"Headers: {list(headers_with_csrf.keys())}")
        
        # POST запит
        resp = session.post(
            endpoint,
            params=params,
            headers=headers_with_csrf,
            timeout=30
        )
        
        print(f"Response status: {resp.status_code}")
        print(f"Response content-type: {resp.headers.get('content-type')}")
        print(f"Response length: {len(resp.text)}")
        
        if resp.status_code != 200:
            if resp.status_code == 404:
                raise AdtError(404, f"Package '{package_name}' not found")
            elif resp.status_code == 403:
                raise AdtError(403, f"Access forbidden: {resp.text}")
            else:
                raise AdtError(resp.status_code, f"HTTP {resp.status_code}: {resp.text}")
        
        print("Successfully received response!")
        
        # Парсимо XML
        print(f"Parsing XML response...")
        doc = xmltodict.parse(resp.text)
        nodes = (
            doc.get("asx:abap", {})
               .get("asx:values", {})
               .get("DATA", {})
               .get("TREE_CONTENT", {})
               .get("SEU_ADT_REPOSITORY_OBJ_NODE", [])
        )
        
        # Handle both single node and array of nodes
        items = nodes if isinstance(nodes, list) else [nodes] if nodes else []
        print(f"Found {len(items)} items in package")

        # Extract and filter
        result = []
        for n in items:
            name = n.get("OBJECT_NAME")
            uri = n.get("OBJECT_URI")
            if not name or not uri:
                continue
            result.append({
                "OBJECT_TYPE": n.get("OBJECT_TYPE"),
                "OBJECT_NAME": name,
                "OBJECT_DESCRIPTION": n.get("DESCRIPTION"),
                "OBJECT_URI": uri
            })

        print(f"Successfully extracted {len(result)} objects from package {package_name}")
        return result
        
    except HTTPError as e:
        if e.response.status_code == 404:
            raise AdtError(404, f"Package '{package_name}' not found") from e
        elif e.response.status_code == 403:
            raise AdtError(403, f"Access forbidden: {e.response.text}") from e
        else:
            raise AdtError(e.response.status_code, f"HTTP error: {e.response.text}") from e
    except RequestException as e:
        raise ConnectionError(f"Network error: {e}") from e
    except Exception as e:
        raise AdtError(500, f"Unexpected error: {e}") from e
