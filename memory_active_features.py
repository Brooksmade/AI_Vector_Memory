"""
Active Memory Features - Makes the memory server proactive
Adds file watching, error detection, and automatic memory engagement
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue
import re
import json
import logging
import time
import os

# Create blueprint for active features
active_memory = Blueprint('active_memory', __name__)

# Setup logger
logger = logging.getLogger('memory_api.active')

class MemoryContext:
    """Tracks current context for automatic memory engagement"""
    
    def __init__(self):
        self.current_files = set()
        self.recent_errors = []
        self.recent_queries = []
        self.project_root = None
        self.technologies = set()
        self.error_patterns = {}
        self.file_history = []
        self.decision_queue = queue.Queue()
        
    def update_file(self, file_path):
        """Track file being worked on"""
        self.current_files.add(file_path)
        self.file_history.append({
            'path': file_path,
            'timestamp': datetime.now().isoformat()
        })
        # Keep only last 50 files
        if len(self.file_history) > 50:
            self.file_history.pop(0)
            
        # Detect technology from file extension
        ext = Path(file_path).suffix.lower()
        tech_map = {
            '.ts': 'typescript', '.tsx': 'typescript',
            '.js': 'javascript', '.jsx': 'javascript',
            '.py': 'python', '.sql': 'sql',
            '.css': 'css', '.html': 'html'
        }
        if ext in tech_map:
            self.technologies.add(tech_map[ext])
    
    def add_error(self, error_text, context=None):
        """Track errors for pattern detection"""
        error_key = self._normalize_error(error_text)
        
        if error_key not in self.error_patterns:
            self.error_patterns[error_key] = {
                'count': 0,
                'first_seen': datetime.now().isoformat(),
                'last_seen': None,
                'contexts': []
            }
        
        self.error_patterns[error_key]['count'] += 1
        self.error_patterns[error_key]['last_seen'] = datetime.now().isoformat()
        if context:
            self.error_patterns[error_key]['contexts'].append(context)
        
        self.recent_errors.append({
            'error': error_text,
            'timestamp': datetime.now().isoformat(),
            'context': context
        })
        
        # Keep only last 20 errors
        if len(self.recent_errors) > 20:
            self.recent_errors.pop(0)
    
    def _normalize_error(self, error):
        """Normalize error for pattern matching"""
        # Remove specific paths, numbers, quotes
        normalized = error.lower()
        normalized = re.sub(r'["\'].*?["\']', 'STRING', normalized)
        normalized = re.sub(r'\b\d+\b', 'NUM', normalized)
        normalized = re.sub(r'[/\\][\w\-\./\\]+', 'PATH', normalized)
        return normalized[:100]  # Truncate for consistency
    
    def get_context_summary(self):
        """Get current context for memory queries"""
        return {
            'current_files': list(self.current_files)[-5:],
            'technologies': list(self.technologies),
            'error_count': len(self.recent_errors),
            'repeated_errors': [k for k, v in self.error_patterns.items() if v['count'] > 1],
            'recent_files': [f['path'] for f in self.file_history[-10:]]
        }

# Global context instance
memory_context = MemoryContext()

class ClaudeFileWatcher(FileSystemEventHandler):
    """Watches for file changes and triggers memory checks"""
    
    def __init__(self, searcher, project_root):
        self.searcher = searcher
        self.project_root = Path(project_root)
        self.last_check = {}
        self.check_interval = 5  # Minimum seconds between checks for same file
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Skip non-code files
        if file_path.suffix not in ['.py', '.js', '.ts', '.tsx', '.jsx', '.sql', '.css', '.html']:
            return
        
        # Rate limit checks
        now = time.time()
        if file_path in self.last_check:
            if now - self.last_check[file_path] < self.check_interval:
                return
        
        self.last_check[file_path] = now
        
        # Update context
        memory_context.update_file(str(file_path))
        
        # Trigger memory check
        self._check_memory_for_file(file_path)
    
    def _check_memory_for_file(self, file_path):
        """Check memory for relevant information about this file"""
        try:
            relative_path = file_path.relative_to(self.project_root)
            query = f"{relative_path.name} {relative_path.parent} error bug fix"
            
            results = self.searcher.search(
                query=query,
                n_results=3,
                min_similarity=0.5
            )
            
            if results:
                # Store relevant memories for Claude to access
                warnings = []
                for result in results:
                    if result.get('similarity', 0) > 0.6:
                        if 'error' in result.get('preview', '').lower():
                            warnings.append({
                                'file': str(relative_path),
                                'memory': result.get('title', 'Unknown'),
                                'date': result.get('date', 'Unknown'),
                                'preview': result.get('preview', '')[:200]
                            })
                
                if warnings:
                    memory_context.decision_queue.put({
                        'type': 'file_warning',
                        'file': str(relative_path),
                        'warnings': warnings,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"Found {len(warnings)} warnings for {relative_path}")
                    
        except Exception as e:
            logger.error(f"Error checking memory for {file_path}: {e}")

class LogMonitor:
    """Monitors logs for errors and patterns"""
    
    def __init__(self, log_files):
        self.log_files = log_files
        self.last_positions = {}
        self.error_patterns = [
            r'ERROR|CRITICAL|FATAL',
            r'Exception|Error:|Failed|Failure',
            r'Traceback \(most recent call last\)',
            r'TypeError|ValueError|KeyError|AttributeError',
        ]
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start monitoring logs in background thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Started log monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped log monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            for log_file in self.log_files:
                if Path(log_file).exists():
                    self._check_log_file(log_file)
            time.sleep(2)  # Check every 2 seconds
    
    def _check_log_file(self, log_file):
        """Check a log file for new errors"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Get last position
                last_pos = self.last_positions.get(log_file, 0)
                f.seek(last_pos)
                
                # Read new lines
                new_lines = f.readlines()
                if new_lines:
                    self.last_positions[log_file] = f.tell()
                    
                    # Check for errors
                    for line in new_lines:
                        for pattern in self.error_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                memory_context.add_error(line.strip(), {
                                    'log_file': log_file,
                                    'pattern': pattern
                                })
                                break
                                
        except Exception as e:
            logger.error(f"Error monitoring log {log_file}: {e}")

# Active memory endpoints
@active_memory.route('/api/active/status', methods=['GET'])
def get_active_status():
    """Get current active memory status"""
    context_summary = memory_context.get_context_summary()
    
    return jsonify({
        'success': True,
        'data': {
            'context': context_summary,
            'monitoring': {
                'file_watcher': hasattr(active_memory, 'file_observer') and active_memory.file_observer.is_alive(),
                'log_monitor': hasattr(active_memory, 'log_monitor') and active_memory.log_monitor.monitoring
            },
            'pending_decisions': memory_context.decision_queue.qsize()
        }
    })

@active_memory.route('/api/active/decisions', methods=['GET'])
def get_pending_decisions():
    """Get pending decisions/warnings for Claude"""
    decisions = []
    
    # Get up to 10 pending decisions
    for _ in range(min(10, memory_context.decision_queue.qsize())):
        try:
            decision = memory_context.decision_queue.get_nowait()
            decisions.append(decision)
        except queue.Empty:
            break
    
    return jsonify({
        'success': True,
        'data': {
            'decisions': decisions,
            'count': len(decisions)
        }
    })

@active_memory.route('/api/active/context', methods=['POST'])
def update_context():
    """Update context from Claude's current state"""
    data = request.json
    
    if 'current_task' in data:
        memory_context.current_task = data['current_task']
    
    if 'technologies' in data:
        memory_context.technologies.update(data['technologies'])
    
    if 'current_file' in data:
        memory_context.update_file(data['current_file'])
    
    if 'error' in data:
        memory_context.add_error(data['error'], data.get('error_context'))
    
    return jsonify({
        'success': True,
        'data': {
            'context_updated': True,
            'summary': memory_context.get_context_summary()
        }
    })

@active_memory.route('/api/active/check_before_action', methods=['POST'])
def check_before_action():
    """Check memory before Claude takes an action"""
    data = request.json
    action = data.get('action', '')
    params = data.get('params', {})
    
    # Build context-aware query
    query_parts = [action]
    
    if 'file_path' in params:
        query_parts.append(Path(params['file_path']).name)
        memory_context.update_file(params['file_path'])
    
    query_parts.extend(memory_context.technologies)
    query_parts.append('error bug fix solution')
    
    query = ' '.join(query_parts)
    
    # Search memory
    from memory_search import MemorySearcher
    searcher = MemorySearcher()
    
    results = searcher.search(
        query=query,
        n_results=5,
        min_similarity=0.4
    )
    
    warnings = []
    suggestions = []
    
    for result in results:
        similarity = result.get('similarity', 0)
        preview = result.get('preview', '').lower()
        
        # High similarity error patterns
        if similarity > 0.6 and ('error' in preview or 'bug' in preview or 'failed' in preview):
            warnings.append({
                'level': 'high',
                'message': f"Similar issue found ({result.get('date', 'unknown')}): {result.get('title', 'Unknown')}",
                'preview': result.get('preview', '')[:200]
            })
            
            # Extract solution if present
            solution_match = re.search(r'fixed by (.+?)\.', preview, re.IGNORECASE)
            if solution_match:
                suggestions.append(f"Previous solution: {solution_match.group(1)}")
        
        # Medium similarity successful patterns
        elif similarity > 0.5 and ('success' in preview or 'completed' in preview):
            suggestions.append(f"Related success: {result.get('title', 'Unknown')}")
    
    # Check error patterns
    if memory_context.error_patterns:
        repeated_errors = [k for k, v in memory_context.error_patterns.items() if v['count'] > 2]
        if repeated_errors:
            warnings.append({
                'level': 'medium',
                'message': f"Repeated errors detected: {len(repeated_errors)} patterns",
                'patterns': repeated_errors[:3]
            })
    
    return jsonify({
        'success': True,
        'data': {
            'action': action,
            'warnings': warnings,
            'suggestions': suggestions,
            'should_proceed': len([w for w in warnings if w.get('level') == 'high']) == 0,
            'context': memory_context.get_context_summary()
        }
    })

def initialize_active_memory(app, searcher, project_root=None):
    """Initialize active memory features"""
    
    # Register blueprint
    app.register_blueprint(active_memory)
    
    # Set project root
    if project_root:
        memory_context.project_root = Path(project_root)
    else:
        # Try to detect project root
        memory_context.project_root = Path.cwd()
    
    # Start file watcher if project root exists
    if memory_context.project_root and memory_context.project_root.exists():
        try:
            event_handler = ClaudeFileWatcher(searcher, memory_context.project_root)
            observer = Observer()
            observer.schedule(event_handler, str(memory_context.project_root), recursive=True)
            observer.start()
            active_memory.file_observer = observer
            logger.info(f"Started file watcher for {memory_context.project_root}")
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
    
    # Start log monitoring
    log_files = [
        'memory_api.log',
        str(Path(memory_context.project_root) / 'error.log'),
        str(Path(memory_context.project_root) / 'app.log'),
    ]
    
    log_monitor = LogMonitor([f for f in log_files if Path(f).exists()])
    log_monitor.start_monitoring()
    active_memory.log_monitor = log_monitor
    
    logger.info("Active memory features initialized")
    
    return active_memory