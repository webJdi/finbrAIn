from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import json
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os
from pathlib import Path

# Try to import vector stores (may not be available in all setups)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    print("Warning: ChromaDB not available for vector storage")
    CHROMADB_AVAILABLE = False

class MemoryStore(ABC):
    """Abstract base class for memory storage systems"""
    
    @abstractmethod
    async def store_memory(self, memory_id: str, content: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Store a memory with given ID and metadata"""
        pass
    
    @abstractmethod
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID"""
        pass
    
    @abstractmethod
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories based on query"""
        pass
    
    @abstractmethod
    async def get_recent_memories(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories within specified time window"""
        pass

class SQLiteMemoryStore(MemoryStore):
    """SQLite-based memory storage for agent learnings and experiences"""
    
    def __init__(self, db_path: str = "memory/agent_memory.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    memory_type TEXT,
                    source TEXT,
                    importance_score REAL DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_type TEXT,
                    stock_symbol TEXT,
                    session_data TEXT,
                    performance_score REAL,
                    lessons_learned TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_improvements (
                    improvement_id TEXT PRIMARY KEY,
                    agent_type TEXT,
                    improvement_type TEXT,
                    description TEXT,
                    implementation_status TEXT,
                    impact_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_symbol ON learning_sessions(stock_symbol)")
            
            conn.commit()
    
    async def store_memory(self, memory_id: str, content: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Store a memory in SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, metadata, memory_type, source, importance_score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                memory_id,
                json.dumps(content),
                json.dumps(metadata) if metadata else None,
                metadata.get("type", "general") if metadata else "general",
                metadata.get("source", "unknown") if metadata else "unknown",
                metadata.get("importance", 0.5) if metadata else 0.5
            ))
            conn.commit()
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID"""
        with sqlite3.connect(self.db_path) as conn:
            # Update access count and last accessed
            conn.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (memory_id,))
            
            cursor = conn.execute("""
                SELECT content, metadata, created_at, memory_type, importance_score
                FROM memories WHERE id = ?
            """, (memory_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": memory_id,
                    "content": json.loads(row[0]),
                    "metadata": json.loads(row[1]) if row[1] else {},
                    "created_at": row[2],
                    "memory_type": row[3],
                    "importance_score": row[4]
                }
        return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using simple text matching"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, content, metadata, created_at, memory_type, importance_score
                FROM memories 
                WHERE content LIKE ? OR metadata LIKE ?
                ORDER BY importance_score DESC, created_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content": json.loads(row[1]),
                    "metadata": json.loads(row[2]) if row[2] else {},
                    "created_at": row[3],
                    "memory_type": row[4],
                    "importance_score": row[5]
                })
            
            return results
    
    async def get_recent_memories(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories within specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, content, metadata, created_at, memory_type, importance_score
                FROM memories 
                WHERE created_at > ?
                ORDER BY importance_score DESC, created_at DESC
                LIMIT ?
            """, (cutoff_time.isoformat(), limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content": json.loads(row[1]),
                    "metadata": json.loads(row[2]) if row[2] else {},
                    "created_at": row[3],
                    "memory_type": row[4],
                    "importance_score": row[5]
                })
            
            return results

class VectorMemoryStore(MemoryStore):
    """ChromaDB-based vector memory store for semantic search"""
    
    def __init__(self, collection_name: str = "agent_memories"):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required for VectorMemoryStore")
        
        self.collection_name = collection_name
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="memory/vector_db"
        ))
        
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(collection_name)
    
    async def store_memory(self, memory_id: str, content: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Store a memory with vector embeddings"""
        # Convert content to text for embedding
        text_content = self._content_to_text(content)
        
        self.collection.add(
            documents=[text_content],
            metadatas=[metadata or {}],
            ids=[memory_id]
        )
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID"""
        try:
            result = self.collection.get(ids=[memory_id])
            if result['documents']:
                return {
                    "id": memory_id,
                    "content": result['documents'][0],
                    "metadata": result['metadatas'][0] if result['metadatas'] else {}
                }
        except:
            pass
        return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using semantic similarity"""
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        memories = []
        for i, doc_id in enumerate(results['ids'][0]):
            memories.append({
                "id": doc_id,
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "similarity_score": 1 - results['distances'][0][i] if results['distances'] else 0.5
            })
        
        return memories
    
    async def get_recent_memories(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories (limited functionality in vector store)"""
        # Vector stores don't naturally support time-based queries
        # This is a simplified implementation
        cutoff_timestamp = (datetime.now() - timedelta(hours=hours)).timestamp()
        
        all_memories = self.collection.get()
        recent_memories = []
        
        for i, memory_id in enumerate(all_memories['ids']):
            metadata = all_memories['metadatas'][i] if all_memories['metadatas'] else {}
            created_at = metadata.get('created_at')
            
            if created_at and float(created_at) > cutoff_timestamp:
                recent_memories.append({
                    "id": memory_id,
                    "content": all_memories['documents'][i],
                    "metadata": metadata
                })
        
        return recent_memories[:limit]
    
    def _content_to_text(self, content: Dict[str, Any]) -> str:
        """Convert content dictionary to text for embedding"""
        if isinstance(content, str):
            return content
        
        text_parts = []
        for key, value in content.items():
            if isinstance(value, (str, int, float)):
                text_parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                text_parts.append(f"{key}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                text_parts.append(f"{key}: {json.dumps(value)}")
        
        return " | ".join(text_parts)

class AgentMemoryManager:
    """High-level memory manager for financial agents"""
    
    def __init__(self, use_vector_store: bool = True):
        self.sqlite_store = SQLiteMemoryStore()
        
        if use_vector_store and CHROMADB_AVAILABLE:
            try:
                self.vector_store = VectorMemoryStore()
                self.use_vector = True
            except:
                print("Warning: Could not initialize vector store, using SQLite only")
                self.vector_store = None
                self.use_vector = False
        else:
            self.vector_store = None
            self.use_vector = False
    
    async def store_learning(self, 
                           agent_type: str,
                           stock_symbol: str,
                           learning_content: Dict[str, Any],
                           performance_score: float = 0.5,
                           importance: float = 0.5):
        """Store a learning experience"""
        
        # Generate unique memory ID
        memory_id = self._generate_memory_id(agent_type, stock_symbol, learning_content)
        
        # Store in SQLite for structured queries
        await self.sqlite_store.store_memory(
            memory_id,
            learning_content,
            {
                "type": "learning",
                "agent_type": agent_type,
                "stock_symbol": stock_symbol,
                "performance_score": performance_score,
                "importance": importance,
                "created_at": datetime.now().timestamp()
            }
        )
        
        # Store in vector store for semantic search
        if self.use_vector:
            await self.vector_store.store_memory(
                memory_id,
                learning_content,
                {
                    "type": "learning",
                    "agent_type": agent_type,
                    "stock_symbol": stock_symbol,
                    "created_at": datetime.now().timestamp()
                }
            )
        
        return memory_id
    
    async def get_relevant_memories(self, 
                                   query: str,
                                   agent_type: Optional[str] = None,
                                   stock_symbol: Optional[str] = None,
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories relevant to a query"""
        
        if self.use_vector:
            # Use semantic search with vector store
            memories = await self.vector_store.search_memories(query, limit)
        else:
            # Fallback to text search with SQLite
            memories = await self.sqlite_store.search_memories(query, limit)
        
        # Filter by agent type and stock symbol if specified
        if agent_type or stock_symbol:
            filtered_memories = []
            for memory in memories:
                metadata = memory.get("metadata", {})
                if agent_type and metadata.get("agent_type") != agent_type:
                    continue
                if stock_symbol and metadata.get("stock_symbol") != stock_symbol:
                    continue
                filtered_memories.append(memory)
            memories = filtered_memories
        
        return memories[:limit]
    
    async def get_agent_performance_history(self, 
                                          agent_type: str,
                                          stock_symbol: Optional[str] = None,
                                          days: int = 30) -> List[Dict[str, Any]]:
        """Get performance history for an agent"""
        
        query = f"agent_type:{agent_type}"
        if stock_symbol:
            query += f" stock_symbol:{stock_symbol}"
        
        memories = await self.sqlite_store.search_memories(query, limit=100)
        
        # Filter by time period
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_memories = [
            memory for memory in memories
            if datetime.fromisoformat(memory.get("created_at", "1900-01-01")) > cutoff_time
        ]
        
        return recent_memories
    
    async def store_improvement_suggestion(self,
                                         agent_type: str,
                                         improvement_type: str,
                                         description: str,
                                         impact_score: float = 0.5):
        """Store an improvement suggestion for an agent"""
        
        improvement_id = f"improvement_{agent_type}_{int(datetime.now().timestamp())}"
        
        # Store in SQLite's improvement table
        with sqlite3.connect(self.sqlite_store.db_path) as conn:
            conn.execute("""
                INSERT INTO agent_improvements 
                (improvement_id, agent_type, improvement_type, description, implementation_status, impact_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                improvement_id,
                agent_type,
                improvement_type,
                description,
                "suggested",
                impact_score
            ))
            conn.commit()
        
        return improvement_id
    
    def _generate_memory_id(self, agent_type: str, stock_symbol: str, content: Dict[str, Any]) -> str:
        """Generate a unique memory ID"""
        content_hash = hashlib.md5(json.dumps(content, sort_keys=True).encode()).hexdigest()[:8]
        timestamp = int(datetime.now().timestamp())
        return f"{agent_type}_{stock_symbol}_{timestamp}_{content_hash}"
    
    async def cleanup_old_memories(self, days: int = 90):
        """Clean up old memories to prevent database bloat"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.sqlite_store.db_path) as conn:
            # Keep important memories longer
            conn.execute("""
                DELETE FROM memories 
                WHERE created_at < ? AND importance_score < 0.7
            """, (cutoff_time.isoformat(),))
            conn.commit()
        
        print(f"Cleaned up memories older than {days} days")

# Example usage and testing
async def main():
    memory_manager = AgentMemoryManager()
    
    # Store a learning experience
    learning = {
        "lesson": "AAPL earnings analysis improved when focusing on services revenue",
        "context": "Q3 2024 earnings analysis",
        "improvement": "Added services revenue growth analysis",
        "outcome": "Better prediction accuracy"
    }
    
    memory_id = await memory_manager.store_learning(
        agent_type="investment_research_agent",
        stock_symbol="AAPL",
        learning_content=learning,
        performance_score=0.85,
        importance=0.9
    )
    
    print(f"Stored learning with ID: {memory_id}")
    
    # Retrieve relevant memories
    relevant = await memory_manager.get_relevant_memories(
        "AAPL earnings analysis services revenue",
        agent_type="investment_research_agent",
        limit=5
    )
    
    print(f"Found {len(relevant)} relevant memories")
    for memory in relevant:
        print(f"- {memory['id']}: {memory['content']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())