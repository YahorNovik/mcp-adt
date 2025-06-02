# tools/usage_references.py

import xmltodict
from typing import Optional, Dict, List
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini function-calling
get_usage_references_definition = {
    "name": "get_usage_references",
    "description": (
        "Retrieve where-used references for an ABAP object "
        "(class, program, include, function_module, interface, table, structure).  "
        "By default, it looks at the very first character of the source."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "object_type": {
                "type": "string",
                "description": (
                    "One of: 'class','program','include','function_module',"
                    "'interface','table','structure'"
                )
            },
            "object_name": {
                "type": "string",
                "description": "The ABAP object name, e.g. 'ZMY_CLASS'"
            },
            "function_group": {
                "type": "string",
                "description": "Function group name (required if object_type is 'function_module')"
            },
            "start_position": {
                "type": "object",
                "description": "Starting position in code (row, col). Defaults to {row:1,col:0}.",
                "properties": {
                    "row": {"type": "integer"},
                    "col": {"type": "integer"}
                },
                "default": {"row": 1, "col": 0}
            },
            "end_position": {
                "type": "object",
                "description": "Optional end position in code (row, col).",
                "properties": {
                    "row": {"type": "integer"},
                    "col": {"type": "integer"}
                }
            }
        },
        "required": ["object_type", "object_name"]
    }
}


def _build_source_path(
    object_type: str,
    object_name: str,
    function_group: Optional[str]
) -> str:
    # Normalize ADT codes to our categories
    ot = object_type.lower()
    # accept raw ADT codes or semantic names
    if ot.startswith("clas"):
        ot = "class"
    elif ot.startswith("prog/p"):
        ot = "program"
    elif ot.startswith("prog/i"):
        ot = "include"
    elif ot.startswith("intf"):
        ot = "interface"
    elif ot.startswith("tabl"):
        ot = "table"
    elif ot.startswith("ttyp"):
        ot = "structure"
    elif ot.startswith("function_module") or ot.startswith("fu") or ot.startswith("func"):
        ot = "function_module"
    if ot == "class":
        return f"/sap/bc/adt/oo/classes/{object_name}/source/main"
    if ot == "program":
        return f"/sap/bc/adt/programs/programs/{object_name}/source/main"
    if ot == "include":
        return f"/sap/bc/adt/programs/includes/{object_name}/source/main"
    if ot == "interface":
        return f"/sap/bc/adt/oo/interfaces/{object_name}/source/main"
    if ot == "table":
        return f"/sap/bc/adt/ddic/tables/{object_name}/source/main"
    if ot == "structure":
        return f"/sap/bc/adt/ddic/structures/{object_name}/source/main"
    if ot == "function_module":
        if not function_group:
            raise ValueError("function_group is required for 'function_module'")
        return (
            f"/sap/bc/adt/functions/groups/{function_group}"
            f"/fmodules/{object_name}/source/main"
        )
    raise ValueError(f"Unsupported object_type: {object_type}")


def _fetch_csrf_token(session, full_url: str) -> str:
    resp = session.get(
        full_url,
        params={"sap-client": SAP_CLIENT},
        headers={"X-CSRF-Token": "Fetch", "Accept": "text/plain"}
    )
    try:
        resp.raise_for_status()
    except HTTPError as e:
        raise AdtError(resp.status_code, resp.text) from e

    token = resp.headers.get("X-CSRF-Token")
    if not token:
        raise AdtError(resp.status_code, "Missing CSRF token")
    return token


def get_usage_references(
    object_type: str,
    object_name: str,
    function_group: Optional[str] = None,
    start_position: Optional[Dict[str,int]] = None,
    end_position:   Optional[Dict[str,int]] = None
) -> List[Dict[str,str]]:
    print(f"Fetching usage references for {object_type}/{object_name}")
    # default to beginning of file
    if start_position is None:
        start_position = {"row": 1, "col": 0}
    r, c = start_position.get("row"), start_position.get("col")

    session = make_session()

    # Build the source path & CSRF token
    src_path = _build_source_path(object_type, object_name, function_group)
    print(f"Source path: {src_path}")
    full_src = f"{SAP_URL.rstrip('/')}{src_path}"
    token    = _fetch_csrf_token(session, full_src)

    # Build fragment & URI param
    frag = f"start={r},{c}"
    if end_position:
        frag += f";end={end_position['row']},{end_position['col']}"
    uri_param = f"{src_path}?version=active#{frag}"

    # Prepare POST
    endpoint = f"{SAP_URL.rstrip('/')}/sap/bc/adt/repository/informationsystem/usageReferences"
    headers  = {
        "X-CSRF-Token": token,
        "Accept":       "application/vnd.sap.adt.repository.usagereferences.result.v1+xml",
        "Content-Type": "application/vnd.sap.adt.repository.usagereferences.request.v1+xml"
    }
    body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<usageReferenceRequest xmlns="http://www.sap.com/adt/ris/usageReferences"/>'
    )

    resp = session.post(
        endpoint,
        params={"sap-client": SAP_CLIENT, "uri": uri_param},
        headers=headers,
        data=body
    )

    print(resp)

    try:
        resp.raise_for_status()
    except HTTPError as e:
        raise AdtError(resp.status_code, resp.text) from e

    # Parse XML
    doc  = xmltodict.parse(resp.text)
    root = doc.get("usageReferences:usageReferenceResult", {})

    ro = root.get("usageReferences:referencedObjects")
    if not ro:
        return []

    raw = ro.get("usageReferences:referencedObject", [])
    entries = raw if isinstance(raw, list) else [raw]

    result: List[Dict[str,str]] = []
    for n in entries:
        adt = n.get("usageReferences:adtObject") or {}
        result.append({
            "name": adt.get("@adtcore:name", ""),
            "type": adt.get("@adtcore:type", ""),
            "uri":  n.get("@uri", "")
        })
    return result