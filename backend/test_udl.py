#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.udl_content_service import UDLContentService
    print("✅ UDLContentService imported successfully")
    
    # Test instantiation
    service = UDLContentService()
    print("✅ UDLContentService instantiated successfully")
    
    # Test initialization
    print(f"✅ UDL guidelines initialized: {len(service.udl_guidelines)} principles")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 