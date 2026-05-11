#!/usr/bin/env python3
"""
PostgreSQL 18 Memory System v1.0.0 - Knowledge Base Python API
============================================================================
Description: Python API for Knowledge Base operations with Knowledge Graph support
Version: 1.0.0-KB-PG18
Author: Haiwen Yin (胖头鱼 🐟)
Date: 2026-05-10
Requirements:
- Python 3.8+
- psycopg2 for PostgreSQL connection
- pgvector extension installed
- BGE-M3 embedding API at http://10.10.10.1:12345/v1
============================================================================
"""

import psycopg2
import psycopg2.extras
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Configuration
DEFAULT_DB_CONFIG = {
    'host': '10.10.10.131',
    'port': 5432,
    'database': 'memory_graph',
    'user': 'pgsql',
    'password': None  # Using .pgpass or trust authentication
}

BGE_M3_API = "http://10.10.10.1:12345/v1/embeddings"
BGE_M3_MODEL = "text-embedding-bge-m3"

class KnowledgeBaseAPI:
    """Python API for Knowledge Base operations on PostgreSQL 18"""
    
    def __init__(self, db_config: Dict[str, Any] = None):
        """
        Initialize Knowledge Base API
        
        Args:
            db_config: Database connection configuration
        """
        self.db_config = db_config or DEFAULT_DB_CONFIG
        self.connection = None
        
    def connect(self) -> bool:
        """
        Connect to PostgreSQL database
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config.get('password')
            )
            self.connection.autocommit = False
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_sql(self, sql: str, params: Tuple = None, fetch: bool = False) -> Any:
        """
        Execute SQL statement
        
        Args:
            sql: SQL statement to execute
            params: Parameters for parameterized queries
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, affected row count otherwise
        """
        if not self.connection:
            if not self.connect():
                raise Exception("Database connection failed")
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute(sql, params or ())
            
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                affected = cursor.rowcount
                self.connection.commit()
                cursor.close()
                return affected
                
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            raise Exception(f"SQL execution error: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using BGE-M3 model
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values (1024 dimensions)
        """
        try:
            payload = {
                "model": BGE_M3_MODEL,
                "input": text
            }
            
            response = requests.post(BGE_M3_API, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                embedding = data["data"][0].get("embedding", [])
                if len(embedding) == 1024:
                    return embedding
                else:
                    print(f"Warning: Expected 1024 dimensions, got {len(embedding)}")
                    return embedding
            else:
                raise Exception("Unexpected API response format")
                
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return [0.0] * 1024
    
    # ====================================================================
    # KNOWLEDGE CONCEPTS OPERATIONS

    # ====================================================================
    
    def create_concept(self, 
                     concept_name: str,
                     concept_type: str,
                     title: str = None,
                     description: str = None,
                     content: str = None,
                     category: str = None,
                     confidence: float = 0.8,
                     source_type: str = 'MANUAL',
                     source_memory_ids: str = None,
                     tags: List[str] = None,
                     metadata: Dict[str, Any] = None) -> int:
        """
        Create a new knowledge concept
        
        Args:
            concept_name: Name of the concept
            concept_type: Type/classification of concept
            title: Optional title
            description: Optional description
            content: Optional detailed content
            category: Optional category classification
            confidence: Confidence score (0.0-1.0)
            source_type: Where this knowledge came from
            source_memory_ids: Source memory IDs if derived from memories
            tags: List of tag names
            metadata: Additional metadata as JSON
            
        Returns:
            New concept ID
        """
        # Generate embedding from combined text
        text_to_embed = f"{concept_name} {title or ''} {description or ''} {content or ''}"
        embedding = self.generate_embedding(text_to_embed)
        
        sql = """
        INSERT INTO knowledge_concepts 
        (concept_name, concept_type, title, description, content, 
         category, confidence, source_type, source_memory_ids, 
         embedding, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING concept_id
        """
        
        result = self.execute_sql(sql, (
            concept_name,
            concept_type,
            title,
            description,
            content,
            category,
            confidence,
            source_type,
            source_memory_ids,
            embedding,
            json.dumps(metadata) if metadata else None
        ), fetch=True)
        
        concept_id = result[0]['concept_id']
        
        # Add tags if provided
        if tags:
            for tag_name in tags:
                self.add_tag_to_concept(concept_id, tag_name)
        
        return concept_id
    
    def get_concept(self, concept_id: int) -> Optional[Dict[str, Any]]:
        """
        Get concept by ID
        
        Args:
            concept_id: Concept ID
            
        Returns:
            Concept data dictionary or None
        """
        sql = """
        SELECT concept_id, concept_name, concept_type, title, description,
               content, category, confidence, source_type, source_memory_ids,
               created_at, updated_at, validated_at, deprecated_at, 
               version, is_current
        FROM knowledge_concepts
        WHERE concept_id = %s
        """
        
        results = self.execute_sql(sql, (concept_id,), fetch=True)
        
        if results:
            return results[0]
        return None
    
    def search_concepts_by_text(self, 
                              query_text: str, 
                              limit: int = 10,
                              concept_type: str = None) -> List[Dict[str, Any]]:
        """
        Search concepts by text using vector similarity
        
        Args:
            query_text: Search query text
            limit: Maximum number of results
            concept_type: Optional filter by concept type
            
        Returns:
            List of matching concepts with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query_text)
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"
        
        sql = f"""
        SELECT concept_id, concept_name, concept_type, title, confidence,
               1 - (embedding <=> '{embedding_str}'::vector(1024)) as similarity_score
        FROM knowledge_concepts
        WHERE embedding IS NOT NULL
        """
        
        params = []
        
        if concept_type:
            sql += " AND concept_type = %s"
            params.append(concept_type)
        
        sql += f"""
        ORDER BY embedding <=> '{embedding_str}'::vector(1024)
        LIMIT %s
        """
        params.append(limit)
        
        return self.execute_sql(sql, tuple(params), fetch=True)
    
    def update_concept(self, 
                      concept_id: int,
                      title: str = None,
                      description: str = None,
                      content: str = None,
                      confidence: float = None,
                      validation_status: str = None) -> bool:
        """
        Update concept (non-destructive, creates version)
        
        Args:
            concept_id: Concept ID to update
            title: New title
            description: New description
            content: New content
            confidence: New confidence score
            validation_status: Validation status
            
        Returns:
            True if successful
        """
        # Get current concept
        current = self.get_concept(concept_id)
        if not current:
            return False
        
        # Create version entry before update
        self.create_version_entry(concept_id, current)
        
        # Update concept
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        if content is not None:
            update_fields.append("content = %s")
            params.append(content)
        if confidence is not None:
            update_fields.append("confidence = %s")
            params.append(confidence)
        if validation_status is not None:
            update_fields.append("validation_status = %s")
            params.append(validation_status)
        
        if not update_fields:
            return False
        
        params.append(concept_id)
        
        sql = f"""
        UPDATE knowledge_concepts
        SET {', '.join(update_fields)}
        WHERE concept_id = %s
        """
        
        self.execute_sql(sql, tuple(params))
        return True
    
    # ====================================================================
    # KNOWLEDGE GRAPH OPERATIONS
    # ====================================================================
    
    def create_relationship(self,
                        source_concept_id: int,
                        target_concept_id: int,
                        relationship_type: str,
                        relationship_strength: float = 1.0,
                        properties: Dict[str, Any] = None,
                        confidence: float = 0.8) -> int:
        """
        Create knowledge relationship
        
        Args:
            source_concept_id: Source concept ID
            target_concept_id: Target concept ID
            relationship_type: Type of relationship
            relationship_strength: Strength (0.0-1.0)
            properties: Additional properties
            confidence: Confidence score
            
        Returns:
            New relationship ID
        """
        sql = """
        INSERT INTO knowledge_graph 
        (source_concept_id, target_concept_id, relationship_type, 
         relationship_strength, properties, confidence)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING relationship_id
        """
        
        result = self.execute_sql(sql, (
            source_concept_id,
            target_concept_id,
            relationship_type,
            relationship_strength,
            json.dumps(properties) if properties else None,
            confidence
        ), fetch=True)
        
        return result[0]['relationship_id']
    
    def get_related_concepts(self, 
                             concept_id: int, 
                             relationship_type: str = None,
                             direction: str = 'both') -> List[Dict[str, Any]]:
        """
        Get concepts related to a given concept
        
        Args:
            concept_id: Starting concept ID
            relationship_type: Optional filter by relationship type
            direction: 'outgoing', 'incoming', or 'both'
            
        Returns:
            List of related concepts
        """
        if direction == 'outgoing':
            sql = """
            SELECT r.*, k.concept_name, k.concept_type, k.title
            FROM knowledge_graph r
            JOIN knowledge_concepts k ON r.target_concept_id = k.concept_id
            WHERE r.source_concept_id = %s
            """
        elif direction == 'incoming':
            sql = """
            SELECT r.*, k.concept_name, k.concept_type, k.title
            FROM knowledge_graph r
            JOIN knowledge_concepts k ON r.source_concept_id = k.concept_id
            WHERE r.target_concept_id = %s
            """
        else:
            sql = """
            SELECT r.*, k.concept_name, k.concept_type, k.title
            FROM knowledge_graph r
            JOIN knowledge_concepts k ON 
                (r.target_concept_id = k.concept_id OR r.source_concept_id = k.concept_id)
            WHERE r.source_concept_id = %s OR r.target_concept_id = %s
            """
        
        params = [concept_id] if direction != 'both' else [concept_id, concept_id]
        
        if relationship_type:
            sql += " AND r.relationship_type = %s"
            params.append(relationship_type)
        
        return self.execute_sql(sql, tuple(params), fetch=True)
    
    # ====================================================================
    # TAGS OPERATIONS
    # ====================================================================
    
    def add_tag_to_concept(self, concept_id: int, tag_name: str) -> bool:
        """Add tag to concept"""
        # First ensure tag exists
        get_tag_sql = "SELECT tag_id FROM knowledge_tags WHERE tag_name = %s"
        existing = self.execute_sql(get_tag_sql, (tag_name,), fetch=True)
        
        if existing:
            tag_id = existing[0]['tag_id']
        else:
            create_tag_sql = """
            INSERT INTO knowledge_tags (tag_name, usage_count)
            VALUES (%s, 1)
            RETURNING tag_id
            """
            result = self.execute_sql(create_tag_sql, (tag_name,), fetch=True)
            tag_id = result[0]['tag_id']
        
        # Link tag to concept
        link_sql = """
        INSERT INTO knowledge_concept_tags (concept_id, tag_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """
        
        self.execute_sql(link_sql, (concept_id, tag_id))
        return True
    
    # ====================================================================
    # VERSION HISTORY OPERATIONS
    # ====================================================================
    
    def create_version_entry(self, concept_id: int, concept_data: Dict[str, Any]) -> int:
        """
        Create version entry for concept before update
        
        Args:
            concept_id: Concept ID
            concept_data: Current concept data
            
        Returns:
            New version ID
        """
        sql = """
        INSERT INTO knowledge_versions 
        (concept_id, title, description, content, versioned_by)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING version_id
        """
        
        result = self.execute_sql(sql, (
            concept_id,
            concept_data.get('title'),
            concept_data.get('description'),
            concept_data.get('content'),
            'system'
        ), fetch=True)
        
        return result[0]['version_id']
    
    # ====================================================================
    # STATISTICS AND QUERIES
    # ====================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        sql = """
        SELECT 
            (SELECT COUNT(*) FROM knowledge_concepts) as total_concepts,
            (SELECT COUNT(*) FROM knowledge_graph) as total_relationships,
            (SELECT COUNT(*) FROM knowledge_tags) as total_tags,
            (SELECT COUNT(*) FROM knowledge_concepts WHERE validation_status = 'VALIDATED') as validated_concepts
        """
        
        result = self.execute_sql(sql, fetch=True)
        
        if result:
            return result[0]
        return {}
    
    def get_concepts_by_type(self, concept_type: str) -> List[Dict[str, Any]]:
        """Get all concepts of a specific type"""
        sql = """
        SELECT concept_id, concept_name, title, confidence, validation_status
        FROM knowledge_concepts
        WHERE concept_type = %s
        ORDER BY created_at DESC
        """
        
        return self.execute_sql(sql, (concept_type,), fetch=True)


# ====================================================================
# USAGE EXAMPLE
# ====================================================================

if __name__ == "__main__":
    # Create API instance
    kb_api = KnowledgeBaseAPI()
    
    try:
        # Connect to database
        if kb_api.connect():
            print("Connected to PostgreSQL knowledge base")
            
            # Get statistics
            stats = kb_api.get_statistics()
            print(f"\nStatistics: {stats}")
            
            # Create a test concept
            concept_id = kb_api.create_concept(
                concept_name="PostgreSQL 18",
                concept_type="database",
                title="PostgreSQL 18 Database",
                description="Latest version of PostgreSQL with pgvector and AGE extensions",
                category="technology",
                confidence=0.95,
                tags=["database", "postgresql", "vector-search"]
            )
            print(f"\nCreated concept ID: {concept_id}")
            
            # Search concepts
            results = kb_api.search_concepts_by_text("vector database search", limit=5)
            print(f"\nSearch results: {len(results)} concepts found")
            for r in results:
                print(f"  - {r['concept_name']} (similarity: {r['similarity_score']:.3f})")
            
            # Disconnect
            kb_api.disconnect()
            print("\nDisconnected from database")
        else:
            print("Failed to connect to database")
            
    except Exception as e:
        print(f"Error: {e}")
        if kb_api.connection:
            kb_api.disconnect()
