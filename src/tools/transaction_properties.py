import xmltodict
from urllib.parse import quote
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini function‐calling
get_transaction_properties_definition = {
    "name": "get_transaction_properties",
    "description": "Retrieve the package and application facets for an ABAP transaction via ADT.",
    "parameters": {
        "type": "object",
        "properties": {
            "transaction_name": {
                "type": "string",
                "description": "ABAP transaction code (e.g. 'SE38')."
            }
        },
        "required": ["transaction_name"]
    }
}

def get_transaction_properties(
    transaction_name: str
) -> dict:
    """
    Fetches ADT object-properties for a transaction, returning parsed XML as a Python dict.

    - Hits the ADT repository/informationsystem/objectproperties/values endpoint.
    - Requests facets 'package' and 'appl' for the given transaction.
    - Raises AdtError on 404/not found; ConnectionError on network failures.
    """
    print(f"Fetching transaction properties for {transaction_name}")
    if not transaction_name:
        raise ValueError("transaction_name is required")

    session = make_session()
    base     = SAP_URL.rstrip('/')
    endpoint = (
        f"{base}/sap/bc/adt/repository/informationsystem/objectproperties/values"
    )

    # Build the object URI for the transaction
    encoded_tx = quote(transaction_name, safe='')
    uri = f"/sap/bc/adt/vit/wb/object_type/trant/object_name/{encoded_tx}"

    params = {
        "uri":     uri,
        "facet":   ["package", "appl"],
        "sap-client": SAP_CLIENT
    }

    resp = session.get(endpoint, params=params)
    try:
        resp.raise_for_status()
    except Exception as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Transaction '{transaction_name}' not found") from e
        raise

    # Parse the XML into a Python dict
    parsed = xmltodict.parse(resp.text)
    return parsed