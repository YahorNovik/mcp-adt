import xmltodict
from .utils import AdtError, make_session, SAP_URL

# Function‐calling metadata for Gemini
get_function_source_definition = {
    "name": "get_function_source",
    "description": "Retrieve source code lines for an ABAP function module via ADT, with XML and text fallback.",
    "parameters": {
        "type": "object",
        "properties": {
            "function_group": {
                "type": "string",
                "description": "Function group name (e.g. ZFUNC_GROUP)"
            },
            "function_name": {
                "type": "string",
                "description": "Function module name (e.g. ZFUNC_MODULE)"
            }
        },
        "required": ["function_group", "function_name"]
    }
}

def get_function_source(
    function_group: str,
    function_name: str
) -> list[str]:
    """
    Fetch ABAP function module source lines via ADT API.
    Tries XML mode first (ADT payload); on 406 falls back to plain text.
    Returns list of source‐code lines.
    """
    print(f"Fetching function source for {function_group}/{function_name}")
    if not function_group or not function_name:
        raise ValueError("function_group and function_name are required")

    session = make_session()
    endpoint = (
        f"{SAP_URL.rstrip('/')}/sap/bc/adt/functions/"
        f"groups/{function_group}/fmodules/{function_name}/source/main"
    )
    hdr_xml   = {"Accept": "application/vnd.sap.adt.abapsource+xml"}
    hdr_plain = {"Accept": "text/plain"}

    # Try XML first
    resp = session.get(endpoint, headers=hdr_xml)
    if resp.status_code == 406:
        # Fallback to plain text
        resp2 = session.get(endpoint, headers=hdr_plain)
        resp2.raise_for_status()
        return resp2.text.splitlines()
    try:
        resp.raise_for_status()
    except Exception as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Function {function_group}/{function_name} not found") from e
        raise

    # Parse XML payload
    doc = xmltodict.parse(resp.text)
    lines = doc['adtcore:abapsource']['objectSource']['line']
    if isinstance(lines, str):
        return [lines]
    return [ln.get('#text', '') for ln in lines]
