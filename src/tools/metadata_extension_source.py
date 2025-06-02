# tools/metadata_extension_source.py

from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# Gemini function‐calling schema
get_metadata_extension_source_definition = {
    "name": "get_metadata_extension_source",
    "description": "Fetch the DDL source code for a Metadata Extension via ADT.",
    "parameters": {
        "type": "object",
        "properties": {
            "extension_name": {
                "type": "string",
                "description": "Name of the metadata extension (e.g. 'C_MANAGEINCIDENT')."
            }
        },
        "required": ["extension_name"]
    }
}

def get_metadata_extension_source(extension_name: str) -> list[str]:
    """
    Retrieve a Metadata Extension’s source lines via ADT.

    - GET /sap/bc/adt/ddic/ddlx/sources/{extension_name}/source/main
      with Accept: text/plain
    - Returns the plain-text DDL split into lines.
    - Raises AdtError on HTTP errors, ConnectionError on network failures.
    """
    if not extension_name:
        raise ValueError("extension_name is required")

    session  = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = (
        f"{base}/sap/bc/adt/ddic/ddlx/sources/{extension_name}/source/main"
    )
    params  = {"sap-client": SAP_CLIENT}
    headers = {"Accept": "text/plain"}

    try:
        resp = session.get(endpoint, params=params, headers=headers)
        resp.raise_for_status()
        return resp.text.splitlines()
    except HTTPError as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Metadata Extension '{extension_name}' not found") from e
        raise AdtError(resp.status_code, resp.text) from e
    except RequestException as e:
        raise ConnectionError(f"Failed to fetch metadata extension: {e}") from e
