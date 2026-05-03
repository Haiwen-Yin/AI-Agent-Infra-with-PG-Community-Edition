#!/usr/bin/env python3
"""
Basic Usage Examples for memory-pg18-by-yhw v0.3.1
=====================================================

This script demonstrates how to use the Memory System with PostgreSQL 18 + Apache AGE.
Platform-agnostic: works with any AI Agent framework.

Requires pg-embedding-gen-by-yhw extension: https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw

Requirements:
    - psycopg2-binary or pg8000
"""
import uuid

import os
import json
from typing import Optional, List, Dict, Any
import psycopg2


class MemorySystem:
    """Platform-agnostic AI Agent Memory System (v0.3.1)"""
    
    def __init__(self, db_url: str = "postgresql://postgres:***@localhost:5432/memory_graph"):
        """Initialize connection to PostgreSQL database
        
        Args:
            db_url: Database connection string
        """
        self.conn = psycopg2.connect(db_url)
    
    def add_concept(
        self, 
        name: str, 
        category: str = 'custom',
        description: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ) -> str:
        """Add a new concept to memory
        
        Args:
            name: Concept identifier/name
            category: Category for filtering
            description: Human-readable description
            content: JSON metadata (optional)
            embedding: Pre-computed embedding vector (optional)
            
        Returns:
            UUID of the created concept
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT memory.add_concept(%s, %s, %s, %s::jsonb, %s::vector)
            """, (name, category, description or '', json.dumps(content) if content else '{}', embedding))
            
            concept_id = cur.fetchone()[0]
            self.conn.commit()
            return str(concept_id)
    
    def add_relation(
        self, 
        from_concept: str, 
        to_concept: str, 
        relation_type: str = 'related_to',
        strength: float = 1.0
    ) -> bool:
        """Create a relationship between two concepts
        
        Args:
            from_concept: UUID or name of source concept
            to_concept: UUID or name of target concept
            relation_type: Type of relationship (e.g., 'related_to', 'extends')
            strength: Relationship strength (0.0 - 1.0)
            
        Returns:
            True if successful
        """
        with self.conn.cursor() as cur:
            # Resolve names to UUIDs if needed
            concept_ids = []
            for name in [from_concept, to_concept]:
                cur.execute("SELECT concept_id FROM memory.concepts WHERE name = %s", (name,))
                result = cur.fetchone()
                if not result:
                    try:
                        uuid.UUID(name)
                        concept_ids.append(name)
                    except ValueError:
                        raise ValueError(f"Concept '{name}' not found")
                else:
                    concept_ids.append(str(result['concept_id']))
            
            cur.execute("""
                SELECT memory.add_relation(%s, %s, %s, %s)
            """, (concept_ids[0], concept_ids[1], relation_type, strength))
            
            self.conn.commit()
            return True
    
    def search_similar(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar concepts using vector similarity
        
        Requires pg-embedding-gen-by-yhw extension (v0.3.1+) or external embedding API
        
        Args:
            query: Search text/query
            limit: Maximum results to return
            
        Returns:
            List of matching concepts with similarity scores
        """
        with self.conn.cursor() as cur:
            # Use the new memory.generate_embedding_sql() function (v0.3.1)
            if hasattr(cur, 'execute'):
                try:
                    cur.execute("""
                        SELECT c.concept_id, c.name, c.category, 
                               memory.cosine_similarity(c.embedding_vector, %s::vector) as similarity_score
                        FROM memory.concepts c
                        WHERE c.embedding_vector IS NOT NULL
                        ORDER BY similarity_score DESC
                        LIMIT %s
                    """, (query, limit))
                    
                    results = []
                    for row in cur.fetchall():
                        results.append({
                            'concept_id': str(row[0]),
                            'name': row[1],
                            'category': row[2],
                            'similarity': float(row[3])
                        })
                    return results
                except Exception:
                    pass
            
            # Fallback: SQL-based embedding via pg-embedding-gen-by-yhw
            cur.execute("""
                SELECT c.concept_id, c.name, 
                       memory.cosine_similarity(c.embedding_vector, %s::vector) as similarity_score
                FROM memory.concepts c
                ORDER BY similarity_score DESC
                LIMIT %s
            """, (query, limit))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'concept_id': str(row[0]),
                    'name': row[1],
                    'similarity': float(row[2])
                })
            return results


if __name__ == '__main__':
    # Example usage
    print("memory-pg18-by-yhw v0.3.1 - Basic Usage Examples")
    print("=" * 50)
    print("For full documentation see SKILL.md or visit:")
    print("https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw")
