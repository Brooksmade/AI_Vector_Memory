#!/usr/bin/env python3
"""
Test script to verify the memory system works from the web interface.
"""

import sys
import json
from pathlib import Path

# Add the scripts directory to path so we can import
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    import chromadb
    import chromadb.errors
    from rich.console import Console
    
    console = Console()
    
    # Configuration
    DB_PATH = Path(__file__).parent / "chroma_db"
    COLLECTION_NAME = "claude_summaries"
    
    def test_database_connection():
        """Test if we can connect to the database."""
        try:
            console.print("[cyan]Testing database connection...[/cyan]")
            
            client = chromadb.PersistentClient(path=str(DB_PATH))
            console.print("✅ ChromaDB client connected successfully")
            
            try:
                collection = client.get_collection(name=COLLECTION_NAME)
                count = collection.count()
                console.print(f"✅ Collection '{COLLECTION_NAME}' found with {count} documents")
                return client, collection
            except chromadb.errors.NotFoundError:
                console.print(f"⚠️  Collection '{COLLECTION_NAME}' not found")
                console.print("This means the database exists but hasn't been indexed yet")
                return client, None
                
        except Exception as e:
            console.print(f"❌ Database connection failed: {e}")
            return None, None
    
    def test_sample_search(collection):
        """Test a sample search query."""
        if not collection:
            console.print("⚠️  Cannot test search - no collection available")
            return
        
        try:
            console.print("\n[cyan]Testing sample search...[/cyan]")
            
            # Try a simple search
            results = collection.query(
                query_texts=["test search query"],
                n_results=3,
                include=["metadatas", "documents", "distances"]
            )
            
            if results["ids"][0]:
                console.print(f"✅ Search successful - found {len(results['ids'][0])} results")
                
                # Show first result
                if results["metadatas"][0]:
                    first_meta = results["metadatas"][0][0]
                    console.print(f"   First result: {first_meta.get('title', 'No title')}")
                    console.print(f"   Date: {first_meta.get('session_date', 'No date')}")
                    console.print(f"   Similarity: {1/(1+results['distances'][0][0]):.1%}")
            else:
                console.print("✅ Search executed but no results found (empty database)")
                
        except Exception as e:
            console.print(f"❌ Search test failed: {e}")
    
    def main():
        """Run all tests."""
        console.print("[bold cyan]Memory System Test from Web Interface[/bold cyan]\n")
        
        # Test 1: Database connection
        client, collection = test_database_connection()
        
        # Test 2: Sample search
        if collection:
            test_sample_search(collection)
        
        # Test 3: Check dependencies
        console.print("\n[cyan]Checking dependencies...[/cyan]")
        try:
            from sentence_transformers import SentenceTransformer
            console.print("✅ sentence-transformers available")
            
            # Try to load the model
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            console.print("✅ Embedding model loaded successfully")
            
        except Exception as e:
            console.print(f"❌ Dependency issue: {e}")
        
        console.print("\n[green]Test complete![/green]")
        
        return {
            "database_accessible": client is not None,
            "collection_exists": collection is not None,
            "document_count": collection.count() if collection else 0
        }

    if __name__ == "__main__":
        result = main()
        print(f"\nTEST_RESULT_JSON: {json.dumps(result)}")

except ImportError as e:
    print(f"Import error: {e}")
    print("This suggests the virtual environment needs to be activated or dependencies installed")
except Exception as e:
    print(f"Unexpected error: {e}")
