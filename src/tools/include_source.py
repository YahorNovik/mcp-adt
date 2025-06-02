import xmltodict
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini function‐calling
get_include_source_definition = {
    "name": "get_include_source",
    "description": "Retrieve source code lines for an ABAP include via ADT, with XML and text fallback.",
    "parameters": {
        "type": "object",
        "properties": {
            "include_name": {
                "type": "string",
                "description": "Name of the ABAP include (e.g. 'ZMY_INCLUDE')."
            }
        },
        "required": ["include_name"]
    }
}

def get_include_source(
    include_name: str
) -> list[str]:
    """
    Fetches source lines of an ABAP include via the ADT API.

    - Tries XML (ADT payload) first.
    - On 406 Not Acceptable, retries with plain text.
    - Raises AdtError on 404/not found; ConnectionError on network errors.
    """
    print(f"Fetching include source for {include_name}")
    if not include_name:
        raise ValueError("include_name is required")

    session = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = (
        f"{base}/sap/bc/adt/programs/"
        f"includes/{include_name}/source/main"
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
            raise AdtError(404, f"Include '{include_name}' not found") from e
        raise

    # 3) Parse ADT XML into a list of lines
    doc   = xmltodict.parse(resp.text)
    lines = doc['adtcore:abapsource']['objectSource']['line']
    if isinstance(lines, str):
        return [lines]
    return [ln.get('#text', '') for ln in lines]