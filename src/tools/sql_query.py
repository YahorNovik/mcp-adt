# tools/sql_query.py

import re
from typing import Dict, List, Any, Optional
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session_with_timeout, SAP_URL, SAP_CLIENT

# JSON schema for MCP function-calling
get_sql_query_definition = {
    "name": "get_sql_query",
    "description": "Execute freestyle SQL queries via SAP ADT Data Preview API.",
    "parameters": {
        "type": "object",
        "properties": {
            "sql_query": {
                "type": "string",
                "description": "SQL query to execute (e.g. 'SELECT * FROM T000 WHERE MANDT = 100')."
            },
            "max_rows": {
                "type": "integer",
                "description": "Maximum number of rows to return (default: 100).",
                "default": 100
            }
        },
        "required": ["sql_query"]
    }
}

def _parse_sql_query_xml(xml_data: str, sql_query: str, max_rows: int) -> Dict[str, Any]:
    """
    Parse SAP ADT XML response from freestyle SQL query and convert to JSON format.
    """
    try:
        # Extract basic information
        total_rows_match = re.search(r'<dataPreview:totalRows>(\d+)</dataPreview:totalRows>', xml_data)
        total_rows = int(total_rows_match.group(1)) if total_rows_match else 0
        
        query_time_match = re.search(r'<dataPreview:queryExecutionTime>([\d.]+)</dataPreview:queryExecutionTime>', xml_data)
        execution_time = float(query_time_match.group(1)) if query_time_match else 0.0

        # Extract column metadata
        columns = []
        column_matches = re.findall(r'<dataPreview:metadata[^>]*>', xml_data)
        
        for match in column_matches:
            name_match = re.search(r'dataPreview:name="([^"]+)"', match)
            type_match = re.search(r'dataPreview:type="([^"]+)"', match)
            desc_match = re.search(r'dataPreview:description="([^"]+)"', match)
            length_match = re.search(r'dataPreview:length="(\d+)"', match)
            
            if name_match:
                columns.append({
                    "name": name_match.group(1),
                    "type": type_match.group(1) if type_match else "UNKNOWN",
                    "description": desc_match.group(1) if desc_match else "",
                    "length": int(length_match.group(1)) if length_match else None
                })

        # Extract row data
        rows = []
        column_sections = re.findall(r'<dataPreview:columns>.*?</dataPreview:columns>', xml_data, re.DOTALL)
        
        if column_sections:
            # Extract data for each column
            column_data = {}
            
            for index, section in enumerate(column_sections):
                if index < len(columns):
                    column_name = columns[index]["name"]
                    data_matches = re.findall(r'<dataPreview:data[^>]*>(.*?)</dataPreview:data>', section)
                    
                    if data_matches:
                        # Clean HTML tags and get content
                        column_data[column_name] = [
                            re.sub(r'<[^>]+>', '', match).strip() if match else None 
                            for match in data_matches
                        ]
                    else:
                        column_data[column_name] = []

            # Convert column-based data to row-based data
            if column_data:
                max_row_count = max(len(arr) for arr in column_data.values()) if column_data else 0
                
                for row_index in range(max_row_count):
                    row = {}
                    for column in columns:
                        column_values = column_data.get(column["name"], [])
                        row[column["name"]] = column_values[row_index] if row_index < len(column_values) else None
                    rows.append(row)

        return {
            "sql_query": sql_query,
            "max_rows": max_rows,
            "execution_time": execution_time,
            "total_rows": total_rows,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }

    except Exception as parse_error:
        print(f"Failed to parse SQL query XML: {parse_error}")
        return {
            "sql_query": sql_query,
            "max_rows": max_rows,
            "execution_time": 0.0,
            "total_rows": 0,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "parse_error": str(parse_error)
        }

def get_sql_query(sql_query: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Execute freestyle SQL queries via SAP ADT Data Preview API.
    
    - POSTs SQL query to freestyle data preview endpoint
    - Parses XML response into structured JSON
    - Returns columns, rows, and execution metadata
    """
    print(f"Executing SQL query: {sql_query}")
    print(f"Max rows: {max_rows}")
    
    if not sql_query:
        raise ValueError("sql_query is required")

    # Use long timeout for SQL queries as they can take time
    session = make_session_with_timeout("long")
    
    try:
        # Build URL for freestyle data preview
        endpoint = f"{SAP_URL.rstrip('/')}/sap/bc/adt/datapreview/freestyle"
        params = {
            "sap-client": SAP_CLIENT,
            "rowNumber": str(max_rows)
        }
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/vnd.sap.adt.datapreview.table.v1+xml"
        }
        
        # Get CSRF token first with csrf timeout
        csrf_session = make_session_with_timeout("csrf")
        csrf_url = f"{SAP_URL.rstrip('/')}/sap/bc/adt/discovery"
        csrf_resp = csrf_session.get(
            csrf_url,
            headers={"x-csrf-token": "fetch", "Accept": "application/atomsvc+xml"}
        )
        
        token = csrf_resp.headers.get("x-csrf-token")
        if not token:
            raise ConnectionError("No CSRF token in response headers")
        
        # Add CSRF token to headers
        headers["x-csrf-token"] = token
        
        # Add cookies if available
        if session.cookies:
            auto_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
            headers["Cookie"] = auto_cookies
        
        print(f"Making POST request to: {endpoint}")
        
        # Execute POST request with SQL query in body
        resp = session.post(
            endpoint,
            params=params,
            headers=headers,
            data=sql_query
        )
        
        resp.raise_for_status()
        
        if resp.status_code == 200 and resp.text:
            print("SQL query executed successfully")
            # Parse the XML response
            parsed_data = _parse_sql_query_xml(resp.text, sql_query, max_rows)
            print(f"Retrieved {parsed_data.get('row_count', 0)} rows in {parsed_data.get('execution_time', 0)}ms")
            return parsed_data
        else:
            raise AdtError(resp.status_code, f"Failed to execute SQL query. Status: {resp.status_code}")
            
    except HTTPError as e:
        raise AdtError(e.response.status_code, e.response.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error executing SQL query: {e}") from e
