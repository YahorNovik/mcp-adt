import xmltodict
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini / function-calling
get_function_group_source_definition = {
    "name": "get_function_group_source",
    "description": "Retrieve source code lines for an ABAP Function Group via the ADT API, with XML and plain-text fallback.",
    "parameters": {
        "type": "object",
        "properties": {
            "function_group": {
                "type": "string",
                "description": "Name of the ABAP Function Group (e.g. 'ZMY_FUNC_GROUP')."
            }
        },
        "required": ["function_group"]
    }
}

def get_function_group_source(
    function_group: str
) -> list[str]:
    """
    Fetches the source code of an ABAP Function Group via ADT.

    - Tries XML mode first (ADT payload).
    - On 406 Not Acceptable, retries with plain text.
    - Raises AdtError on 404/not found; ConnectionError on network failures.
    """
    print(f"Fetching function group source for {function_group}")
    if not function_group:
        raise ValueError("function_group is required")

    session = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = (
        f"{base}/sap/bc/adt/functions/"
        f"groups/{function_group}/source/main"
    )
    params   = {"sap-client": SAP_CLIENT}
    hdr_xml  = {"Accept": "application/vnd.sap.adt.abapsource+xml"}
    hdr_txt  = {"Accept": "text/plain"}

    # 1) Try XML payload
    resp = session.get(endpoint, params=params, headers=hdr_xml)
    if resp.status_code == 406:
        # 2) Fallback to plain text
        resp2 = session.get(endpoint, params=params, headers=hdr_txt)
        resp2.raise_for_status()
        return resp2.text.splitlines()

    try:
        resp.raise_for_status()
    except Exception as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Function group '{function_group}' not found") from e
        raise

    # 3) Parse ADT XML into Python list of lines
    doc   = xmltodict.parse(resp.text)
    lines = doc['adtcore:abapsource']['objectSource']['line']
    if isinstance(lines, str):
        return [lines]
    return [ln.get('#text', '') for ln in lines]
