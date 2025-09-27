#!/usr/bin/env python3
"""
Test the BuzzBrief API endpoints
"""
import asyncio
import json
import httpx
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    print("🌐 Testing Root Endpoint")
    print("-" * 40)
    
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_health_endpoint():
    """Test health check endpoints"""
    print("🏥 Testing Health Endpoints")
    print("-" * 40)
    
    # Basic health check
    response = client.get("/health")
    print(f"Health Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Detailed health check
    response = client.get("/health/dependencies")
    print(f"Dependencies Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_video_generation():
    """Test single video generation"""
    print("🎬 Testing Video Generation Endpoint")
    print("-" * 40)
    
    # Sample email data
    email_data = {
        "id": "test_email_123",
        "from": "sarah@techcorp.com",
        "subject": "URGENT: Server Down!",
        "body": "Hi team, our main server is down and customers are complaining. Emergency meeting in 10 minutes!",
        "timestamp": "2024-01-15T14:30:00Z"
    }
    
    print(f"Input Email:")
    print(f"  From: {email_data['from']}")
    print(f"  Subject: {email_data['subject']}")
    print(f"  Body: {email_data['body'][:50]}...")
    print()
    
    response = client.post("/api/generate-video", json=email_data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_batch_generation():
    """Test batch video generation"""
    print("📦 Testing Batch Video Generation")
    print("-" * 40)
    
    # Sample batch data
    batch_data = {
        "emails": [
            {
                "id": "email_1",
                "from": "boss@company.com",
                "subject": "Meeting Tomorrow",
                "body": "Team meeting at 2 PM tomorrow about quarterly reports."
            },
            {
                "id": "email_2",
                "from": "client@business.com", 
                "subject": "Project Update",
                "body": "Here's the latest update on the website redesign project."
            },
            {
                "id": "email_3",
                "from": "hr@company.com",
                "subject": "New Policy",
                "body": "Please review the new remote work policy attached."
            }
        ]
    }
    
    print(f"Processing {len(batch_data['emails'])} emails...")
    
    response = client.post("/api/generate-batch", json=batch_data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all API tests"""
    print("🚀 BuzzBrief API Testing")
    print("=" * 50)
    print()
    
    test_root_endpoint()
    test_health_endpoint()
    test_video_generation()
    test_batch_generation()
    
    print("=" * 50)
    print("✅ API Testing Complete!")
    print()
    print("📝 Summary:")
    print("  • Root endpoint provides API overview")
    print("  • Health endpoints show system status")
    print("  • /api/generate-video converts single email to video")
    print("  • /api/generate-batch processes multiple emails")
    print()
    print("🌐 To start the server: uvicorn app.main:app --reload")
    print("📚 API docs available at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()