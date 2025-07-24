#!/usr/bin/env python3
"""
Quick test script to verify the Claude Memory API is working
"""

import requests
import json
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:8080"

def test_health():
    """Test the health endpoint"""
    try:
        print("Testing API health...")
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"API is healthy!")
            print(f"   Status: {data['data']['status']}")
            print(f"   Documents: {data['data']['database']['document_count']}")
            print(f"   Uptime: {data['data']['performance'].get('uptime_seconds', 0):.1f}s")
            return True
        else:
            print(f"Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API server at http://localhost:8080")
        print("   Make sure the server is running with: python memory_api_server.py")
        return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_search(query="python development"):
    """Test the search endpoint"""
    try:
        print(f"Testing search for: '{query}'")
        
        search_data = {
            "query": query,
            "max_results": 3,
            "similarity_threshold": 0.1  # Lower threshold for more results
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/search",
            headers={"Content-Type": "application/json"},
            json=search_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                results = data['data']['results']
                print(f"Search successful!")
                print(f"   Found: {len(results)} results in {data['data']['search_time_ms']}ms")
                
                for i, result in enumerate(results, 1):
                    print(f"   {i}. {result['title']} ({result['similarity']*100:.1f}% similarity)")
                    print(f"      Date: {result['date']} | Technologies: {result['metadata'].get('technologies', [])}")
                    print(f"      Preview: {result['preview'][:100]}...")
                    print()
                
                return True
            else:
                print(f"Search failed: {data.get('error', {}).get('message', 'Unknown error')}")
                return False
        else:
            print(f"Search request failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Search error: {e}")
        return False

def test_add_memory():
    """Test adding a new memory"""
    try:
        print("Testing add memory...")
        
        memory_data = {
            "content": f"Test memory created at {datetime.now().isoformat()} for API validation. This memory contains information about testing the Claude Memory API system with various queries and ensuring the search functionality works correctly.",
            "title": "API Test Memory",
            "source": "claude_code",
            "technologies": ["python", "api", "testing", "memory"],
            "complexity": "low",
            "project": "memory-api-testing"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/add_memory",
            headers={"Content-Type": "application/json"},
            json=memory_data,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            if data['success']:
                print(f"Memory added successfully!")
                print(f"   ID: {data['data']['id']}")
                print(f"   Title: {data['data']['title']}")
                return data['data']['id']
            else:
                print(f"Add memory failed: {data.get('error', {}).get('message', 'Unknown error')}")
                return None
        else:
            print(f"Add memory request failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Add memory error: {e}")
        return None

def main():
    """Run all tests"""
    print("Claude Memory API - Quick Test")
    print("=" * 50)
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\nAPI server is not running or not responding")
        print("Please start the server with one of these methods:")
        print("  1. python memory_api_server.py")
        print("  2. .\\Start-MemoryAPI.ps1")
        print("  3. start_memory_api.bat")
        sys.exit(1)
    
    print()
    
    # Test 2: Search existing memories
    test_search("python development")
    print()
    
    # Test 3: Add a new memory
    memory_id = test_add_memory()
    print()
    
    # Test 4: Search for the memory we just added
    if memory_id:
        test_search("API test memory")
        print()
    
    print("All tests completed!")
    print("\nTry these commands:")
    print("PowerShell:")
    print("  Import-Module .\\ClaudeMemory.psm1")
    print("  Search-ClaudeMemory 'your query here'")
    print("\nCommand line:")
    print("  curl -X POST http://localhost:8080/api/search \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"query\": \"your query\", \"max_results\": 3}'")

if __name__ == "__main__":
    main()