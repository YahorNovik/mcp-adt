#!/usr/bin/env python3
"""
Comprehensive test suite for all latest MCP-ADT features.
This script runs all tests for the new functionality added from Node.js project.
"""

import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def run_test_script(script_name):
    """Run a test script and return success status."""
    print(f"\n{'='*80}")
    print(f"RUNNING: {script_name}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"[PASS] {script_name} PASSED")
            return True
        else:
            print(f"[FAIL] {script_name} FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {script_name} TIMED OUT")
        return False
    except Exception as e:
        print(f"[ERROR] {script_name} ERROR: {e}")
        return False

def main():
    """Run all test scripts."""
    print("🚀 COMPREHENSIVE TEST SUITE FOR LATEST MCP-ADT FEATURES")
    print("=" * 80)
    print("Testing all new functionality transferred from Node.js project:")
    print("  • GetIncludesList - Recursive include discovery")
    print("  • GetEnhancementByName - Direct enhancement retrieval")
    print("  • Enhanced GetEnhancements - Class support & nested search")
    print("  • XML Parsing - Multiple format support")
    
    test_scripts = [
        "test/test_latest_features.py",
        "test/test_enhancement_xml_parsing.py"
    ]
    
    results = {}
    
    for script in test_scripts:
        script_path = project_root / script
        if script_path.exists():
            results[script] = run_test_script(script)
        else:
            print(f"❌ Test script not found: {script}")
            results[script] = False
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for script, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {script}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("\n[+] Latest features successfully integrated:")
        print("   - Class enhancement support")
        print("   - Recursive include analysis") 
        print("   - Direct enhancement access by name")
        print("   - Robust XML parsing")
        print("   - Comprehensive error handling")
        print("   - Parameter validation")
        print("\n[READY] Ready for production use!")
        print("\nNext steps:")
        print("   1. Configure SAP connection in .env file")
        print("   2. Test with real SAP system")
        print("   3. Deploy MCP server: python mcp_server.py")
        return True
    else:
        print(f"\n❌ {total - passed} test suite(s) failed")
        print("Please review the errors above and fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
