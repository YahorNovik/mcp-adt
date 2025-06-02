#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from tools.table_contents import get_table_contents

def test_zok_d_phase():
    """Test reading ZOK_D_PHASE table contents"""
    print("=== Testing ZOK_D_PHASE Table Contents ===")
    
    try:
        result = get_table_contents("ZOK_D_PHASE", max_rows=10)
        
        print(f"✅ Success!")
        print(f"Table: {result.get('table_name')}")
        print(f"Total rows: {result.get('total_rows')}")
        print(f"Retrieved rows: {result.get('row_count')}")
        print(f"Execution time: {result.get('execution_time')}ms")
        
        print("\n📊 Columns:")
        for col in result.get('columns', []):
            print(f"  - {col['name']} ({col['type']}) - {col.get('description', '')}")
        
        print("\n📋 Sample rows:")
        for i, row in enumerate(result.get('rows', [])[:3]):
            print(f"  Row {i+1}: {row}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_zok_d_phase()
    sys.exit(0 if success else 1)
