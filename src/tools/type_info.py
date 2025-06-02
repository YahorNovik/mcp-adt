# tools/type_info.py

import xmltodict
from xml.dom.minidom import parseString
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini function‐calling
get_type_info_definition = {
    "name": "get_type_info",
    "description": (
        "Fetches the source lines for domain or data element; "
        "if no domain exists, falls back to fetch a DDIC data element."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "type_name": {
                "type": "string",
                "description": "Name of the DDIC domain or data element (e.g. 'ZMY_DOMAIN')."
            }
        },
        "required": ["type_name"]
    }
}

def _pretty_xml_lines(xml_str: str) -> list[str]:
    """Turn a raw XML string into a pretty-printed list of lines."""
    dom = parseString(xml_str)
    pretty = dom.toprettyxml(indent="  ")
    # remove empty lines
    return [line for line in pretty.splitlines() if line.strip()]

def get_type_info(type_name: str) -> list[str]:
    """
    Fetch DDIC type info via ADT:
      1) Try domain source at /ddic/domains/{type_name}/source/main
      2) If that returns 404, fall back to data element at /ddic/dataelements/{type_name}
    Domain lookup:
      - Accept: application/vnd.sap.adt.abapsource+xml, then text/plain on 406
    Data element lookup:
      - No Accept header (server default)
    Raises: AdtError on 404 both lookups; ConnectionError on network failures.
    Returns: Pretty-printed XML lines.
    """
    print(f"Fetching type info for {type_name}")
    if not type_name:
        raise ValueError("type_name is required")

    session = make_session()
    base    = SAP_URL.rstrip('/')
    params  = {"sap-client": SAP_CLIENT}
    hdr_xml = {"Accept": "application/vnd.sap.adt.abapsource+xml"}
    hdr_txt = {"Accept": "text/plain"}

    # 1) Try domain source
    domain_url = f"{base}/sap/bc/adt/ddic/domains/{type_name}/source/main"
    try:
        resp = session.get(domain_url, params=params, headers=hdr_xml)
        if resp.status_code == 406:
            resp = session.get(domain_url, params=params, headers=hdr_txt)
        resp.raise_for_status()
        return _pretty_xml_lines(resp.text)
    except HTTPError as e:
        # only fall back to data element if it was a 404
        if e.response.status_code != 404:
            raise AdtError(e.response.status_code, e.response.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error fetching domain: {e}") from e

    # 2) Now try data element (no Accept header)
    de_url = f"{base}/sap/bc/adt/ddic/dataelements/{type_name}"
    try:
        resp = session.get(de_url, params=params)
        resp.raise_for_status()
        return _pretty_xml_lines(resp.text)
    except HTTPError as e_de:
        if resp.status_code == 404:
            raise AdtError(404, f"Type '{type_name}' not found as domain or data element") from e_de
        raise AdtError(resp.status_code, resp.text) from e_de
    except RequestException as net:
        raise ConnectionError(f"Network error fetching data element: {net}") from net
