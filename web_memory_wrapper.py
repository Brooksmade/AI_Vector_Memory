#!/usr/bin/env python3
"""
Web interface wrapper for memory search functionality.
Returns JSON results that can be easily parsed by the web interface.
"""

import sys
import json
from pathlib import Path

# Add the scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from memory_search import MemorySearcher
    
    def web_memory_search(query, max_results=3):
        """
        Search memory and return JSON results for web interface.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            JSON string with search results
        """
        try:
            searcher = MemorySearcher()
            results = searcher.search(query, n_results=max_results, min_similarity=0.3)
            
            # Format results for web interface
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result["title"],
                    "filename": result["filename"],
                    "date": result["date"],
                    "similarity_score": f"{result['similarity']:.1%}",
                    "relevance_score": f"{result['hybrid_score']:.1%}",
                    "technologies": result["technologies"],
                    "complexity": result["complexity"],
                    "preview": result["preview"][:200] + "..." if len(result["preview"]) > 200 else result["preview"],
                    "file_path": str(result["file_path"])
                })
            
            return {
                "success": True,
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results_count": 0,
                "results": []
            }
    
    def main():
        """Command line interface for web wrapper."""
        if len(sys.argv) < 2:
            print(json.dumps({
                "success": False,
                "error": "Usage: python web_memory_wrapper.py <search_query>",
                "results_count": 0,
                "results": []
            }))
            return
        
        query = " ".join(sys.argv[1:])
        result = web_memory_search(query)
        print(json.dumps(result, indent=2))

    if __name__ == "__main__":
        main()

except ImportError as e:
    # Handle case where dependencies aren't available
    error_result = {
        "success": False,
        "error": f"Memory system not properly initialized: {e}",
        "query": sys.argv[1] if len(sys.argv) > 1 else "",
        "results_count": 0,
        "results": []
    }
    print(json.dumps(error_result, indent=2))
