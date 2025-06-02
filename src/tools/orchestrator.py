from typing import Any, Dict, List
from .search_objects import get_search_objects
from .usage_references import get_usage_references
from .class_source import get_class_source
from .program_source import get_program_source
from .function_source import get_function_source

# Gemini function‐calling schema
analyze_object_definition = {
    "name": "analyze_object",
    "description": (
        "Auto-discover an ABAP object’s type via quickSearch, "
        "get its where-used list, then fetch the source of any "
        "class/program/function_module hits."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "object_name": {
                "type": "string",
                "description": "Name of the ABAP object to analyze."
            },
            "max_usage": {
                "type": "integer",
                "description": "Max number of where-used hits to fetch source for.",
                "default": 5
            }
        },
        "required": ["object_name"]
    }
}

def analyze_object(object_name: str, max_usage: int = 5) -> Dict[str, Any]:
    """
    1) quickSearch to find the object's ADT type & URI
    2) normalize that to one of our semantic object_types
    3) extract function_group from URI for function_modules
    4) call get_usage_references at row=1,col=0
    5) fetch source for up to max_usage dependencies of type class/program/function_module
    """
    # 1) discover via quickSearch
    hits = get_search_objects(object_name, max_results=1)
    if not hits:
        return {"error": f"No object found matching '{object_name}'"}
    primary = hits[0]
    adt_type = primary["objectType"].lower()      # e.g. "clas/oc", "fugr/ff", etc.
    uri      = primary["uri"]                     # e.g. "/sap/bc/adt/functions/groups/WVK3/fmodules/…"

    # 2) map ADT code → semantic object_type & extract function_group
    if adt_type.startswith("clas"):
        object_type = "class"
        func_group  = None
    elif adt_type.startswith("prog/p"):
        object_type = "program"
        func_group  = None
    elif adt_type.startswith("prog/i"):
        object_type = "include"
        func_group  = None
    elif adt_type.startswith("intf"):
        object_type = "interface"
        func_group  = None
    elif adt_type.startswith("tabl"):
        object_type = "table"
        func_group  = None
    elif adt_type.startswith("ttyp"):
        object_type = "structure"
        func_group  = None
    elif adt_type.startswith("fugr") or adt_type.startswith("fu"):
        object_type = "function_module"
        # pull the group name out of the URI path
        parts = uri.strip("/").split("/")
        try:
            idx = parts.index("groups")
            func_group = parts[idx + 1]
        except (ValueError, IndexError):
            raise ValueError(f"Cannot parse function group from URI: {uri}")
    else:
        raise ValueError(f"Unknown ADT type code: {adt_type}")

    # 3) annotate our primary result
    result: Dict[str, Any] = {
        "object": {
            "name":        primary["objectName"],
            "adt_type":    adt_type,
            "semantic":    object_type,
            "function_group": func_group,
            "uri":         uri
        }
    }

    # 4) fetch where-used list at the very start of the source
    try:
        usage = get_usage_references(
            object_type=object_type,
            object_name=primary["objectName"],
            function_group=func_group,
            start_position={"row": 1, "col": 0}
        )
    except Exception as e:
        # if the service fails, we treat as empty
        usage = []
        result["whereUsedError"] = str(e)

    result["whereUsed"] = usage

    # 5) for the first few hits of interest, fetch source
    deps: List[Dict[str, Any]] = []
    for hit in usage[:max_usage]:
        hit_type = hit["type"].split("/")[0].lower()  # "clas", "prog", "fugr", etc.
        name     = hit["name"]
        if name != object_name:
          try:
              if hit_type == "clas":
                  src = get_class_source(name)
              elif hit_type.startswith("prog"):
                # includes and programs share program_source
                src = get_program_source(name)
              elif hit_type in ("fugr", "fu", "function_module"):
                # reuse our primary function_group
                src = get_function_source(name, func_group)
              else:
                # skip unknown hit types
                continue
              deps.append({"name": name, "type": hit_type, "source": src})
          except Exception as e:
              deps.append({"name": name, "type": hit_type, "error": str(e)})

    result["dependencySources"] = deps
    return result
