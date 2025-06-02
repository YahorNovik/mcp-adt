# tools/source_by_uri.py

from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

get_source_by_uri_definition = {
    "name": "get_source_by_uri",
    "description": (
        "Fetches an ABAP source fragment by its ADT URI, "
        "including any URL fragment (e.g. method anchors)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "uri": {
                "type": "string",
                "description": (
                    "Full ADT URI path (including fragment) "
                    "starting with '/sap/bc/adt/...'"
                )
            }
        },
        "required": ["uri"]
    }
}

def get_source_by_uri(uri: str) -> list[str]:
    """
    GETs the given ADT URI (including any #fragment) with Accept:text/plain,
    and returns the lines of source covering that fragment.
    """
    if not uri.startswith("/sap/bc/adt/"):
        raise ValueError("uri must start with '/sap/bc/adt/'")

    session  = make_session()
    base     = SAP_URL.rstrip('/')
    full_url = f"{base}{uri}"
    params   = {"sap-client": SAP_CLIENT}
    headers  = {"Accept": "text/plain"}

    try:
        resp = session.get(full_url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.text.splitlines()
    except HTTPError as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Fragment URI not found: {uri}") from e
        raise AdtError(resp.status_code, resp.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error fetching {uri}: {e}") from e
