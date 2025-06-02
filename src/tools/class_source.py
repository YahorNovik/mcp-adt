import xmltodict
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL

# Function-calling metadata for Gemini
get_class_source_definition = {
    "name": "get_class_source",
    "description": "Retrieve ABAP class source lines via ADT, with XML and plain-text fallback.",
    "parameters": {
        "type": "object",
        "properties": {
            "class_name": {"type": "string", "description": "ABAP class name (e.g. ZCL_FOO)"}
        },
        "required": ["class_name"]
    }
}

def get_class_source(class_name: str) -> list[str]:
    """
    Fetches ABAP class source lines via ADT API.
    Tries XML mode first, then falls back to plain text on 406.
    """
    print(f"Fetching class source for {class_name}")
    if not class_name:
        raise ValueError("class_name is required")

    session = make_session()
    endpoint = f"{SAP_URL.rstrip('/')}/sap/bc/adt/oo/classes/{class_name}/source/main"
    hdr_xml   = {"Accept": "application/vnd.sap.adt.abapsource+xml"}
    hdr_plain = {"Accept": "text/plain"}

    try:
        resp = session.get(endpoint, headers=hdr_xml)
        resp.raise_for_status()
        doc = xmltodict.parse(resp.text)
        lines = doc['adtcore:abapsource']['objectSource']['line']
        if isinstance(lines, str):
            return [lines]
        return [ln.get('#text', '') for ln in lines]
    except HTTPError as e:
        if resp.status_code == 406:
            resp2 = session.get(endpoint, headers=hdr_plain)
            resp2.raise_for_status()
            return resp2.text.splitlines()
        if resp.status_code == 404:
            raise AdtError(404, f"Class {class_name} not found")
        raise AdtError(resp.status_code, resp.text)
    except RequestException as e:
        raise ConnectionError(f"Network error: {e}")