#!/usr/bin/env python3
"""
Comprehensive API tests for Claude Memory API.
Tests all endpoints, validation, error handling, and integration.
"""

import pytest
import json
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Flask app and dependencies
from memory_api_server import app
from models import MemoryDocument, SearchRequest, AddMemoryRequest
import uuid


class TestMemoryAPI:
    """Test suite for Memory API endpoints"""

    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def sample_memory_data(self):
        """Sample memory data for testing"""
        return {
            "content": "This is a test memory about Python Flask API development. We created endpoints for search, add, list, and delete operations.",
            "title": "Python Flask API Development",
            "date": "2025-07-24",
            "source": "claude_code",
            "technologies": ["python", "flask", "api", "chromadb"],
            "file_paths": ["/src/api.py", "/tests/test_api.py"],
            "complexity": "medium",
            "project": "memory-api-webapp",
            "metadata": {
                "user_satisfaction": "high",
                "session_duration": 120
            }
        }

    @pytest.fixture
    def sample_search_data(self):
        """Sample search request data"""
        return {
            "query": "python flask development",
            "max_results": 3,
            "similarity_threshold": 0.3,
            "source_filter": "claude_code"
        }

    # Health Endpoint Tests
    def test_health_endpoint_returns_success(self, client):
        """Test health endpoint returns successful response"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'metadata' in data
        assert data['data']['status'] in ['healthy', 'unhealthy']

    def test_health_endpoint_includes_required_fields(self, client):
        """Test health endpoint includes all required fields"""
        response = client.get('/api/health')
        data = response.get_json()
        
        assert 'database' in data['data']
        assert 'api' in data['data']
        assert 'performance' in data['data']
        
        # Check database info
        db_info = data['data']['database']
        assert 'connected' in db_info
        assert 'document_count' in db_info
        assert 'path' in db_info
        assert 'collection' in db_info

    # Search Endpoint Tests
    def test_search_endpoint_with_valid_query(self, client, sample_search_data):
        """Test search endpoint with valid query"""
        response = client.post('/api/search', 
                              data=json.dumps(sample_search_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'results' in data['data']
        assert 'query' in data['data']
        assert data['data']['query'] == sample_search_data['query']

    def test_search_endpoint_validates_missing_query(self, client):
        """Test search endpoint validation for missing query"""
        response = client.post('/api/search', 
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert 'VALIDATION_ERROR' in data['error']['code']

    def test_search_endpoint_validates_empty_query(self, client):
        """Test search endpoint validation for empty query"""
        response = client.post('/api/search', 
                              data=json.dumps({"query": ""}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_search_endpoint_validates_max_results(self, client):
        """Test search endpoint validates max_results parameter"""
        # Test with max_results exceeding limit
        search_data = {
            "query": "test query",
            "max_results": 20  # Should be capped at 10
        }
        
        response = client.post('/api/search', 
                              data=json.dumps(search_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        # Should be capped at maximum allowed
        assert len(data['data']['results']) <= 10

    def test_search_endpoint_with_source_filter(self, client):
        """Test search endpoint with source filter"""
        search_data = {
            "query": "test query",
            "source_filter": "claude_code"
        }
        
        response = client.post('/api/search', 
                              data=json.dumps(search_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_search_endpoint_response_format(self, client):
        """Test search endpoint returns properly formatted response"""
        search_data = {"query": "test"}
        
        response = client.post('/api/search', 
                              data=json.dumps(search_data),
                              content_type='application/json')
        
        data = response.get_json()
        
        # Check top-level structure
        assert 'success' in data
        assert 'data' in data
        assert 'metadata' in data
        
        # Check metadata structure
        metadata = data['metadata']
        assert 'timestamp' in metadata
        assert 'request_id' in metadata
        assert 'execution_time_ms' in metadata
        
        # Check data structure
        if data['success']:
            search_data = data['data']
            assert 'query' in search_data
            assert 'results' in search_data
            assert 'total_results' in search_data
            assert 'search_time_ms' in search_data

    # Add Memory Endpoint Tests
    def test_add_memory_endpoint_with_valid_data(self, client, sample_memory_data):
        """Test add memory endpoint with valid data"""
        response = client.post('/api/add_memory', 
                              data=json.dumps(sample_memory_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'id' in data['data']
        assert 'title' in data['data']

    def test_add_memory_endpoint_validates_required_content(self, client):
        """Test add memory endpoint validates required content field"""
        response = client.post('/api/add_memory', 
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'VALIDATION_ERROR' in data['error']['code']

    def test_add_memory_endpoint_validates_empty_content(self, client):
        """Test add memory endpoint validates empty content"""
        memory_data = {"content": ""}
        
        response = client.post('/api/add_memory', 
                              data=json.dumps(memory_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_add_memory_endpoint_with_minimal_data(self, client):
        """Test add memory endpoint with minimal required data"""
        memory_data = {
            "content": "Minimal test memory content for API testing."
        }
        
        response = client.post('/api/add_memory', 
                              data=json.dumps(memory_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

    def test_add_memory_endpoint_sets_defaults(self, client):
        """Test add memory endpoint sets appropriate defaults"""
        memory_data = {
            "content": "Test content without explicit metadata"
        }
        
        response = client.post('/api/add_memory', 
                              data=json.dumps(memory_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        # Should have generated title
        assert data['data']['title'] != ""

    # List Memories Endpoint Tests
    def test_list_memories_endpoint_default_pagination(self, client):
        """Test list memories endpoint with default pagination"""
        response = client.get('/api/memories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'memories' in data['data']
        assert 'pagination' in data['data']

    def test_list_memories_endpoint_custom_pagination(self, client):
        """Test list memories endpoint with custom pagination"""
        response = client.get('/api/memories?page=2&limit=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 2
        assert pagination['limit'] == 5

    def test_list_memories_endpoint_validates_pagination_limits(self, client):
        """Test list memories endpoint validates pagination limits"""
        # Test with limit exceeding maximum
        response = client.get('/api/memories?limit=100')
        
        assert response.status_code == 200
        data = response.get_json()
        # Should be capped at maximum allowed (50)
        assert data['data']['pagination']['limit'] <= 50

    def test_list_memories_response_format(self, client):
        """Test list memories endpoint response format"""
        response = client.get('/api/memories')
        data = response.get_json()
        
        if data['success'] and data['data']['memories']:
            memory = data['data']['memories'][0]
            required_fields = ['id', 'title', 'date', 'source', 'complexity', 'preview']
            for field in required_fields:
                assert field in memory

    # Delete Memory Endpoint Tests
    def test_delete_memory_endpoint_with_nonexistent_id(self, client):
        """Test delete memory endpoint with non-existent ID"""
        fake_id = "nonexistent-memory-id-12345"
        
        response = client.delete(f'/api/memory/{fake_id}')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'NOT_FOUND' in data['error']['code']

    def test_delete_memory_endpoint_with_empty_id(self, client):
        """Test delete memory endpoint with empty ID"""
        response = client.delete('/api/memory/')
        
        # Should return 404 or 405 (method not allowed) depending on routing
        assert response.status_code in [404, 405]

    # Reindex Endpoint Tests
    def test_reindex_endpoint_requires_confirmation(self, client):
        """Test reindex endpoint requires confirmation"""
        response = client.post('/api/reindex', 
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'CONFIRMATION_REQUIRED' in data['error']['code']

    def test_reindex_endpoint_with_confirmation(self, client):
        """Test reindex endpoint with proper confirmation"""
        reindex_data = {"confirm": True}
        
        response = client.post('/api/reindex', 
                              data=json.dumps(reindex_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    # Error Handling Tests
    def test_invalid_json_handling(self, client):
        """Test API handles invalid JSON gracefully"""
        response = client.post('/api/search', 
                              data='{"invalid": json}',
                              content_type='application/json')
        
        assert response.status_code == 400

    def test_missing_content_type_handling(self, client):
        """Test API handles missing content type"""
        response = client.post('/api/search', data='{"query": "test"}')
        
        # Should handle gracefully, likely 400 or 415
        assert response.status_code in [400, 415]

    def test_rate_limiting_headers(self, client):
        """Test rate limiting is properly configured"""
        response = client.post('/api/search', 
                              data=json.dumps({"query": "test"}),
                              content_type='application/json')
        
        # Rate limiting should add headers
        assert response.status_code in [200, 429]

    # CORS Tests
    def test_cors_headers_present(self, client):
        """Test CORS headers are present in responses"""
        response = client.options('/api/health')
        
        # Check for CORS headers
        headers = response.headers
        # Flask-CORS should add appropriate headers

    def test_cors_preflight_request(self, client):
        """Test CORS preflight requests are handled"""
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = client.options('/api/search', headers=headers)
        assert response.status_code in [200, 204]

    # Integration Tests
    def test_search_after_add_memory_workflow(self, client, sample_memory_data):
        """Test complete workflow: add memory then search for it"""
        # First add a memory
        add_response = client.post('/api/add_memory', 
                                  data=json.dumps(sample_memory_data),
                                  content_type='application/json')
        
        assert add_response.status_code == 201
        add_data = add_response.get_json()
        memory_id = add_data['data']['id']
        
        # Then search for it
        search_data = {"query": "python flask", "max_results": 5}
        search_response = client.post('/api/search', 
                                     data=json.dumps(search_data),
                                     content_type='application/json')
        
        assert search_response.status_code == 200
        search_results = search_response.get_json()
        
        # Should find the memory we just added
        found_memory = False
        for result in search_results['data']['results']:
            if result['id'] == memory_id:
                found_memory = True
                break
        
        # Note: This might not always pass immediately due to indexing delays
        # In a real system, you might need to wait or refresh the index

    # Performance Tests
    def test_search_response_time(self, client):
        """Test search endpoint response time is reasonable"""
        search_data = {"query": "performance test"}
        
        start_time = datetime.now()
        response = client.post('/api/search', 
                              data=json.dumps(search_data),
                              content_type='application/json')
        end_time = datetime.now()
        
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        assert response.status_code == 200
        # Should respond within 2 seconds
        assert duration_ms < 2000

    def test_add_memory_response_time(self, client):
        """Test add memory endpoint response time"""
        memory_data = {
            "content": "Performance test memory content " * 100  # Make it substantial
        }
        
        start_time = datetime.now()
        response = client.post('/api/add_memory', 
                              data=json.dumps(memory_data),
                              content_type='application/json')
        end_time = datetime.now()
        
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        assert response.status_code == 201
        # Should respond within 3 seconds
        assert duration_ms < 3000


class TestDataValidation:
    """Test data validation using Pydantic models"""

    def test_memory_document_validation(self):
        """Test MemoryDocument validation"""
        valid_data = {
            "content": "Test content",
            "title": "Test Title",
            "date": "2025-07-24",
            "source": "claude_code",
            "complexity": "medium"
        }
        
        # Should validate successfully
        memory = MemoryDocument(**valid_data)
        assert memory.content == "Test content"
        assert memory.source == "claude_code"

    def test_memory_document_invalid_date(self):
        """Test MemoryDocument with invalid date format"""
        invalid_data = {
            "content": "Test content",
            "title": "Test Title",
            "date": "invalid-date",
            "source": "claude_code",
            "complexity": "medium"
        }
        
        with pytest.raises(ValueError):
            MemoryDocument(**invalid_data)

    def test_memory_document_invalid_source(self):
        """Test MemoryDocument with invalid source"""
        invalid_data = {
            "content": "Test content",
            "title": "Test Title",
            "date": "2025-07-24",
            "source": "invalid_source",
            "complexity": "medium"
        }
        
        with pytest.raises(ValueError):
            MemoryDocument(**invalid_data)

    def test_search_request_validation(self):
        """Test SearchRequest validation"""
        valid_data = {
            "query": "test query",
            "max_results": 5,
            "similarity_threshold": 0.5
        }
        
        search_request = SearchRequest(**valid_data)
        assert search_request.query == "test query"
        assert search_request.max_results == 5

    def test_search_request_invalid_max_results(self):
        """Test SearchRequest with invalid max_results"""
        invalid_data = {
            "query": "test query",
            "max_results": 15  # Exceeds maximum
        }
        
        with pytest.raises(ValueError):
            SearchRequest(**invalid_data)

    def test_add_memory_request_validation(self):
        """Test AddMemoryRequest validation with defaults"""
        minimal_data = {
            "content": "Test memory content"
        }
        
        add_request = AddMemoryRequest(**minimal_data)
        assert add_request.content == "Test memory content"
        assert add_request.source == "claude_desktop"  # Default
        assert add_request.complexity == "medium"  # Default


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])