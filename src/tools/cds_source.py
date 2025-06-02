# tools/cds_source.py

from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# Gemini function-calling schema
get_cds_source_definition = {
    "name": "get_cds_source",
    "description": "Fetch the DDL source code for a CDS view or entity via ADT.",
    "parameters": {
        "type": "object",
        "properties": {
            "cds_name": {
                "type": "string",
                "description": "Name of the CDS source (e.g. 'I_INHOUSEREPAIR')."
            }
        },
        "required": ["cds_name"]
    }
}

def get_cds_source(cds_name: str) -> list[str]:
    """
    Retrieve a CDS DDL source via the ADT DDIC DDL service.

    - GETs /sap/bc/adt/ddic/ddl/sources/{cds_name}/source/main
    - Returns the plain-text DDL split into lines.
    - Raises AdtError on HTTP errors, ConnectionError on network failures.
    """
    if not cds_name:
        raise ValueError("cds_name is required")

    session  = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = f"{base}/sap/bc/adt/ddic/ddl/sources/{cds_name}/source/main"
    params   = {"sap-client": SAP_CLIENT}
    headers  = {"Accept": "text/plain"}

    try:
        resp = session.get(endpoint, params=params, headers=headers)
        resp.raise_for_status()
        return resp.text.splitlines()
    except HTTPError as e:
        # 404 → not found
        if resp.status_code == 404:
            raise AdtError(404, f"CDS source '{cds_name}' not found") from e
        raise AdtError(resp.status_code, resp.text) from e
    except RequestException as e:
        raise ConnectionError(f"Failed to fetch CDS source: {e}") from e
