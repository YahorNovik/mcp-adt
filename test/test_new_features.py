#!/usr/bin/env python3
"""
Test script to verify the new MCP tools are properly integrated.
This script tests the imports and basic functionality without requiring SAP connection.
"""

import sys
import traceback

def test_imports():
    """Test that all new modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from src.tools.table_contents import get_table_contents
        print("SUCCESS: table_contents.py imported successfully")
    except Exception as e:
        print(f"FAILED: Failed to import table_contents: {e}")
        return False
    
    try:
        from src.tools.sql_query import get_sql_query
        print("SUCCESS: sql_query.py imported successfully")
    except Exception as e:
        print(f"FAILED: Failed to import sql_query: {e}")
        return False
    
    try:
        from src.tools.enhancements import get_enhancements
        print("SUCCESS: enhancements.py imported successfully")
    except Exception as e:
        print(f"FAILED: Failed to import enhancements: {e}")
        return False
    
    return True

def test_mcp_server():
    """Test that the MCP server can be imported with all tools."""
    print("\nTesting MCP server integration...")
    
    try:
        import mcp_server
        print("SUCCESS: mcp_server.py imported successfully")
        
        # Check if the FastMCP instance exists
        if hasattr(mcp_server, 'mcp'):
            print("SUCCESS: FastMCP instance created")
            
            # Check if our new tool functions exist in the module
            new_tool_functions = [
                'get_table_contents_mcp',
                'get_sql_query_mcp', 
                'get_enhancements_mcp'
            ]
            
            for func_name in new_tool_functions:
                if hasattr(mcp_server, func_name):
                    print(f"SUCCESS: MCP tool function '{func_name}' found")
                else:
                    print(f"FAILED: MCP tool function '{func_name}' not found")
                    return False
            
        return True
    except Exception as e:
        print(f"FAILED: Failed to test MCP server: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that required dependencies are available."""
    print("\nTesting dependencies...")
    
    try:
        import xmltodict
        print("SUCCESS: xmltodict dependency available")
    except ImportError:
        print("FAILED: xmltodict dependency missing")
        return False
    
    try:
        import requests
        print("SUCCESS: requests dependency available")
    except ImportError:
        print("FAILED: requests dependency missing")
        return False
    
    try:
        from dotenv import load_dotenv
        print("SUCCESS: python-dotenv dependency available")
    except ImportError:
        print("FAILED: python-dotenv dependency missing")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Testing new MCP-ADT features integration...")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test dependencies
    if not test_dependencies():
        all_passed = False
    
    # Test MCP server
    if not test_mcp_server():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("SUCCESS: All tests passed! The new features are successfully integrated.")
        print("\nSummary of new MCP tools:")
        print("   - get_table_contents_mcp - Enhanced table data retrieval")
        print("   - get_sql_query_mcp - Freestyle SQL execution")
        print("   - get_enhancements_mcp - Enhancement implementation discovery")
        print("\nNext steps:")
        print("   1. Configure SAP connection in .env file")
        print("   2. Test with actual SAP system")
        print("   3. Run: python mcp_server.py")
    else:
        print("FAILED: Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
