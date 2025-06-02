#!/usr/bin/env python3
"""
Test script to verify XML parsing functionality for enhancement features.
This script tests the XML parsing logic with sample data.
"""

import sys
import base64
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def test_base64_xml_parsing():
    """Test parsing of base64 encoded enhancement XML."""
    print("Testing base64 XML parsing...")
    
    try:
        from src.tools.enhancement_by_name import _parse_enhancement_source_from_xml
        
        # Create sample ABAP code
        sample_abap_code = """DATA: lv_test TYPE string.
lv_test = 'Hello World'.
WRITE: / lv_test."""
        
        # Encode to base64
        encoded_code = base64.b64encode(sample_abap_code.encode('utf-8')).decode('utf-8')
        
        # Create sample XML with base64 encoded source
        sample_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<enhancement:source xmlns:enhancement="http://www.sap.com/adt/enhancement">
    <source>{encoded_code}</source>
</enhancement:source>"""
        
        result = _parse_enhancement_source_from_xml(sample_xml)
        
        if sample_abap_code in result:
            print("SUCCESS: Base64 XML parsing works correctly")
            print(f"Decoded ABAP code: {result[:50]}...")
            return True
        else:
            print(f"FAILED: Expected ABAP code not found in result: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing base64 XML parsing: {e}")
        return False

def test_cdata_xml_parsing():
    """Test parsing of CDATA enhancement XML."""
    print("\nTesting CDATA XML parsing...")
    
    try:
        from src.tools.enhancement_by_name import _parse_enhancement_source_from_xml
        
        # Create sample ABAP code
        sample_abap_code = """DATA: lv_counter TYPE i.
DO 10 TIMES.
  lv_counter = lv_counter + 1.
ENDDO."""
        
        # Create sample XML with CDATA
        sample_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<enhancement:source xmlns:enhancement="http://www.sap.com/adt/enhancement">
    <source><![CDATA[{sample_abap_code}]]></source>
</enhancement:source>"""
        
        result = _parse_enhancement_source_from_xml(sample_xml)
        
        if sample_abap_code in result:
            print("SUCCESS: CDATA XML parsing works correctly")
            print(f"Extracted ABAP code: {result[:50]}...")
            return True
        else:
            print(f"FAILED: Expected ABAP code not found in result: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing CDATA XML parsing: {e}")
        return False

def test_enh_source_xml_parsing():
    """Test parsing of enh:source XML format."""
    print("\nTesting enh:source XML parsing...")
    
    try:
        from src.tools.enhancement_by_name import _parse_enhancement_source_from_xml
        
        # Create sample ABAP code
        sample_abap_code = """ENHANCEMENT-POINT ztest_enhancement.
DATA: lv_enhanced TYPE string.
lv_enhanced = 'Enhanced functionality'.
END-ENHANCEMENT-POINT."""
        
        # Encode to base64
        encoded_code = base64.b64encode(sample_abap_code.encode('utf-8')).decode('utf-8')
        
        # Create sample XML with enh:source format
        sample_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<enhancement:implementation xmlns:enhancement="http://www.sap.com/adt/enhancement">
    <enh:source>{encoded_code}</enh:source>
</enhancement:implementation>"""
        
        result = _parse_enhancement_source_from_xml(sample_xml)
        
        if sample_abap_code in result:
            print("SUCCESS: enh:source XML parsing works correctly")
            print(f"Extracted enhancement code: {result[:50]}...")
            return True
        else:
            print(f"FAILED: Expected ABAP code not found in result: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing enh:source XML parsing: {e}")
        return False

def test_fallback_xml_parsing():
    """Test fallback behavior when no recognized format is found."""
    print("\nTesting fallback XML parsing...")
    
    try:
        from src.tools.enhancement_by_name import _parse_enhancement_source_from_xml
        
        # Create sample XML without recognized source tags
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<unknown:format xmlns:unknown="http://www.sap.com/adt/unknown">
    <content>Some unrecognized content</content>
</unknown:format>"""
        
        result = _parse_enhancement_source_from_xml(sample_xml)
        
        if result == sample_xml:
            print("SUCCESS: Fallback XML parsing returns original XML")
            return True
        else:
            print(f"FAILED: Fallback should return original XML, got: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing fallback XML parsing: {e}")
        return False

def test_enhancement_list_xml_parsing():
    """Test parsing of enhancement list XML from enhancements.py."""
    print("\nTesting enhancement list XML parsing...")
    
    try:
        from src.tools.enhancements import _parse_enhancements_from_xml
        
        # Create sample enhancement list XML
        sample_abap_code1 = "DATA: lv_enh1 TYPE string."
        sample_abap_code2 = "DATA: lv_enh2 TYPE string."
        
        encoded_code1 = base64.b64encode(sample_abap_code1.encode('utf-8')).decode('utf-8')
        encoded_code2 = base64.b64encode(sample_abap_code2.encode('utf-8')).decode('utf-8')
        
        sample_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<enhancement:elements xmlns:enhancement="http://www.sap.com/adt/enhancement">
    <enhancement:element adtcore:name="enhancement_1" adtcore:type="enhancement_impl">
        <enh:source>{encoded_code1}</enh:source>
    </enhancement:element>
    <enhancement:element adtcore:name="enhancement_2" adtcore:type="enhancement_impl">
        <enh:source>{encoded_code2}</enh:source>
    </enhancement:element>
</enhancement:elements>"""
        
        result = _parse_enhancements_from_xml(sample_xml)
        
        if len(result) == 2:
            print(f"SUCCESS: Enhancement list parsing found {len(result)} enhancements")
            for i, enh in enumerate(result):
                print(f"  Enhancement {i+1}: {enh.name} ({enh.type})")
            return True
        else:
            print(f"FAILED: Expected 2 enhancements, got {len(result)}")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing enhancement list XML parsing: {e}")
        return False

def main():
    """Run all XML parsing tests."""
    print("Testing Enhancement XML Parsing Functionality...")
    print("=" * 60)
    
    all_passed = True
    
    # Test base64 XML parsing
    if not test_base64_xml_parsing():
        all_passed = False
    
    # Test CDATA XML parsing
    if not test_cdata_xml_parsing():
        all_passed = False
    
    # Test enh:source XML parsing
    if not test_enh_source_xml_parsing():
        all_passed = False
    
    # Test fallback XML parsing
    if not test_fallback_xml_parsing():
        all_passed = False
    
    # Test enhancement list XML parsing
    if not test_enhancement_list_xml_parsing():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: All XML parsing tests passed!")
        print("\nXML parsing capabilities verified:")
        print("   [+] Base64 encoded source code")
        print("   [+] CDATA wrapped source code")
        print("   [+] enh:source format")
        print("   [+] Fallback to raw XML")
        print("   [+] Enhancement list parsing")
        print("\nThe enhancement XML parsing is robust and handles multiple formats.")
    else:
        print("FAILED: Some XML parsing tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
