from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# Gemini function‐calling schema
get_behavior_definition_source_definition = {
    "name": "get_behavior_definition_source",
    "description": "Fetch the source code of an ABAP Behavior Definition via ADT.",
    "parameters": {
        "type": "object",
        "properties": {
            "behavior_name": {
                "type": "string",
                "description": "Name of the behavior definition (e.g. 'I_INHOUSEREPAIRTP')."
            }
        },
        "required": ["behavior_name"]
    }
}

def get_behavior_definition_source(behavior_name: str) -> list[str]:
    """
    Retrieve an ABAP Behavior Definition’s source lines via ADT.

    - GET /sap/bc/adt/bo/behaviordefinitions/{behavior_name}/source/main
      with Accept: text/plain
    - Returns the plain-text source split into a list of lines.
    - Raises AdtError on HTTP errors, ConnectionError on network failures.
    """
    if not behavior_name:
        raise ValueError("behavior_name is required")

    session  = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = f"{base}/sap/bc/adt/bo/behaviordefinitions/{behavior_name}/source/main"
    params   = {"sap-client": SAP_CLIENT}
    headers  = {"Accept": "text/plain"}

    try:
        resp = session.get(endpoint, params=params, headers=headers)
        resp.raise_for_status()
        return resp.text.splitlines()
    except HTTPError as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Behavior definition '{behavior_name}' not found") from e
        raise AdtError(resp.status_code, resp.text) from e
    except RequestException as e:
        raise ConnectionError(f"Failed to fetch behavior definition: {e}") from e
