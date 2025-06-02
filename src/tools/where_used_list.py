# tools/where_used_list.py

import xmltodict
from typing import Optional, Dict, List
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini function-calling
get_where_used_definition = {
    "name": "get_where_used_list",
    "description": "Retrieve where-used references for an ABAP class via ADT usageReferences.",
    "parameters": {
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "Name of the ABAP class to search usages for."
            },
            "start_position": {
                "type": "object",
                "description": "Starting position in the source code (row, col).",
                "properties": {
                    "row": {"type": "integer"},
                    "col": {"type": "integer"}
                }
            },
            "end_position": {
                "type": "object",
                "description": "Optional end position in the source code (row, col).",
                "properties": {
                    "row": {"type": "integer"},
                    "col": {"type": "integer"}
                }
            }
        },
        "required": ["class_name", "start_position"]
    }
}

def _fetch_csrf_token_from_class_source(
    session,
    class_name: str
) -> str:
    """
    Fetches a CSRF token by doing a plain-text GET on the class source endpoint.
    """
    src_url = f"{SAP_URL.rstrip('/')}/sap/bc/adt/oo/classes/{class_name}/source/main"
    resp = session.get(
        src_url,
        headers={
            "X-CSRF-Token": "Fetch",
            "Accept":       "text/plain"
        }
    )
    resp.raise_for_status()
    token = resp.headers.get("X-CSRF-Token")
    if not token:
        raise AdtError(resp.status_code, "Failed to fetch CSRF token")
    return token

def get_where_used_list(
    class_name: str,
    start_position: Dict[str,int],
    end_position: Optional[Dict[str,int]] = None
) -> List[Dict[str,str]]:
    """
    Calls the ADT usageReferences endpoint for a given ABAP class and code position,
    parses the XML response, and returns a list of references:
      - name
      - type
      - uri
    """
    # validate start_position
    row = start_position.get("row")
    col = start_position.get("col")
    if row is None or col is None:
        raise ValueError("start_position must include 'row' and 'col'")

    session = make_session()

    # 1) fetch CSRF token
    token = _fetch_csrf_token_from_class_source(session, class_name)

    # 2) build the fragment for the source URI
    frag = f"start={row},{col}"
    if end_position:
        erow = end_position.get("row")
        ecol = end_position.get("col")
        if erow is None or ecol is None:
            raise ValueError("end_position must include 'row' and 'col' if provided")
        frag += f";end={erow},{ecol}"

    source_uri = (
        f"/sap/bc/adt/oo/classes/{class_name}/source/main"
        f"?version=active#{frag}"
    )
    endpoint = f"{SAP_URL.rstrip('/')}/sap/bc/adt/repository/informationsystem/usageReferences"

    # 3) POST the usageReferences request
    body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<usageReferenceRequest xmlns="http://www.sap.com/adt/ris/usageReferences"/>'
    )
    try:
        resp = session.post(
            endpoint,
            params={
                "sap-client": SAP_CLIENT,
                "uri":         source_uri
            },
            headers={
                "X-CSRF-Token": token,
                "Accept":       "application/vnd.sap.adt.repository.usagereferences.result.v1+xml",
                "Content-Type": "application/vnd.sap.adt.repository.usagereferences.request.v1+xml",
                "X-sap-adt-profiling": "server-time"
            },
            data=body
        )
        resp.raise_for_status()
    except HTTPError as e:
        raise AdtError(resp.status_code, resp.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error during usageReferences POST: {e}") from e

    # 4) parse XML into Python objects
    doc = xmltodict.parse(resp.text)
    result_nodes = (
        doc.get("usageReferences:usageReferenceResult", {})
           .get("usageReferences:referencedObjects", {})
           .get("usageReferences:referencedObject", [])
    )
    items = result_nodes if isinstance(result_nodes, list) else [result_nodes]

    references: List[Dict[str,str]] = []
    for node in items:
        adt = node.get("usageReferences:adtObject", {})
        references.append({
            "name": adt.get("@adtcore:name", ""),
            "type": adt.get("@adtcore:type", ""),
            "uri":  node.get("@uri", "")
        })
    return references
