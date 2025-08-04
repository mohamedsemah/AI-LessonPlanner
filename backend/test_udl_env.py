#!/usr/bin/env python3

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY found: {api_key[:10]}...")
    else:
        print("❌ OPENAI_API_KEY not found")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'OPENAI' in key or 'API' in key:
                print(f"  {key}: {value[:10] if value else 'None'}...")
    
    from app.services.udl_content_service import UDLContentService
    print("✅ UDLContentService imported successfully")
    
    # Test instantiation
    service = UDLContentService()
    print("✅ UDLContentService instantiated successfully")
    
    # Test initialization
    print(f"✅ UDL guidelines initialized: {len(service.udl_guidelines)} principles")
    
    # Test a simple method
    features = service._extract_accessibility_features([])
    print(f"✅ Method test passed: {features}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 