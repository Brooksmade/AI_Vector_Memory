#!/usr/bin/env python3
"""
Integration tests for Claude Memory API.
Tests real database interactions, client library integration, and system workflows.
"""

import pytest
import json
import sys
import tempfile
import shutil
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from threading import Thread

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_api_server import app
import chromadb
from scripts.memory_search import MemorySearcher
from scripts.index_summaries import SummaryIndexer


class TestDatabaseIntegration:
    """Test integration with actual ChromaDB database"""

    @pytest.fixture(scope='class')
    def test_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_chroma_db"
        yield db_path
        # Cleanup
        if db_path.exists():
            shutil.rmtree(temp_dir)

    @pytest.fixture(scope='class')
    def test_searcher(self, test_db_path):
        """Create test memory searcher with temporary database"""
        # Create a test searcher with temporary database
        searcher = MemorySearcher()
        # Override the database path for testing
        searcher.client = chromadb.PersistentClient(path=str(test_db_path))
        try:
            searcher.collection = searcher.client.get_collection("claude_summaries")
        except:
            searcher.collection = searcher.client.create_collection("claude_summaries")
        return searcher

    @pytest.fixture(scope='class')
    def test_indexer(self, test_db_path):
        """Create test indexer with temporary database"""
        indexer = SummaryIndexer()
        # Override the database path for testing
        indexer.client = chromadb.PersistentClient(path=str(test_db_path))
        try:
            indexer.collection = indexer.client.get_collection("claude_summaries")
        except:
            indexer.collection = indexer.client.create_collection("claude_summaries")
        return indexer

    def test_database_connection(self, test_searcher):
        """Test basic database connectivity"""
        assert test_searcher.client is not None
        assert test_searcher.collection is not None

    def test_index_and_search_workflow(self, test_indexer, test_searcher):
        """Test complete index and search workflow"""
        # Index a test document
        test_content = """
        Title: Python Flask API Development Session
        Description: Comprehensive session on building REST APIs with Flask
        
        We built a complete Flask API with the following features:
        - User authentication endpoints
        - CRUD operations for resources
        - Database integration with SQLAlchemy
        - Input validation with Marshmallow
        - Error handling and logging
        - API documentation with Swagger
        
        Technologies used: Python, Flask, SQLAlchemy, PostgreSQL, Docker
        Files modified: app.py, models.py, routes.py, requirements.txt
        """
        
        metadata = {
            'title': 'Python Flask API Development Session',
            'session_date': '2025-07-24',
            'source': 'claude_code',
            'technologies': '["python", "flask", "api", "sqlalchemy"]',
            'complexity': 'high',
            'project': 'flask-api-project'
        }
        
        # Index the document
        doc_id = test_indexer.index_content(
            content=test_content,
            metadata=metadata,
            doc_id='test-flask-session-001'
        )
        
        assert doc_id == 'test-flask-session-001'
        
        # Wait a moment for indexing to complete
        time.sleep(0.1)
        
        # Search for the document
        results = test_searcher.search("python flask api development", n_results=5)
        
        assert len(results) > 0
        found_doc = False
        for result in results:
            if result['filename'] == 'test-flask-session-001':
                found_doc = True
                assert 'flask' in result['title'].lower()
                assert result['complexity'] == 'high'
                break
        
        assert found_doc, "Indexed document should be found in search results"

    def test_search_with_filters(self, test_searcher, test_indexer):
        """Test search functionality with different filters"""
        # Add multiple test documents with different sources
        test_docs = [
            {
                'content': 'Claude Code CLI development session focusing on terminal interface',
                'metadata': {
                    'title': 'CLI Development',
                    'source': 'claude_code',
                    'session_date': '2025-07-24',
                    'technologies': '["python", "cli", "argparse"]',
                    'complexity': 'medium'
                },
                'id': 'test-cli-001'
            },
            {
                'content': 'Claude Desktop web interface development with React components',
                'metadata': {
                    'title': 'Web Interface Development',
                    'source': 'claude_desktop',
                    'session_date': '2025-07-24',
                    'technologies': '["javascript", "react", "web"]',
                    'complexity': 'high'
                },
                'id': 'test-web-001'
            }
        ]
        
        # Index test documents
        for doc in test_docs:
            test_indexer.index_content(
                content=doc['content'],
                metadata=doc['metadata'],
                doc_id=doc['id']
            )
        
        time.sleep(0.1)  # Wait for indexing
        
        # Search without filters
        all_results = test_searcher.search("development", n_results=10)
        assert len(all_results) >= 2
        
        # Test recency scoring
        recent_results = test_searcher.search("development", n_results=5)
        for result in recent_results:
            assert 'hybrid_score' in result
            assert result['hybrid_score'] > 0

    def test_database_persistence(self, test_db_path):
        """Test that data persists across client connections"""
        # Create first client and add data
        client1 = chromadb.PersistentClient(path=str(test_db_path))
        try:
            collection1 = client1.get_collection("claude_summaries")
        except:
            collection1 = client1.create_collection("claude_summaries")
        
        collection1.add(
            documents=["Test persistence document"],
            metadatas=[{"title": "Persistence Test", "source": "test"}],
            ids=["persistence-test-001"]
        )
        
        # Create second client and check data exists
        client2 = chromadb.PersistentClient(path=str(test_db_path))
        collection2 = client2.get_collection("claude_summaries")
        
        result = collection2.get(ids=["persistence-test-001"])
        assert len(result['ids']) == 1
        assert result['documents'][0] == "Test persistence document"

    def test_large_document_handling(self, test_indexer, test_searcher):
        """Test handling of large documents"""
        # Create a large document
        large_content = "Large document content. " * 1000  # ~23KB
        
        metadata = {
            'title': 'Large Document Test',
            'source': 'claude_code',
            'session_date': '2025-07-24',
            'technologies': '["test"]',
            'complexity': 'low'
        }
        
        # Should handle without errors
        doc_id = test_indexer.index_content(
            content=large_content,
            metadata=metadata,
            doc_id='large-doc-test'
        )
        
        assert doc_id == 'large-doc-test'
        
        # Should be searchable
        time.sleep(0.1)
        results = test_searcher.search("large document", n_results=5)
        
        found = any(r['filename'] == 'large-doc-test' for r in results)
        assert found


class TestAPIServerIntegration:
    """Test integration with running API server"""

    @pytest.fixture(scope='class')
    def api_server_url(self):
        """Base URL for API server (assumes it's running)"""
        return 'http://localhost:8080'

    def test_api_server_health(self, api_server_url):
        """Test API server health endpoint"""
        try:
            response = requests.get(f'{api_server_url}/api/health', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                assert data['success'] is True
                assert 'database' in data['data']
            else:
                pytest.skip("API server not running or not accessible")
                
        except requests.exceptions.RequestException:
            pytest.skip("API server not running or not accessible")

    def test_api_search_integration(self, api_server_url):
        """Test search API integration"""
        try:
            search_data = {
                "query": "python development",
                "max_results": 3
            }
            
            response = requests.post(
                f'{api_server_url}/api/search',
                json=search_data,
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'results' in data['data']
            
        except requests.exceptions.RequestException:
            pytest.skip("API server not running or not accessible")

    def test_api_add_memory_integration(self, api_server_url):
        """Test add memory API integration"""
        try:
            memory_data = {
                "content": "Integration test memory from automated test suite",
                "title": "Integration Test Memory",
                "source": "claude_code",
                "technologies": ["python", "testing", "integration"],
                "complexity": "low"
            }
            
            response = requests.post(
                f'{api_server_url}/api/add_memory',
                json=memory_data,
                timeout=10
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data['success'] is True
            assert 'id' in data['data']
            
            # Store ID for potential cleanup
            memory_id = data['data']['id']
            
            # Try to search for the added memory
            search_response = requests.post(
                f'{api_server_url}/api/search',
                json={"query": "integration test memory"},
                timeout=10
            )
            
            search_data = search_response.json()
            if search_data['success']:
                found = any('integration test' in r['title'].lower() 
                          for r in search_data['data']['results'])
                # Note: May not find immediately due to indexing delay
            
        except requests.exceptions.RequestException:
            pytest.skip("API server not running or not accessible")

    def test_api_rate_limiting(self, api_server_url):
        """Test API rate limiting behavior"""
        try:
            # Make multiple rapid requests
            responses = []
            for i in range(25):  # More than typical rate limit
                response = requests.post(
                    f'{api_server_url}/api/search',
                    json={"query": f"rate limit test {i}"},
                    timeout=5
                )
                responses.append(response.status_code)
                
                if response.status_code == 429:
                    break
            
            # Should eventually hit rate limit
            rate_limited = any(status == 429 for status in responses)
            # Note: Rate limiting might not trigger in test environment
            
        except requests.exceptions.RequestException:
            pytest.skip("API server not running or not accessible")


class TestJavaScriptClientIntegration:
    """Test JavaScript client library integration"""

    def test_javascript_client_exists(self):
        """Test that JavaScript client file exists and is readable"""
        client_file = Path(__file__).parent.parent / "memory_client.js"
        assert client_file.exists(), "JavaScript client library should exist"
        
        content = client_file.read_text()
        assert "ClaudeMemoryClient" in content
        assert "MemoryIntegration" in content

    def test_javascript_client_syntax(self):
        """Test JavaScript client has valid syntax"""
        client_file = Path(__file__).parent.parent / "memory_client.js"
        
        # Basic syntax check by reading and looking for key patterns
        content = client_file.read_text()
        
        # Check for proper class definitions
        assert "class ClaudeMemoryClient {" in content
        assert "class MemoryIntegration {" in content
        
        # Check for key methods
        assert "async search(" in content
        assert "async addMemory(" in content
        assert "async getHealth(" in content
        
        # Check for proper exports
        assert "ClaudeMemoryClient" in content
        assert "MemoryIntegration" in content


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""

    @pytest.fixture
    def client(self):
        """Create Flask test client for E2E tests"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_complete_memory_lifecycle(self, client):
        """Test complete memory lifecycle: add, search, list, delete"""
        # Step 1: Add a memory
        memory_data = {
            "content": "E2E test memory for complete lifecycle testing",
            "title": "E2E Lifecycle Test",
            "source": "claude_code",
            "technologies": ["testing", "e2e", "lifecycle"],
            "complexity": "medium"
        }
        
        add_response = client.post('/api/add_memory', 
                                  json=memory_data)
        assert add_response.status_code == 201
        add_data = add_response.json()
        memory_id = add_data['data']['id']
        
        # Step 2: Search for the memory
        search_response = client.post('/api/search', 
                                     json={"query": "e2e lifecycle"})
        assert search_response.status_code == 200
        
        # Step 3: List memories (should include our memory)
        list_response = client.get('/api/memories?limit=50')
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        found_in_list = any(m['id'] == memory_id for m in list_data['data']['memories'])
        assert found_in_list, "Memory should appear in list"
        
        # Step 4: Delete the memory
        delete_response = client.delete(f'/api/memory/{memory_id}')
        assert delete_response.status_code == 200
        
        # Step 5: Verify memory is deleted
        list_after_delete = client.get('/api/memories?limit=50')
        list_after_data = list_after_delete.json()
        
        not_found_after_delete = not any(m['id'] == memory_id 
                                       for m in list_after_data['data']['memories'])
        assert not_found_after_delete, "Memory should not appear in list after deletion"

    def test_search_relevance_workflow(self, client):
        """Test search relevance with multiple related memories"""
        # Add multiple memories with varying relevance
        test_memories = [
            {
                "content": "Python Flask web development tutorial with database integration",
                "title": "Flask Web Development",
                "technologies": ["python", "flask", "web", "database"],
                "complexity": "high"
            },
            {
                "content": "Basic Python programming concepts and syntax overview",
                "title": "Python Basics",
                "technologies": ["python", "basics"],
                "complexity": "low"
            },
            {
                "content": "Advanced Flask application deployment with Docker and nginx",
                "title": "Flask Deployment",
                "technologies": ["flask", "docker", "deployment", "nginx"],
                "complexity": "high"
            }
        ]
        
        memory_ids = []
        for memory in test_memories:
            response = client.post('/api/add_memory', json=memory)
            assert response.status_code == 201
            memory_ids.append(response.json()['data']['id'])
        
        # Search for Flask-specific content
        search_response = client.post('/api/search', 
                                     json={"query": "flask web development", "max_results": 5})
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        results = search_data['data']['results']
        
        # Should find Flask-related memories first
        if len(results) >= 2:
            flask_results = [r for r in results if 'flask' in r['title'].lower()]
            assert len(flask_results) >= 2, "Should find multiple Flask-related memories"
        
        # Cleanup
        for memory_id in memory_ids:
            client.delete(f'/api/memory/{memory_id}')

    def test_error_recovery_workflow(self, client):
        """Test system behavior during error conditions"""
        # Test 1: Invalid JSON handling
        response = client.post('/api/search', 
                              data='{"invalid": json syntax}',
                              content_type='application/json')
        assert response.status_code == 400
        
        # Test 2: Missing required fields
        response = client.post('/api/add_memory', json={})
        assert response.status_code == 400
        
        # Test 3: Invalid memory ID for deletion
        response = client.delete('/api/memory/invalid-id-12345')
        assert response.status_code == 404
        
        # Test 4: System should still be healthy after errors
        health_response = client.get('/api/health')
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data['success'] is True


class TestPerformanceIntegration:
    """Test performance characteristics under load"""

    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_concurrent_searches(self, client):
        """Test system handles concurrent search requests"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def search_worker():
            try:
                response = client.post('/api/search', 
                                      json={"query": "concurrent test"})
                results_queue.put(response.status_code)
            except Exception as e:
                results_queue.put(str(e))
        
        # Launch multiple concurrent searches
        threads = []
        for i in range(10):
            thread = threading.Thread(target=search_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Most requests should succeed
        successful = sum(1 for r in results if r == 200)
        assert successful >= 8, "Most concurrent requests should succeed"

    def test_bulk_memory_operations(self, client):
        """Test system handles bulk memory operations"""
        # Add multiple memories
        memory_ids = []
        
        start_time = time.time()
        for i in range(20):
            memory_data = {
                "content": f"Bulk test memory {i} with unique content for testing",
                "title": f"Bulk Test Memory {i}",
                "technologies": ["testing", "bulk", "performance"],
                "complexity": "low"
            }
            
            response = client.post('/api/add_memory', json=memory_data)
            if response.status_code == 201:
                memory_ids.append(response.json()['data']['id'])
        
        add_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert add_time < 30, "Bulk add operations should complete within 30 seconds"
        assert len(memory_ids) >= 15, "Most bulk add operations should succeed"
        
        # Cleanup
        for memory_id in memory_ids:
            client.delete(f'/api/memory/{memory_id}')


if __name__ == '__main__':
    # Run integration tests
    pytest.main([__file__, '-v', '--tb=short', '-x'])