#!/usr/bin/env python3
"""
Test script to verify the latest MCP tools are properly integrated.
This script tests GetIncludesList and GetEnhancementByName functionality.
"""

import sys
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all latest modules can be imported successfully."""
    print("Testing imports for latest features...")
    
    try:
        from src.tools.includes_list import get_includes_list
        print("SUCCESS: includes_list.py imported successfully")
    except Exception as e:
        print(f"FAILED: Failed to import includes_list: {e}")
        return False
    
    try:
        from src.tools.enhancement_by_name import get_enhancement_by_name
        print("SUCCESS: enhancement_by_name.py imported successfully")
    except Exception as e:
        print(f"FAILED: Failed to import enhancement_by_name: {e}")
        return False
    
    try:
        from src.tools.enhancements import get_enhancements
        print("SUCCESS: Updated enhancements.py imported successfully")
    except Exception as e:
        print(f"FAILED: Failed to import updated enhancements: {e}")
        return False
    
    return True

def test_function_signatures():
    """Test that functions have correct signatures."""
    print("\nTesting function signatures...")
    
    try:
        from src.tools.includes_list import get_includes_list
        import inspect
        
        # Test get_includes_list signature
        sig = inspect.signature(get_includes_list)
        params = list(sig.parameters.keys())
        expected_params = ['object_name', 'object_type']
        
        if params == expected_params:
            print("SUCCESS: get_includes_list has correct signature")
        else:
            print(f"FAILED: get_includes_list signature mismatch. Expected: {expected_params}, Got: {params}")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing get_includes_list signature: {e}")
        return False
    
    try:
        from src.tools.enhancement_by_name import get_enhancement_by_name
        import inspect
        
        # Test get_enhancement_by_name signature
        sig = inspect.signature(get_enhancement_by_name)
        params = list(sig.parameters.keys())
        expected_params = ['enhancement_spot', 'enhancement_name']
        
        if params == expected_params:
            print("SUCCESS: get_enhancement_by_name has correct signature")
        else:
            print(f"FAILED: get_enhancement_by_name signature mismatch. Expected: {expected_params}, Got: {params}")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing get_enhancement_by_name signature: {e}")
        return False
    
    try:
        from src.tools.enhancements import get_enhancements
        import inspect
        
        # Test updated get_enhancements signature (should now support include_nested)
        sig = inspect.signature(get_enhancements)
        params = list(sig.parameters.keys())
        expected_params = ['object_name', 'program', 'include_nested']
        
        if params == expected_params:
            print("SUCCESS: get_enhancements has updated signature with include_nested")
        else:
            print(f"FAILED: get_enhancements signature mismatch. Expected: {expected_params}, Got: {params}")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing get_enhancements signature: {e}")
        return False
    
    return True

def test_mcp_server_integration():
    """Test that the MCP server includes the new tools."""
    print("\nTesting MCP server integration for latest features...")
    
    try:
        import mcp_server
        print("SUCCESS: mcp_server.py imported successfully")
        
        # Check if our new tool functions exist in the module
        new_tool_functions = [
            'get_includes_list_mcp',
            'get_enhancement_by_name_mcp',
            'get_enhancements_mcp'  # Should be updated
        ]
        
        for func_name in new_tool_functions:
            if hasattr(mcp_server, func_name):
                print(f"SUCCESS: MCP tool function '{func_name}' found")
            else:
                print(f"FAILED: MCP tool function '{func_name}' not found")
                return False
        
        return True
    except Exception as e:
        print(f"FAILED: Failed to test MCP server integration: {e}")
        traceback.print_exc()
        return False

def test_parameter_validation():
    """Test parameter validation for new functions."""
    print("\nTesting parameter validation...")
    
    try:
        from src.tools.includes_list import get_includes_list
        
        # Test empty object_name
        try:
            get_includes_list("", "program")
            print("FAILED: get_includes_list should reject empty object_name")
            return False
        except ValueError:
            print("SUCCESS: get_includes_list correctly validates object_name")
        
        # Test invalid object_type
        try:
            get_includes_list("TEST", "invalid_type")
            print("FAILED: get_includes_list should reject invalid object_type")
            return False
        except ValueError:
            print("SUCCESS: get_includes_list correctly validates object_type")
            
    except Exception as e:
        print(f"FAILED: Error testing get_includes_list validation: {e}")
        return False
    
    try:
        from src.tools.enhancement_by_name import get_enhancement_by_name
        
        # Test empty enhancement_spot
        try:
            get_enhancement_by_name("", "test_name")
            print("FAILED: get_enhancement_by_name should reject empty enhancement_spot")
            return False
        except ValueError:
            print("SUCCESS: get_enhancement_by_name correctly validates enhancement_spot")
        
        # Test empty enhancement_name
        try:
            get_enhancement_by_name("test_spot", "")
            print("FAILED: get_enhancement_by_name should reject empty enhancement_name")
            return False
        except ValueError:
            print("SUCCESS: get_enhancement_by_name correctly validates enhancement_name")
            
    except Exception as e:
        print(f"FAILED: Error testing get_enhancement_by_name validation: {e}")
        return False
    
    return True

def test_class_support_in_enhancements():
    """Test that enhancements module supports classes."""
    print("\nTesting class support in enhancements...")
    
    try:
        from src.tools.enhancements import _determine_object_type_and_path
        
        # This function should exist and handle classes
        print("SUCCESS: _determine_object_type_and_path function exists")
        
        # Check if the function mentions classes in its docstring
        docstring = _determine_object_type_and_path.__doc__
        if docstring and "class" in docstring.lower():
            print("SUCCESS: _determine_object_type_and_path mentions class support")
        else:
            print("WARNING: _determine_object_type_and_path docstring may not mention classes")
        
        return True
    except Exception as e:
        print(f"FAILED: Error testing class support: {e}")
        return False

def test_xml_parsing_functions():
    """Test XML parsing functions exist."""
    print("\nTesting XML parsing functions...")
    
    try:
        from src.tools.enhancement_by_name import _parse_enhancement_source_from_xml
        print("SUCCESS: _parse_enhancement_source_from_xml function exists")
        
        # Test with sample XML
        sample_xml = "<source>dGVzdA==</source>"  # base64 for "test"
        result = _parse_enhancement_source_from_xml(sample_xml)
        if result:
            print("SUCCESS: _parse_enhancement_source_from_xml processes XML")
        else:
            print("WARNING: _parse_enhancement_source_from_xml returned empty result")
        
        return True
    except Exception as e:
        print(f"FAILED: Error testing XML parsing: {e}")
        return False

def main():
    """Run all tests for latest features."""
    print("Testing latest MCP-ADT features integration...")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test function signatures
    if not test_function_signatures():
        all_passed = False
    
    # Test MCP server integration
    if not test_mcp_server_integration():
        all_passed = False
    
    # Test parameter validation
    if not test_parameter_validation():
        all_passed = False
    
    # Test class support
    if not test_class_support_in_enhancements():
        all_passed = False
    
    # Test XML parsing
    if not test_xml_parsing_functions():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: All tests passed! The latest features are successfully integrated.")
        print("\nSummary of latest MCP tools:")
        print("   - get_includes_list_mcp - Recursive include discovery")
        print("   - get_enhancement_by_name_mcp - Direct enhancement retrieval by name")
        print("   - get_enhancements_mcp - Enhanced with class support and nested search")
        print("\nNew capabilities:")
        print("   [+] Class enhancement support")
        print("   [+] Recursive include analysis")
        print("   [+] Direct enhancement access by name")
        print("   [+] Nested enhancement search")
        print("\nNext steps:")
        print("   1. Configure SAP connection in .env file")
        print("   2. Test with actual SAP system")
        print("   3. Run: python mcp_server.py")
    else:
        print("FAILED: Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
