"""
Memory Curation API Endpoints
Adds memory management and curation features to the memory server
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# Import the curator
from memory_curator import MemoryCurator

# Create blueprint
curation_api = Blueprint('curation_api', __name__)

# Setup logger
logger = logging.getLogger('memory_api.curation')

# Global curator instance (will be initialized by main server)
curator = None

@curation_api.route('/api/curator/health', methods=['GET'])
def get_memory_health():
    """Get comprehensive memory health analysis"""
    try:
        if not curator:
            return jsonify({
                'success': False,
                'error': 'Curator not initialized'
            }), 500
        
        start_time = datetime.now()
        health_report = curator.analyze_memory_health()
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return jsonify({
            'success': True,
            'data': health_report,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'execution_time_seconds': execution_time
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curation_api.route('/api/curator/deduplicate', methods=['POST'])
def deduplicate_memories():
    """Remove duplicate memories"""
    try:
        data = request.json or {}
        dry_run = data.get('dry_run', True)  # Default to dry run for safety
        
        result = curator.deduplicate_memories(dry_run=dry_run)
        
        return jsonify({
            'success': True,
            'data': result,
            'metadata': {
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Deduplication failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curation_api.route('/api/curator/consolidate', methods=['POST'])
def consolidate_memories():
    """Consolidate multiple memories into one"""
    try:
        data = request.json
        if not data or 'memory_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'memory_ids required'
            }), 400
        
        memory_ids = data['memory_ids']
        new_title = data.get('title')
        
        result = curator.consolidate_memories(memory_ids, new_title)
        
        return jsonify({
            'success': result['success'],
            'data': result,
            'metadata': {
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Consolidation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curation_api.route('/api/curator/archive', methods=['POST'])
def archive_old_memories():
    """Archive memories older than threshold"""
    try:
        data = request.json or {}
        days_threshold = data.get('days', 90)
        dry_run = data.get('dry_run', True)
        
        result = curator.archive_old_memories(days_threshold, dry_run)
        
        return jsonify({
            'success': True,
            'data': result,
            'metadata': {
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Archival failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curation_api.route('/api/curator/enhance/<memory_id>', methods=['POST'])
def enhance_memory(memory_id):
    """Enhance a specific memory's quality"""
    try:
        result = curator.enhance_memory_quality(memory_id)
        
        return jsonify({
            'success': result['success'],
            'data': result,
            'metadata': {
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curation_api.route('/api/curator/analyze', methods=['GET'])
def analyze_patterns():
    """Analyze patterns and insights from memories"""
    try:
        # Get all memories for analysis
        results = curator.searcher.collection.get(include=["metadatas", "documents"])
        
        if not results['ids']:
            return jsonify({
                'success': True,
                'data': {'message': 'No memories to analyze'},
            })
        
        memories = []
        for i, doc_id in enumerate(results['ids']):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            content = results['documents'][i] if results['documents'] else ''
            memories.append({
                'id': doc_id,
                'metadata': metadata,
                'content': content
            })
        
        # Analyze patterns
        insights = {
            'total_memories': len(memories),
            'error_patterns': curator._analyze_error_patterns(memories),
            'technology_trends': curator._get_technology_distribution(memories),
            'quality_metrics': curator._assess_quality_distribution(memories),
            'temporal_patterns': curator._get_age_distribution(memories),
            'consolidation_opportunities': len(curator._find_consolidation_opportunities(memories))
        }
        
        # Generate insights
        if insights['error_patterns']['common_patterns']:
            insights['key_insights'] = [
                f"Found {len(insights['error_patterns']['common_patterns'])} recurring error patterns",
                f"Most common technology: {list(insights['technology_trends'].keys())[0] if insights['technology_trends'] else 'None'}",
                f"Memory quality: {insights['quality_metrics']['high']} high, {insights['quality_metrics']['medium']} medium, {insights['quality_metrics']['low']} low"
            ]
        else:
            insights['key_insights'] = []
        
        return jsonify({
            'success': True,
            'data': insights,
            'metadata': {
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curation_api.route('/api/curator/auto-curate', methods=['POST'])
def auto_curate():
    """Automatically curate memories based on best practices"""
    try:
        data = request.json or {}
        dry_run = data.get('dry_run', True)
        
        actions_taken = []
        
        # 1. Remove duplicates
        dedup_result = curator.deduplicate_memories(dry_run=dry_run)
        if dedup_result['duplicates_found'] > 0:
            actions_taken.append(f"{'Would remove' if dry_run else 'Removed'} {dedup_result['duplicates_found']} duplicates")
        
        # 2. Archive old memories (>180 days)
        archive_result = curator.archive_old_memories(180, dry_run=dry_run)
        if archive_result['found'] > 0:
            actions_taken.append(f"{'Would archive' if dry_run else 'Archived'} {archive_result['found']} old memories")
        
        # 3. Enhance low-quality memories
        results = curator.searcher.collection.get(include=["metadatas"])
        enhanced_count = 0
        
        if results['ids']:
            for i, doc_id in enumerate(results['ids'][:20]):  # Limit to 20 for performance
                memory = {
                    'id': doc_id,
                    'metadata': results['metadatas'][i] if results['metadatas'] else {},
                    'content': ''
                }
                
                quality_score = curator._calculate_memory_quality_score(memory)
                if quality_score < 0.5 and not dry_run:
                    try:
                        curator.enhance_memory_quality(doc_id)
                        enhanced_count += 1
                    except:
                        pass
        
        if enhanced_count > 0 or (dry_run and enhanced_count == 0):
            actions_taken.append(f"{'Would enhance' if dry_run else 'Enhanced'} {enhanced_count} low-quality memories")
        
        return jsonify({
            'success': True,
            'data': {
                'dry_run': dry_run,
                'actions_taken': actions_taken,
                'summary': f"{len(actions_taken)} curation actions {'identified' if dry_run else 'completed'}"
            },
            'metadata': {
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Auto-curation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def initialize_curation_api(app, searcher, indexer):
    """Initialize the curation API with dependencies"""
    global curator
    
    # Initialize curator
    curator = MemoryCurator(searcher, indexer)
    
    # Register blueprint
    app.register_blueprint(curation_api)
    
    logger.info("Curation API initialized")
    
    return curation_api