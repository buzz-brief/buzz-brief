#!/usr/bin/env python3
"""
Test script for the FastAPI endpoint to process emails.
This tests the /process-email endpoint with real email data.
"""

import requests
import json
import time
import sys

def test_process_email_endpoint(base_url="http://localhost:8000"):
    """Test the /process-email endpoint."""
    
    # Test email data
    test_email = {
        "id": "test_email_123",
        "from": "manager@company.com",
        "subject": "Weekly Team Standup Tomorrow",
        "body": """
        Hi team,
        
        Just a reminder that we have our weekly standup meeting tomorrow at 10 AM.
        Please come prepared with:
        - Your progress updates
        - Any blockers you're facing
        - Plans for the upcoming week
        
        Looking forward to seeing everyone there!
        
        Best,
        Alex
        """
    }
    
    print("🧪 Testing /process-email endpoint...")
    print(f"Base URL: {base_url}")
    
    try:
        # Test health endpoint first
        print("\n1. Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {health_response.json()}")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
            return False
        
        # Test process-email endpoint
        print("\n2. Testing /process-email endpoint...")
        print(f"   Email: {test_email['subject']}")
        
        response = requests.post(
            f"{base_url}/process-email",
            json=test_email,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email processing successful!")
            print(f"   Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Email processing failed")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server")
        print("   Make sure the FastAPI server is running:")
        print("   cd backend && python -m app.main")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_multiple_emails_endpoint(base_url="http://localhost:8000"):
    """Test the /process-emails endpoint with multiple emails."""
    
    test_emails = [
        {
            "id": "email_1",
            "from": "boss@work.com",
            "subject": "Meeting Tomorrow",
            "body": "We need to discuss the quarterly reports tomorrow at 2 PM."
        },
        {
            "id": "email_2", 
            "from": "friend@gmail.com",
            "subject": "Weekend Plans",
            "body": "Want to grab dinner this weekend?"
        }
    ]
    
    print("\n3. Testing /process-emails endpoint...")
    
    try:
        response = requests.post(
            f"{base_url}/process-emails",
            json=test_emails,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Batch email processing successful!")
            print(f"   Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Batch email processing failed")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False


def start_server_if_needed():
    """Check if server is running and provide instructions to start it."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is already running")
            return True
    except:
        pass
    
    print("❌ Server is not running")
    print("\nTo start the server, run:")
    print("cd /Users/rishimanimaran/Documents/Work/buzzBrief/backend")
    print("python -m app.main")
    print("\nOr with uvicorn:")
    print("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    return False


if __name__ == "__main__":
    print("🚀 API Endpoint Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not start_server_if_needed():
        sys.exit(1)
    
    # Run tests
    success1 = test_process_email_endpoint()
    success2 = test_multiple_emails_endpoint()
    
    if success1 and success2:
        print("\n🎉 All API tests passed!")
    else:
        print("\n💥 Some API tests failed!")
        sys.exit(1)

