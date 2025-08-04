#!/usr/bin/env python3

import sys
import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_endpoint():
    try:
        # Test if the server is running
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get("http://localhost:8000/health")
            print(f"✅ Health endpoint: {response.status_code}")
            
            # Test UDL guidelines endpoint
            response = await client.get("http://localhost:8000/api/udl-content/udl-guidelines")
            print(f"✅ UDL guidelines endpoint: {response.status_code}")
            
            # Test content modalities endpoint
            response = await client.get("http://localhost:8000/api/udl-content/content-modalities")
            print(f"✅ Content modalities endpoint: {response.status_code}")
            
            # Test accessibility features endpoint
            response = await client.get("http://localhost:8000/api/udl-content/accessibility-features")
            print(f"✅ Accessibility features endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint()) 