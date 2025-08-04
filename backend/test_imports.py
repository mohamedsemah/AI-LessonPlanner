#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from app.models.udl_content import SlideContent, CourseContentRequest
        print("✅ UDL content models imported successfully")
        
        from app.services.udl_content_service import UDLContentService
        print("✅ UDL content service imported successfully")
        
        from app.services.slide_design_service import SlideDesignService
        print("✅ Slide design service imported successfully")
        
        from app.services.export_service import ExportService
        print("✅ Export service imported successfully")
        
        from app.routers.udl_content import router
        print("✅ UDL content router imported successfully")
        
        from app.main import app
        print("✅ Main app imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 