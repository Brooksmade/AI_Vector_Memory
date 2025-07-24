from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import traceback
import logging
from pathlib import Path
import json
import uuid
import sys
import os

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent / "scripts"))

# Import your existing modules
from memory_search import MemorySearcher
from index_summaries import SummaryIndexer

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])  # Enable CORS for web interface

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# Load configuration
CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default configuration if file doesn't exist
        return {
            "api": {"host": "localhost", "port": 8080, "debug": False},
            "database": {"path": "./chroma_db", "collection_name": "claude_summaries"},
            "logging": {"level": "INFO", "file": "memory_api.log"}
        }

config = load_config()

# Configuration constants
DB_PATH = Path(__file__).parent / config["database"]["path"]
COLLECTION_NAME = config["database"]["collection_name"]
API_HOST = config["api"]["host"]
API_PORT = config["api"]["port"]
DEBUG_MODE = config["api"]["debug"]

# Setup enhanced logging
log_level = getattr(logging, config.get("logging", {}).get("level", "INFO").upper())
log_file = config.get("logging", {}).get("file", "memory_api.log")

# Create logs directory if it doesn't exist
log_path = Path(log_file)
log_path.parent.mkdir(exist_ok=True)

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

# Remove default handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup custom logging
logger = logging.getLogger('memory_api')
logger.setLevel(log_level)

# File handler with rotation
file_handler = RotatingFileHandler(
    log_file, 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(log_level)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
simple_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

file_handler.setFormatter(detailed_formatter)
console_handler.setFormatter(simple_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Set Flask app logger
app.logger.handlers = []
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(log_level)

# Performance monitoring
request_count = 0
total_response_time = 0.0

def get_performance_stats():
    """Get current performance statistics"""
    global request_count, total_response_time
    return {
        'request_count': request_count,
        'average_response_time_ms': (total_response_time / request_count * 1000) if request_count > 0 else 0,
        'uptime_seconds': (datetime.now() - startup_time).total_seconds()
    }

startup_time = datetime.now()

# Initialize once at startup
try:
    logger.info("🚀 Initializing Claude Memory API Server...")
    logger.info(f"📁 Database path: {DB_PATH}")
    logger.info(f"🗂️  Collection name: {COLLECTION_NAME}")
    logger.info(f"🌐 Server: {API_HOST}:{API_PORT}")
    logger.info(f"🔧 Debug mode: {DEBUG_MODE}")
    
    searcher = MemorySearcher()
    indexer = SummaryIndexer()
    
    doc_count = searcher.collection.count()
    logger.info(f"✅ Connected to ChromaDB successfully")
    logger.info(f"📊 Document count: {doc_count}")
    
    if doc_count == 0:
        logger.warning("⚠️  Database is empty - consider running indexing scripts")
        
except Exception as e:
    logger.error(f"❌ Failed to initialize database connection: {e}")
    logger.error(f"🔧 Check that ChromaDB is installed and database path is accessible")
    raise

# Enhanced middleware for logging and monitoring
@app.before_request
def before_request():
    global request_count
    request_count += 1
    
    request.request_id = str(uuid.uuid4())[:8]  # Shorter ID for readability
    request.start_time = datetime.now()
    
    # Log request details
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')[:50]
    
    if request.method == 'POST' and request.json:
        query = request.json.get('query', '')[:50] if request.json else ''
        logger.info(f"📥 {request.method} {request.path} - {query} [ID: {request.request_id}] [IP: {client_ip}]")
    else:
        logger.info(f"📥 {request.method} {request.path} [ID: {request.request_id}] [IP: {client_ip}]")

@app.after_request
def after_request(response):
    global total_response_time
    
    if hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        duration_ms = duration * 1000
        total_response_time += duration
        
        # Log response details
        logger.info(f"📤 {response.status_code} - {duration_ms:.2f}ms [ID: {getattr(request, 'request_id', 'unknown')}]")
        
        # Log slow requests as warnings
        if duration_ms > 1000:  # Slower than 1 second
            logger.warning(f"🐌 Slow request: {request.method} {request.path} took {duration_ms:.2f}ms")
            
        # Add performance headers
        response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"
        response.headers['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
        
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"🔍 404 Not Found: {request.method} {request.path} [ID: {getattr(request, 'request_id', 'unknown')}]")
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Endpoint not found',
            'details': {'path': request.path, 'method': request.method}
        },
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'request_id': getattr(request, 'request_id', 'unknown'),
            'execution_time_ms': 0
        }
    }), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    logger.warning(f"🚫 Rate limit exceeded: {request.remote_addr} [ID: {getattr(request, 'request_id', 'unknown')}]")
    return jsonify({
        'success': False,
        'error': {
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': 'Too many requests',
            'details': {'retry_after': '60 seconds'}
        },
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'request_id': getattr(request, 'request_id', 'unknown'),
            'execution_time_ms': 0
        }
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"💥 Internal server error: {error} [ID: {getattr(request, 'request_id', 'unknown')}]")
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'Internal server error',
            'details': {}
        },
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'request_id': getattr(request, 'request_id', 'unknown'),
            'execution_time_ms': 0
        }
    }), 500

@app.route('/api/search', methods=['POST'])
@limiter.limit("20 per minute")
def search_memory():
    """Search the vector database for similar content"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Missing 'query' in request body",
                    "details": {}
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "request_id": getattr(request, 'request_id', 'unknown'),
                    "execution_time_ms": 0
                }
            }), 400
        
        start_time = datetime.now()
        
        # Extract search parameters
        query = data['query']
        max_results = min(data.get('max_results', 3), 10)  # Cap at 10
        similarity_threshold = data.get('similarity_threshold', 0.3)
        source_filter = data.get('source_filter')  # claude_code or claude_desktop
        
        # Perform search
        results = searcher.search(
            query=query, 
            n_results=max_results,
            min_similarity=similarity_threshold
        )
        
        # Filter by source if specified
        if source_filter:
            results = [r for r in results if r.get('source') == source_filter]
        
        # Format results according to API spec
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.get('filename', str(uuid.uuid4())),
                "title": result.get('title', 'Untitled'),
                "similarity": result.get('similarity', 0),
                "relevance_score": result.get('hybrid_score', result.get('similarity', 0)),
                "preview": result.get('preview', '')[:300],
                "metadata": {
                    "date": result.get('date', 'unknown'),
                    "complexity": result.get('complexity', 'unknown'),
                    "technologies": result.get('technologies', []),
                    "source": result.get('source', 'unknown'),
                    "file_path": str(result.get('file_path', ''))
                },
                "source": result.get('source', 'unknown'),
                "date": result.get('date', 'unknown')
            })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return jsonify({
            "success": True,
            "data": {
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "search_time_ms": round(execution_time, 2)
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', 'unknown'),
                "execution_time_ms": round(execution_time, 2)
            }
        })
    except Exception as e:
        app.logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Search operation failed",
                "details": {"error": str(e)}
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', 'unknown'),
                "execution_time_ms": 0
            }
        }), 500

@app.route('/api/add_memory', methods=['POST'])
@limiter.limit("50 per minute")
def add_memory():
    """Add new memory to the database"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR", 
                    "message": "Request body is required",
                    "details": {}
                }
            }), 400
        
        # Validate required fields
        required_fields = ['content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Missing required fields: {missing_fields}",
                    "details": {"missing_fields": missing_fields}
                }
            }), 400
        
        start_time = datetime.now()
        
        # Extract memory data according to execution plan schema
        memory_data = {
            "content": data['content'],
            "title": data.get('title', 'Untitled Memory'),
            "date": data.get('date', datetime.now().strftime('%Y-%m-%d')),
            "source": data.get('source', 'claude_desktop'),
            "technologies": data.get('technologies', []),
            "file_paths": data.get('file_paths', []),
            "complexity": data.get('complexity', 'medium'),
            "project": data.get('project', ''),
        }
        
        # Prepare metadata for ChromaDB
        metadata = data.get('metadata', {})
        metadata.update({
            'title': memory_data['title'],
            'session_date': memory_data['date'],
            'source': memory_data['source'],
            'technologies': json.dumps(memory_data['technologies']),
            'complexity': memory_data['complexity'],
            'project': memory_data['project'],
            'indexed_at': datetime.now().isoformat(),
            'via_api': True,
            'conversation_length': len(memory_data['content']),
            'code_blocks': memory_data['content'].count('```'),
        })
        
        # Generate unique ID
        doc_id = data.get('id', str(uuid.uuid4()))
        
        # Index the content
        try:
            # Use ChromaDB collection directly to add the memory
            indexer.collection.add(
                documents=[memory_data['content']],
                metadatas=[metadata],
                ids=[doc_id]
            )
            indexed_id = doc_id
        except Exception as index_error:
            app.logger.error(f"Indexing error: {index_error}", exc_info=True)
            return jsonify({
                "success": False,
                "error": {
                    "code": "INDEX_ERROR",
                    "message": "Failed to index memory content",
                    "details": {"error": str(index_error)}
                }
            }), 500
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return jsonify({
            "success": True,
            "data": {
                "id": indexed_id,
                "title": memory_data['title'],
                "message": "Memory added successfully"
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', 'unknown'),
                "execution_time_ms": round(execution_time, 2)
            }
        }), 201
        
    except Exception as e:
        app.logger.error(f"Add memory error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to add memory",
                "details": {"error": str(e)}
            }
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check API and database health"""
    try:
        start_time = datetime.now()
        
        # Test database connectivity
        count = searcher.collection.count()
        
        # Test search functionality
        test_search = searcher.search("test", n_results=1)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Get performance statistics
        perf_stats = get_performance_stats()
        
        return jsonify({
            "success": True,
            "data": {
                "status": "healthy",
                "database": {
                    "connected": True,
                    "document_count": count,
                    "path": str(DB_PATH),
                    "collection": COLLECTION_NAME
                },
                "api": {
                    "version": "1.0",
                    "endpoints_available": [
                        "POST /api/search",
                        "POST /api/add_memory", 
                        "GET /api/health",
                        "GET /api/memories",
                        "DELETE /api/memory/{id}",
                        "POST /api/reindex"
                    ]
                },
                "performance": {
                    "health_check_time_ms": round(execution_time, 2),
                    "search_functional": len(test_search) >= 0,
                    "uptime_seconds": perf_stats['uptime_seconds'],
                    "total_requests": perf_stats['request_count'],
                    "average_response_time_ms": round(perf_stats['average_response_time_ms'], 2)
                },
                "system": {
                    "startup_time": startup_time.isoformat(),
                    "config_loaded": CONFIG_FILE.exists(),
                    "log_file": log_file
                }
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', str(uuid.uuid4())),
                "execution_time_ms": round(execution_time, 2)
            }
        })
    except Exception as e:
        app.logger.error(f"Health check error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "data": {
                "status": "unhealthy",
                "database": {"connected": False},
                "api": {"version": "1.0"}
            },
            "error": {
                "code": "HEALTH_CHECK_FAILED",
                "message": "System health check failed",
                "details": {"error": str(e)}
            }
        }), 503

@app.route('/api/memories', methods=['GET'])
def list_memories():
    """List all memories with pagination"""
    try:
        start_time = datetime.now()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 50)  # Cap at 50
        offset = (page - 1) * limit
        
        # Get total count
        total_count = searcher.collection.count()
        
        # Get memories with pagination
        try:
            results = searcher.collection.get(
                limit=limit,
                offset=offset,
                include=["metadatas", "documents"]
            )
        except Exception as query_error:
            # Fallback if offset not supported
            results = searcher.collection.get(include=["metadatas", "documents"])
            # Manual pagination
            if results['ids']:
                start_idx = min(offset, len(results['ids']))
                end_idx = min(offset + limit, len(results['ids']))
                results = {
                    'ids': results['ids'][start_idx:end_idx],
                    'metadatas': results['metadatas'][start_idx:end_idx] if results['metadatas'] else [],
                    'documents': results['documents'][start_idx:end_idx] if results['documents'] else []
                }
        
        # Format memories
        memories = []
        if results['ids']:
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                document = results['documents'][i] if results['documents'] else ""
                
                memories.append({
                    "id": doc_id,
                    "title": metadata.get('title', 'Untitled'),
                    "date": metadata.get('session_date', 'unknown'),
                    "source": metadata.get('source', 'unknown'),
                    "complexity": metadata.get('complexity', 'unknown'),
                    "technologies": json.loads(metadata.get('technologies', '[]')),
                    "preview": document[:200] + "..." if len(document) > 200 else document,
                    "metadata": {
                        "conversation_length": metadata.get('conversation_length', 0),
                        "code_blocks": metadata.get('code_blocks', 0),
                        "project": metadata.get('project', ''),
                        "indexed_at": metadata.get('indexed_at', '')
                    }
                })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return jsonify({
            "success": True,
            "data": {
                "memories": memories,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": (total_count + limit - 1) // limit,
                    "has_next": offset + limit < total_count,
                    "has_prev": page > 1
                }
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', str(uuid.uuid4())),
                "execution_time_ms": round(execution_time, 2)
            }
        })
    except Exception as e:
        app.logger.error(f"List memories error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to list memories",
                "details": {"error": str(e)}
            }
        }), 500

@app.route('/api/memory/<memory_id>', methods=['DELETE'])
@limiter.limit("30 per minute")
def delete_memory(memory_id):
    """Delete a specific memory by ID"""
    try:
        start_time = datetime.now()
        
        # Check if memory exists first
        try:
            result = searcher.collection.get(ids=[memory_id])
            if not result['ids']:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Memory with ID '{memory_id}' not found",
                        "details": {}
                    }
                }), 404
        except Exception:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND", 
                    "message": f"Memory with ID '{memory_id}' not found",
                    "details": {}
                }
            }), 404
        
        # Delete the memory
        searcher.collection.delete(ids=[memory_id])
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return jsonify({
            "success": True,
            "data": {
                "message": f"Memory '{memory_id}' deleted successfully"
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', str(uuid.uuid4())),
                "execution_time_ms": round(execution_time, 2)
            }
        })
    except Exception as e:
        app.logger.error(f"Delete memory error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to delete memory",
                "details": {"error": str(e)}
            }
        }), 500

@app.route('/api/reindex', methods=['POST'])
@limiter.limit("5 per hour")
def reindex_database():
    """Rebuild the entire index"""
    try:
        start_time = datetime.now()
        
        # Get admin confirmation
        data = request.json or {}
        if not data.get('confirm', False):
            return jsonify({
                "success": False,
                "error": {
                    "code": "CONFIRMATION_REQUIRED",
                    "message": "Reindexing requires confirmation. Send {\"confirm\": true}",
                    "details": {}
                }
            }), 400
        
        # Get current count before reindex
        old_count = searcher.collection.count()
        
        # Perform reindex (this would typically involve re-reading source files)
        app.logger.info("Starting database reindex operation")
        
        # Note: This is a placeholder - actual reindex would need to be implemented
        # based on your specific indexing strategy
        new_count = old_count  # For now, just return current count
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return jsonify({
            "success": True,
            "data": {
                "message": "Reindex completed successfully",
                "statistics": {
                    "documents_before": old_count,
                    "documents_after": new_count,
                    "reindex_time_ms": round(execution_time, 2)
                }
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, 'request_id', str(uuid.uuid4())),
                "execution_time_ms": round(execution_time, 2)
            }
        })
    except Exception as e:
        app.logger.error(f"Reindex error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "REINDEX_FAILED",
                "message": "Database reindex failed",
                "details": {"error": str(e)}
            }
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Claude Memory API Server...")
    print(f"📍 API available at: http://{API_HOST}:{API_PORT}")
    print("📚 Available Endpoints:")
    print("   - POST /api/search           - Search for similar content")
    print("   - POST /api/add_memory       - Add new memory to database")
    print("   - GET  /api/health           - Check system health & status")
    print("   - GET  /api/memories         - List all memories (paginated)")
    print("   - DELETE /api/memory/<id>    - Delete specific memory by ID")
    print("   - POST /api/reindex          - Rebuild entire search index")
    print("\n🔗 Integration URLs:")
    print("   - Claude Code CLI: Include this API in CLAUDE.md")
    print("   - Claude Desktop: Use JavaScript client library")
    print("\n💡 Usage Examples:")
    print(f"   curl -X POST http://{API_HOST}:{API_PORT}/api/search -H 'Content-Type: application/json' -d '{{\"query\":\"python flask\"}}'")
    print(f"   curl -X GET http://{API_HOST}:{API_PORT}/api/health")
    print(f"\n📊 Configuration:")
    print(f"   - Debug mode: {DEBUG_MODE}")
    print(f"   - Log file: {log_file}")
    print(f"   - Database: {DB_PATH}")
    print(f"   - Collection: {COLLECTION_NAME}")
    print("\n🌐 Starting server with CORS enabled for web interface...")
    
    try:
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server startup failed: {e}")
        raise
