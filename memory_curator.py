"""
Memory Curator - Advanced memory management and curation system
Handles deduplication, consolidation, quality scoring, and lifecycle management
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple
import hashlib
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('memory_curator')

class MemoryCurator:
    """Manages the quality and lifecycle of memories"""
    
    def __init__(self, searcher, indexer):
        self.searcher = searcher
        self.indexer = indexer
        self.quality_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
    def analyze_memory_health(self) -> Dict[str, Any]:
        """Analyze overall health of memory database"""
        try:
            # Get all memories
            results = self.searcher.collection.get(include=["metadatas", "documents"])
            
            if not results['ids']:
                return {'status': 'empty', 'total_memories': 0}
            
            memories = []
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                content = results['documents'][i] if results['documents'] else ''
                memories.append({
                    'id': doc_id,
                    'metadata': metadata,
                    'content': content
                })
            
            # Calculate statistics
            stats = {
                'total_memories': len(memories),
                'duplicates': self._find_duplicates(memories),
                'stale_memories': self._find_stale_memories(memories),
                'error_patterns': self._analyze_error_patterns(memories),
                'technology_distribution': self._get_technology_distribution(memories),
                'quality_distribution': self._assess_quality_distribution(memories),
                'consolidation_opportunities': self._find_consolidation_opportunities(memories),
                'memory_age_distribution': self._get_age_distribution(memories)
            }
            
            # Generate recommendations
            stats['recommendations'] = self._generate_recommendations(stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing memory health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _find_duplicates(self, memories: List[Dict]) -> Dict[str, Any]:
        """Find duplicate or near-duplicate memories"""
        duplicates = []
        content_hashes = defaultdict(list)
        
        # Check exact duplicates via content hash
        for memory in memories:
            content = memory.get('content', '')
            if content:
                content_hash = hashlib.md5(content.encode()).hexdigest()
                content_hashes[content_hash].append(memory['id'])
        
        exact_duplicates = [ids for ids in content_hashes.values() if len(ids) > 1]
        
        # Check near-duplicates via similarity
        if len(memories) > 1:
            try:
                contents = [m.get('content', '')[:500] for m in memories]  # Use first 500 chars
                if any(contents):
                    # Filter out empty contents
                    valid_contents = [c for c in contents if c]
                    if len(valid_contents) > 1:
                        vectors = self.vectorizer.fit_transform(valid_contents)
                        similarity_matrix = cosine_similarity(vectors)
                        
                        near_duplicates = []
                        for i in range(len(valid_contents)):
                            for j in range(i + 1, len(valid_contents)):
                                if similarity_matrix[i, j] > 0.85:  # 85% similarity threshold
                                    near_duplicates.append({
                                        'memory1': memories[i]['id'],
                                        'memory2': memories[j]['id'],
                                        'similarity': float(similarity_matrix[i, j])
                                    })
                        
                        duplicates = {
                            'exact': exact_duplicates,
                            'near': near_duplicates[:10]  # Limit to top 10
                        }
            except Exception as e:
                logger.warning(f"Error finding near-duplicates: {e}")
                duplicates = {'exact': exact_duplicates, 'near': []}
        else:
            duplicates = {'exact': exact_duplicates, 'near': []}
        
        return duplicates
    
    def _find_stale_memories(self, memories: List[Dict], days_threshold: int = 90) -> List[Dict]:
        """Find memories that haven't been accessed recently"""
        stale = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        for memory in memories:
            metadata = memory.get('metadata', {})
            
            # Check last access date
            last_access = metadata.get('last_accessed')
            if not last_access:
                # Check creation date as fallback
                date_str = metadata.get('date') or metadata.get('session_date')
                if date_str:
                    try:
                        memory_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        if memory_date < cutoff_date:
                            stale.append({
                                'id': memory['id'],
                                'date': date_str,
                                'title': metadata.get('title', 'Untitled')
                            })
                    except:
                        pass
        
        return stale[:20]  # Return top 20 stale memories
    
    def _analyze_error_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns in memories"""
        error_memories = []
        error_types = defaultdict(int)
        
        for memory in memories:
            content = memory.get('content', '').lower()
            metadata = memory.get('metadata', {})
            
            # Check if this is an error-related memory
            if any(term in content for term in ['error', 'failed', 'exception', 'bug', 'issue']):
                error_memories.append(memory)
                
                # Categorize error type
                if 'typeerror' in content:
                    error_types['TypeError'] += 1
                elif 'syntaxerror' in content:
                    error_types['SyntaxError'] += 1
                elif 'null' in content or 'undefined' in content:
                    error_types['NullReference'] += 1
                elif 'import' in content or 'module' in content:
                    error_types['ImportError'] += 1
                else:
                    error_types['Other'] += 1
        
        # Find most common error patterns
        common_patterns = []
        if error_memories:
            # Extract error messages
            error_messages = []
            for mem in error_memories[:50]:  # Analyze top 50
                content = mem.get('content', '')
                # Try to extract error message
                error_match = re.search(r'error[:\s]+([^\n]{20,100})', content, re.IGNORECASE)
                if error_match:
                    error_messages.append(error_match.group(1))
            
            # Find common substrings
            if error_messages:
                common_patterns = self._find_common_patterns(error_messages)
        
        return {
            'total_error_memories': len(error_memories),
            'error_types': dict(error_types),
            'common_patterns': common_patterns[:5],
            'error_rate': len(error_memories) / len(memories) if memories else 0
        }
    
    def _find_common_patterns(self, messages: List[str]) -> List[str]:
        """Find common patterns in error messages"""
        # Simple pattern extraction - find common substrings
        patterns = defaultdict(int)
        
        for msg in messages:
            # Extract potential patterns (words/phrases)
            words = msg.split()
            for i in range(len(words)):
                for j in range(i + 1, min(i + 4, len(words) + 1)):
                    pattern = ' '.join(words[i:j])
                    if len(pattern) > 10:  # Minimum pattern length
                        patterns[pattern] += 1
        
        # Return patterns that appear multiple times
        common = [p for p, count in patterns.items() if count > 1]
        common.sort(key=lambda x: patterns[x], reverse=True)
        return common
    
    def _get_technology_distribution(self, memories: List[Dict]) -> Dict[str, int]:
        """Get distribution of technologies mentioned in memories"""
        tech_count = defaultdict(int)
        
        for memory in memories:
            metadata = memory.get('metadata', {})
            
            # Check technologies field
            tech_str = metadata.get('technologies', '[]')
            try:
                if isinstance(tech_str, str):
                    technologies = json.loads(tech_str)
                else:
                    technologies = tech_str
                    
                for tech in technologies:
                    tech_count[tech] += 1
            except:
                pass
        
        # Sort by count
        sorted_tech = dict(sorted(tech_count.items(), key=lambda x: x[1], reverse=True)[:10])
        return sorted_tech
    
    def _assess_quality_distribution(self, memories: List[Dict]) -> Dict[str, int]:
        """Assess quality of memories"""
        quality_dist = {'high': 0, 'medium': 0, 'low': 0}
        
        for memory in memories:
            score = self._calculate_memory_quality_score(memory)
            
            if score >= self.quality_thresholds['high']:
                quality_dist['high'] += 1
            elif score >= self.quality_thresholds['medium']:
                quality_dist['medium'] += 1
            else:
                quality_dist['low'] += 1
        
        return quality_dist
    
    def _calculate_memory_quality_score(self, memory: Dict) -> float:
        """Calculate quality score for a memory"""
        score = 0.0
        metadata = memory.get('metadata', {})
        content = memory.get('content', '')
        
        # Content length (longer is generally better)
        if len(content) > 500:
            score += 0.2
        elif len(content) > 200:
            score += 0.1
        
        # Has title
        if metadata.get('title') and metadata.get('title') != 'Untitled':
            score += 0.2
        
        # Has technologies
        if metadata.get('technologies'):
            score += 0.15
        
        # Has complexity rating
        if metadata.get('complexity'):
            score += 0.1
        
        # Has date
        if metadata.get('date') or metadata.get('session_date'):
            score += 0.1
        
        # Has source
        if metadata.get('source'):
            score += 0.1
        
        # Contains code blocks (valuable for technical memories)
        if '```' in content:
            score += 0.15
        
        return min(score, 1.0)
    
    def _find_consolidation_opportunities(self, memories: List[Dict]) -> List[Dict]:
        """Find memories that could be consolidated"""
        opportunities = []
        
        # Group by similar titles or dates
        title_groups = defaultdict(list)
        date_groups = defaultdict(list)
        
        for memory in memories:
            metadata = memory.get('metadata', {})
            
            # Group by title similarity
            title = metadata.get('title', '')
            if title and title != 'Untitled':
                # Normalize title for grouping
                title_key = re.sub(r'[^a-z0-9]+', '', title.lower())[:20]
                title_groups[title_key].append(memory)
            
            # Group by date
            date = metadata.get('date') or metadata.get('session_date')
            if date:
                date_groups[date[:10]].append(memory)  # Group by day
        
        # Find groups with multiple memories
        for title_key, group in title_groups.items():
            if len(group) > 2:
                opportunities.append({
                    'type': 'similar_title',
                    'count': len(group),
                    'sample': group[0].get('metadata', {}).get('title', 'Unknown'),
                    'memory_ids': [m['id'] for m in group[:5]]
                })
        
        for date, group in date_groups.items():
            if len(group) > 3:
                opportunities.append({
                    'type': 'same_date',
                    'date': date,
                    'count': len(group),
                    'memory_ids': [m['id'] for m in group[:5]]
                })
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def _get_age_distribution(self, memories: List[Dict]) -> Dict[str, int]:
        """Get age distribution of memories"""
        age_dist = {
            'today': 0,
            'this_week': 0,
            'this_month': 0,
            'this_quarter': 0,
            'older': 0
        }
        
        now = datetime.now()
        
        for memory in memories:
            metadata = memory.get('metadata', {})
            date_str = metadata.get('date') or metadata.get('session_date')
            
            if date_str:
                try:
                    memory_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    age_days = (now - memory_date).days
                    
                    if age_days == 0:
                        age_dist['today'] += 1
                    elif age_days <= 7:
                        age_dist['this_week'] += 1
                    elif age_days <= 30:
                        age_dist['this_month'] += 1
                    elif age_days <= 90:
                        age_dist['this_quarter'] += 1
                    else:
                        age_dist['older'] += 1
                except:
                    pass
        
        return age_dist
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Check for duplicates
        duplicates = stats.get('duplicates', {})
        if duplicates.get('exact'):
            recommendations.append(f"Remove {len(duplicates['exact'])} exact duplicate memories")
        if duplicates.get('near'):
            recommendations.append(f"Review {len(duplicates['near'])} near-duplicate memories for consolidation")
        
        # Check for stale memories
        stale = stats.get('stale_memories', [])
        if len(stale) > 10:
            recommendations.append(f"Archive {len(stale)} stale memories (>90 days old)")
        
        # Check quality distribution
        quality = stats.get('quality_distribution', {})
        if quality.get('low', 0) > quality.get('high', 0):
            recommendations.append("Improve memory quality by adding titles, technologies, and structure")
        
        # Check error rate
        error_stats = stats.get('error_patterns', {})
        if error_stats.get('error_rate', 0) > 0.3:
            recommendations.append("High error rate detected - consider implementing preventive measures")
        
        # Check consolidation opportunities
        consolidation = stats.get('consolidation_opportunities', [])
        if consolidation:
            recommendations.append(f"Found {len(consolidation)} consolidation opportunities")
        
        # Check total memory count
        total = stats.get('total_memories', 0)
        if total > 500:
            recommendations.append("Consider implementing memory pagination or archival strategy")
        elif total < 10:
            recommendations.append("Memory database is sparse - ensure memories are being captured")
        
        return recommendations
    
    def deduplicate_memories(self, dry_run: bool = True) -> Dict[str, Any]:
        """Remove duplicate memories"""
        results = self.searcher.collection.get(include=["metadatas", "documents"])
        
        if not results['ids']:
            return {'removed': 0, 'message': 'No memories to deduplicate'}
        
        # Find exact duplicates
        content_map = {}
        duplicates_to_remove = []
        
        for i, doc_id in enumerate(results['ids']):
            content = results['documents'][i] if results['documents'] else ''
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash in content_map:
                # This is a duplicate
                duplicates_to_remove.append(doc_id)
            else:
                content_map[content_hash] = doc_id
        
        if not dry_run and duplicates_to_remove:
            # Remove duplicates
            for doc_id in duplicates_to_remove:
                try:
                    self.searcher.collection.delete(ids=[doc_id])
                except Exception as e:
                    logger.error(f"Failed to delete duplicate {doc_id}: {e}")
        
        return {
            'duplicates_found': len(duplicates_to_remove),
            'removed': 0 if dry_run else len(duplicates_to_remove),
            'dry_run': dry_run,
            'duplicate_ids': duplicates_to_remove[:10]  # Show first 10
        }
    
    def consolidate_memories(self, memory_ids: List[str], new_title: str = None) -> Dict[str, Any]:
        """Consolidate multiple memories into one"""
        try:
            # Get the memories to consolidate
            results = self.searcher.collection.get(
                ids=memory_ids,
                include=["metadatas", "documents"]
            )
            
            if not results['ids']:
                return {'success': False, 'error': 'No memories found with provided IDs'}
            
            # Combine contents
            combined_content = []
            combined_technologies = set()
            dates = []
            
            for i, doc_id in enumerate(results['ids']):
                content = results['documents'][i] if results['documents'] else ''
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                
                # Add content with header
                title = metadata.get('title', 'Untitled')
                date = metadata.get('date', 'Unknown date')
                combined_content.append(f"## {title} ({date})\n{content}\n")
                
                # Collect technologies
                tech = metadata.get('technologies')
                if tech:
                    if isinstance(tech, str):
                        try:
                            tech = json.loads(tech)
                        except:
                            tech = []
                    combined_technologies.update(tech)
                
                # Collect dates
                if date != 'Unknown date':
                    dates.append(date)
            
            # Create consolidated memory
            consolidated_title = new_title or f"Consolidated Memory ({len(memory_ids)} memories)"
            consolidated_content = "\n---\n".join(combined_content)
            
            # Determine date range
            if dates:
                dates.sort()
                date_range = f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else dates[0]
            else:
                date_range = datetime.now().strftime('%Y-%m-%d')
            
            # Add consolidated memory
            consolidated_id = f"consolidated_{hashlib.md5(consolidated_content.encode()).hexdigest()[:8]}"
            
            self.indexer.collection.add(
                documents=[consolidated_content],
                metadatas=[{
                    'title': consolidated_title,
                    'date': date_range,
                    'source': 'consolidation',
                    'technologies': json.dumps(list(combined_technologies)),
                    'complexity': 'high',
                    'original_count': len(memory_ids),
                    'consolidated_from': json.dumps(memory_ids),
                    'consolidated_at': datetime.now().isoformat()
                }],
                ids=[consolidated_id]
            )
            
            # Optionally delete original memories
            # for memory_id in memory_ids:
            #     self.searcher.collection.delete(ids=[memory_id])
            
            return {
                'success': True,
                'consolidated_id': consolidated_id,
                'original_count': len(memory_ids),
                'new_title': consolidated_title
            }
            
        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def archive_old_memories(self, days_threshold: int = 90, dry_run: bool = True) -> Dict[str, Any]:
        """Archive memories older than threshold"""
        results = self.searcher.collection.get(include=["metadatas"])
        
        if not results['ids']:
            return {'archived': 0, 'message': 'No memories to archive'}
        
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        to_archive = []
        
        for i, doc_id in enumerate(results['ids']):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            date_str = metadata.get('date') or metadata.get('session_date')
            
            if date_str:
                try:
                    memory_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if memory_date < cutoff_date:
                        to_archive.append({
                            'id': doc_id,
                            'date': date_str,
                            'title': metadata.get('title', 'Untitled')
                        })
                except:
                    pass
        
        if not dry_run and to_archive:
            # Create archive file
            archive_path = Path('memory_archive') / f"archive_{datetime.now().strftime('%Y%m%d')}.json"
            archive_path.parent.mkdir(exist_ok=True)
            
            # Save to archive
            with open(archive_path, 'w') as f:
                json.dump(to_archive, f, indent=2)
            
            # Remove from active database
            for memory in to_archive:
                try:
                    self.searcher.collection.delete(ids=[memory['id']])
                except Exception as e:
                    logger.error(f"Failed to archive {memory['id']}: {e}")
        
        return {
            'found': len(to_archive),
            'archived': 0 if dry_run else len(to_archive),
            'dry_run': dry_run,
            'archive_path': str(archive_path) if not dry_run and to_archive else None,
            'sample': to_archive[:5]  # Show first 5
        }
    
    def enhance_memory_quality(self, memory_id: str) -> Dict[str, Any]:
        """Enhance a low-quality memory with better structure and metadata"""
        try:
            results = self.searcher.collection.get(
                ids=[memory_id],
                include=["metadatas", "documents"]
            )
            
            if not results['ids']:
                return {'success': False, 'error': 'Memory not found'}
            
            metadata = results['metadatas'][0] if results['metadatas'] else {}
            content = results['documents'][0] if results['documents'] else ''
            
            # Enhance metadata
            enhanced_metadata = metadata.copy()
            
            # Generate better title if missing
            if not enhanced_metadata.get('title') or enhanced_metadata.get('title') == 'Untitled':
                # Extract first meaningful line as title
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and len(line) > 10 and len(line) < 100:
                        enhanced_metadata['title'] = line.strip()[:80]
                        break
            
            # Extract technologies from content
            if not enhanced_metadata.get('technologies'):
                tech_keywords = ['python', 'javascript', 'typescript', 'react', 'flask', 
                               'sql', 'html', 'css', 'node', 'npm', 'git', 'docker']
                found_tech = []
                content_lower = content.lower()
                for tech in tech_keywords:
                    if tech in content_lower:
                        found_tech.append(tech)
                if found_tech:
                    enhanced_metadata['technologies'] = json.dumps(found_tech)
            
            # Add complexity rating based on content
            if not enhanced_metadata.get('complexity'):
                if len(content) > 1000 or '```' in content:
                    enhanced_metadata['complexity'] = 'high'
                elif len(content) > 500:
                    enhanced_metadata['complexity'] = 'medium'
                else:
                    enhanced_metadata['complexity'] = 'low'
            
            # Add enhancement timestamp
            enhanced_metadata['enhanced_at'] = datetime.now().isoformat()
            
            # Update the memory
            self.searcher.collection.update(
                ids=[memory_id],
                metadatas=[enhanced_metadata]
            )
            
            return {
                'success': True,
                'memory_id': memory_id,
                'enhancements': {
                    'title_added': 'title' in enhanced_metadata and 'title' not in metadata,
                    'technologies_added': 'technologies' in enhanced_metadata and 'technologies' not in metadata,
                    'complexity_added': 'complexity' in enhanced_metadata and 'complexity' not in metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            return {'success': False, 'error': str(e)}