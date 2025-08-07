# Technical Specification for MCPIndexAgent Implementation

*Generated on August 07, 2025, at 10:26 AM EDT*

## 1. Overview

The `MCPIndexAgent` is an autonomous component in the AI-based code analyzer and modernization application, responsible for creating and managing vector database indexes for metadata and code embeddings. It enables efficient similarity searches and supports AI-driven analysis (e.g., code smell detection, refactoring suggestions). The agent operates within an agentic architecture coordinated by the `MCPOrchestratorAgent` using Multi-Agent Constraint Programming (MCP). It is designed to be **database-agnostic**, supporting both cloud-based (e.g., Qdrant, Pinecone) and on-premises (e.g., Milvus, Weaviate) vector databases, with configuration-driven selection for flexibility in deployment.

### 1.1 Responsibilities
- **Index Creation**: Create vector database indexes for metadata (e.g., ASTs, metrics, dependencies) and code embeddings.
- **Embedding Generation**: Generate vector embeddings for code and metadata using a model like `sentence-transformers`.
- **Index Management**: Update or delete indexes as needed for incremental updates or repository changes.
- **Constraint Compliance**: Adhere to MCP constraints (e.g., resource limits, indexing deadlines).
- **Event Publishing**: Notify downstream agents (e.g., `CodeSmellAgent`) via a message bus (e.g., Kafka).
- **Error Handling**: Manage indexing errors, logging issues for compliance and debugging.

### 1.2 Constraints
- **Resource Constraints**:
  - Maximum 4GB RAM per indexing task.
  - Maximum 2 CPU cores per task.
- **Temporal Constraints**:
  - Index metadata for 100K lines of code within 60 seconds (MVP target).
- **Dependency Constraints**:
  - Requires metadata from `MetadataExtractorAgent` via `MetadataExtracted` event.
  - Must complete before AI analysis by `CodeSmellAgent` (Phase 3).
- **Security Constraints**:
  - Ensure no sensitive data (e.g., credentials) is included in embeddings.
  - Log all indexing events for compliance auditing.

### 1.3 Integration Points
- **Input**: Receives metadata from `MetadataExtractorAgent` via `MetadataExtracted` event.
- **Output**: Produces index metadata as an `IndexCreated` event.
- **Coordination**: Interacts with `MCPOrchestratorAgent` for task assignment and constraint enforcement.
- **Storage**: Stores vector indexes in a configured vector database (cloud or on-premises) via `StorageAgent`.
- **Database Agnosticism**: Uses an abstract interface to support multiple vector databases, configured via environment variables.

## 2. Data Schema

The `MCPIndexAgent` uses schemas for input, output, and storage, extending the BRD’s schema for vector index management.

### 2.1 Input Schema
Received via the `MetadataExtracted` event:
```json
{
  "event_id": "UUID",
  "file_id": "UUID",
  "repository_id": "UUID",
  "metadata": {
    "language": "string",
    "metrics": {
      "lines_of_code": "integer",
      "cyclomatic_complexity": "integer",
      "comment_ratio": "float"
    },
    "dependencies": ["string"]
  },
  "constraints": {
    "resource_limit": { "cpu": "integer", "memory": "string" },
    "deadline": "timestamp",
    "priority": "enum(high, medium, low)"
  }
}
```

### 2.2 Output Schema
Published as the `IndexCreated` event:
```json
{
  "event_id": "UUID",
  "file_id": "UUID",
  "repository_id": "UUID",
  "index_id": "string",
  "vector_db": "string", // e.g., "qdrant", "milvus"
  "index_metadata": {
    "collection_name": "string",
    "vector_dimension": "integer",
    "record_count": "integer"
  },
  "constraints_satisfied": "boolean",
  "constraint_violations": ["string"],
  "error_message": "string | null",
  "timestamp": "timestamp"
}
```

### 2.3 Storage Schema
Stored via `StorageAgent` in the vector database:
```json
{
  "index_id": "string",
  "file_id": "UUID",
  "repository_id": "UUID",
  "vector_db": "string",
  "collection_name": "string",
  "vector": ["float"], // Embedding vector
  "metadata": {
    "language": "string",
    "metrics": {
      "lines_of_code": "integer",
      "cyclomatic_complexity": "integer",
      "comment_ratio": "float"
    },
    "dependencies": ["string"]
  },
  "created_at": "timestamp",
  "constraints_satisfied": "boolean",
  "constraint_violations": ["string"]
}
```

## 3. Endpoints

The `MCPIndexAgent` exposes internal endpoints for communication via Kafka topics.

### 3.1 Create Index
- **Topic**: `index.create`
- **Request**:
  ```typescript
  interface CreateIndexRequest {
    event_id: string;
    file_id: string;
    repository_id: string;
    metadata: {
      language: string;
      metrics: {
        lines_of_code: number;
        cyclomatic_complexity: number;
        comment_ratio: number;
      };
      dependencies: string[];
    };
    constraints: {
      resource_limit?: { cpu: number; memory: string };
      deadline?: string;
      priority: "high" | "medium" | "low";
    };
  }
  ```
- **Response** (Published to `index.result`):
  ```typescript
  interface CreateIndexResponse {
    event_id: string;
    file_id: string;
    repository_id: string;
    index_id: string;
    vector_db: string;
    index_metadata: {
      collection_name: string;
      vector_dimension: number;
      record_count: number;
    };
    constraints_satisfied: boolean;
    constraint_violations?: string[];
    error_message?: string;
    timestamp: string;
  }
  ```

### 3.2 Health Check
- **Topic**: `index.health`
- **Request**:
  ```typescript
  interface HealthCheckRequest {
    agent_id: string;
  }
  ```
- **Response**:
  ```typescript
  interface HealthCheckResponse {
    agent_id: string;
    status: "healthy" | "unhealthy";
    resource_usage: { cpu: number; memory: string };
    active_tasks: number;
  }
  ```

## 4. Mini Component Diagram

The following diagram highlights the `MCPIndexAgent`’s interactions within the system, focusing on its role in the agentic architecture.

```mermaid
classDiagram
    subgraph CoreAgents
        MCPIndexAgent
        MCPOrchestratorAgent
        MetadataExtractorAgent
        StorageAgent
        CodeSmellAgent
    end

    class MCPIndexAgent {
        +createIndex()
        +generateEmbeddings()
    }
    class MCPOrchestratorAgent {
        +solveConstraints()
        +coordinateAgents()
    }
    class MetadataExtractorAgent {
        +extractMetadata()
        +computeMetrics()
    }
    class StorageAgent {
        +storeData()
        +redactSensitiveData()
    }
    class CodeSmellAgent {
        +detectCodeSmells()
    }

    MCPOrchestratorAgent --> MCPIndexAgent : Coordinates
    MetadataExtractorAgent --> MCPIndexAgent : Sends MetadataExtracted
    MCPIndexAgent --> CodeSmellAgent : Sends IndexCreated (Phase 3)
    MCPIndexAgent --> StorageAgent : Stores Index
    StorageAgent --> VectorDB : Stores
    MCPIndexAgent --> Kafka : Publishes to

    note for CodeSmellAgent "Phase 3"
    note for VectorDB "Cloud or On-Premises"
```

**Diagram Explanation**:
- **Grouping**: Agents are grouped in a `CoreAgents` subgraph for brevity.
- **Focus**: Emphasizes `MCPIndexAgent`’s interactions:
  - Receives `MetadataExtracted` from `MetadataExtractorAgent`.
  - Publishes `IndexCreated` to `CodeSmellAgent` (Phase 3).
  - Stores indexes via `StorageAgent`.
  - Coordinated by `MCPOrchestratorAgent`.
- **External Systems**: Shows a generic `VectorDB` (cloud or on-premises) and Kafka.
- **Phase Annotation**: Notes `CodeSmellAgent` as Phase 3 and `VectorDB` flexibility.

## 5. Python Implementation

The `MCPIndexAgent` is implemented in Python, using `sentence-transformers` for embeddings and an abstract vector database interface to support multiple databases (e.g., Qdrant, Milvus). It runs as a worker process, consuming Kafka messages.

### 5.1 Dependencies
```bash
pip install kafka-python sentence-transformers qdrant-client milvus-client psutil
```

### 5.2 Core Implementation
```python
import json
import time
import uuid
from kafka import KafkaConsumer, KafkaProducer
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from pymilvus import connections, Collection
import psutil
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from abc import ABC, abstractmethod

class VectorDBInterface(ABC):
    """Abstract interface for vector databases."""
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, dimension: int):
        pass

    @abstractmethod
    def insert(self, collection_name: str, vectors: List[List[float]], metadata: List[Dict]):
        pass

class QdrantDB(VectorDBInterface):
    def __init__(self, host: str, port: int):
        self.client = None
        self.host = host
        self.port = port

    def connect(self):
        self.client = QdrantClient(host=self.host, port=self.port)

    def create_collection(self, collection_name: str, dimension: int):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={"size": dimension, "distance": "Cosine"}
        )

    def insert(self, collection_name: str, vectors: List[List[float]], metadata: List[Dict]):
        self.client.upsert(
            collection_name=collection_name,
            points=[
                {"id": str(uuid.uuid4()), "vector": vector, "payload": meta}
                for vector, meta in zip(vectors, metadata)
            ]
        )

class MilvusDB(VectorDBInterface):
    def __init__(self, host: str, port: int):
        self.collection = None
        self.host = host
        self.port = port

    def connect(self):
        connections.connect(host=self.host, port=self.port)

    def create_collection(self, collection_name: str, dimension: int):
        from pymilvus import CollectionSchema, FieldSchema, DataType
        fields = [
            FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema("vector", DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema("metadata", DataType.JSON)
        ]
        schema = CollectionSchema(fields, description="Code metadata index")
        self.collection = Collection(collection_name, schema)
        self.collection.create_index("vector", {"index_type": "IVF_FLAT", "metric_type": "COSINE"})

    def insert(self, collection_name: str, vectors: List[List[float]], metadata: List[Dict]):
        self.collection.load()
        self.collection.insert([
            [str(uuid.uuid4()) for _ in vectors],  # IDs
            vectors,                               # Vectors
            metadata                               # Metadata
        ])

class MCPIndexAgent:
    def __init__(self, kafka_bootstrap_servers: str, db_config: Dict):
        self.producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
        self.consumer = KafkaConsumer(
            'index.create',
            bootstrap_servers=kafka_bootstrap_servers,
            group_id='index_agent_group'
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_db = self._init_vector_db(db_config)

    def _init_vector_db(self, db_config: Dict) -> VectorDBInterface:
        """Initialize vector database based on configuration."""
        db_type = db_config['type']
        host = db_config['host']
        port = db_config['port']
        if db_type == 'qdrant':
            db = QdrantDB(host, port)
        elif db_type == 'milvus':
            db = MilvusDB(host, port)
        else:
            raise ValueError(f"Unsupported vector DB: {db_type}")
        db.connect()
        return db

    def generate_embedding(self, metadata: Dict) -> List[float]:
        """Generate vector embedding for metadata."""
        # Serialize metadata to text for embedding
        text = json.dumps(metadata)
        return self.embedding_model.encode(text).tolist()

    def check_constraints(self, constraints: Dict, start_time: float) -> tuple[bool, List[str]]:
        """Validate MCP constraints."""
        violations = []
        satisfied = True

        # Resource constraints
        process = psutil.Process()
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)
        if constraints.get('resource_limit'):
            if memory_info.rss > int(constraints['resource_limit']['memory'].replace('GB', '')) * 1e9:
                violations.append("Memory limit exceeded")
                satisfied = False
            if cpu_percent / psutil.cpu_count() > constraints['resource_limit']['cpu'] * 100:
                violations.append("CPU limit exceeded")
                satisfied = False

        # Temporal constraints
        if constraints.get('deadline'):
            deadline = datetime.fromisoformat(constraints['deadline'])
            if datetime.now() > deadline:
                violations.append("Deadline exceeded")
                satisfied = False

        return satisfied, violations

    def process_metadata(self, message: Dict):
        """Process metadata and create vector index."""
        event_id = str(uuid.uuid4())
        file_id = message['file_id']
        repository_id = message['repository_id']
        metadata = message['metadata']
        constraints = message.get('constraints', {})
        collection_name = f"repo_{repository_id}"

        start_time = time.time()
        try:
            # Generate embedding
            vector = self.generate_embedding(metadata)

            # Create collection if it doesn't exist
            vector_dimension = len(vector)
            self.vector_db.create_collection(collection_name, vector_dimension)

            # Insert vector and metadata
            self.vector_db.insert(collection_name, [vector], [metadata])

            # Check constraints
            constraints_satisfied, constraint_violations = self.check_constraints(constraints, start_time)

            # Prepare response
            response = {
                'event_id': event_id,
                'file_id': file_id,
                'repository_id': repository_id,
                'index_id': str(uuid.uuid4()),
                'vector_db': message.get('vector_db', 'qdrant'),
                'index_metadata': {
                    'collection_name': collection_name,
                    'vector_dimension': vector_dimension,
                    'record_count': 1
                },
                'constraints_satisfied': constraints_satisfied,
                'constraint_violations': constraint_violations,
                'error_message': None,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            response = {
                'event_id': event_id,
                'file_id': file_id,
                'repository_id': repository_id,
                'index_id': None,
                'vector_db': message.get('vector_db', 'qdrant'),
                'index_metadata': None,
                'constraints_satisfied': False,
                'constraint_violations': ["Indexing error"],
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

        # Publish result
        self.producer.send('index.result', json.dumps(response).encode('utf-8'))

    def run(self):
        """Main loop to consume and process messages."""
        for message in self.consumer:
            try:
                msg = json.loads(message.value.decode('utf-8'))
                self.process_metadata(msg)
            except Exception as e:
                print(f"Error processing message: {str(e)}")

    def health_check(self, agent_id: str) -> Dict:
        """Return health status and resource usage."""
        process = psutil.Process()
        return {
            'agent_id': agent_id,
            'status': 'healthy',
            'resource_usage': {
                'cpu': process.cpu_percent(interval=0.1) / psutil.cpu_count(),
                'memory': f"{process.memory_info().rss / 1e9}GB"
            },
            'active_tasks': len(self.consumer.assignment())
        }
```

### 5.3 Configuration
- **Kafka Topics**:
  - Subscribe to: `index.create`
  - Publish to: `index.result`, `index.health`
- **Environment Variables**:
  - `KAFKA_BOOTSTRAP_SERVERS`: Kafka server address (e.g., `localhost:9092`).
  - `VECTOR_DB_TYPE`: Database type (e.g., `qdrant`, `milvus`).
  - `VECTOR_DB_HOST`: Database host (e.g., `localhost` for on-premises, cloud endpoint for Qdrant).
  - `VECTOR_DB_PORT`: Database port (e.g., `6333` for Qdrant, `19530` for Milvus).
- **Constraints Example**:
  ```json
  {
    "resource_limit": { "cpu": 2, "memory": "4GB" },
    "deadline": "2025-08-07T10:30:00Z",
    "priority": "medium"
  }
  ```

## 6. Error Handling and Logging
- **Error Handling**:
  - Catch indexing exceptions and include in `error_message`.
  - Validate constraints and report violations in `constraint_violations`.
  - Retry transient failures (e.g., vector DB connection errors) up to 3 times.
- **Logging**:
  - Log events to `AuditLog` via `ComplianceAgent`:
    ```json
    {
      "event_id": "UUID",
      "type": "index_create",
      "timestamp": "timestamp",
      "user_id": "UUID",
      "details": "Created index for file {file_id}",
      "compliance_status": "compliant",
      "constraint_violations": []
    }
    ```
  - Use Python’s `logging` module:
    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('MCPIndexAgent')
    ```

## 7. MCP Integration
The `MCPIndexAgent` integrates with MCP via the `check_constraints` method, ensuring compliance with resource, temporal, and dependency constraints. The `MCPOrchestratorAgent` assigns tasks using a constraint satisfaction problem (CSP) solved with Google OR-Tools.

- **CSP Model**:
  - **Variables**: Indexing tasks (e.g., index metadata for file X).
  - **Domains**: Available `MCPIndexAgent` instances.
  - **Constraints**:
    - Resource: CPU ≤ 2 cores, memory ≤ 4GB.
    - Temporal: Complete within deadline.
    - Dependency: Wait for `MetadataExtracted` event.
  - **Solver**: OR-Tools for optimal task assignment.

## 8. Testing and Validation
### 8.1 Unit Tests
```python
import unittest
from unittest.mock import MagicMock

class TestMCPIndexAgent(unittest.TestCase):
    def setUp(self):
        self.db_config = {'type': 'qdrant', 'host': 'localhost', 'port': 6333}
        self.agent = MCPIndexAgent(kafka_bootstrap_servers='localhost:9092', db_config=self.db_config)
        self.agent.vector_db = MagicMock()

    def test_generate_embedding(self):
        metadata = {'language': 'Python', 'metrics': {'lines_of_code': 100}}
        vector = self.agent.generate_embedding(metadata)
        self.assertEqual(len(vector), 384)  # Default dimension for all-MiniLM-L6-v2

    def test_check_constraints(self):
        constraints = {
            'resource_limit': {'cpu': 1, 'memory': '1GB'},
            'deadline': (datetime.now() - timedelta(seconds=1)).isoformat()
        }
        satisfied, violations = self.agent.check_constraints(constraints, time.time())
        self.assertFalse(satisfied)
        self.assertIn('Deadline exceeded', violations)

    def test_process_metadata(self):
        message = {
            'event_id': str(uuid.uuid4()),
            'file_id': str(uuid.uuid4()),
            'repository_id': str(uuid.uuid4()),
            'metadata': {'language': 'Python', 'metrics': {'lines_of_code': 100}},
            'constraints': {}
        }
        self.agent.process_metadata(message)
        self.assertTrue(self.agent.vector_db.insert.called)

if __name__ == '__main__':
    unittest.main()
```

### 8.2 Success Criteria
- Index metadata for 100K lines in <60 seconds.
- 99% accuracy in embedding generation.
- 100% constraint satisfaction for hard constraints.
- Zero sensitive data in vector indexes.

## 9. Deployment
- **Environment**: Docker container with Kubernetes for scaling.
- **Configuration**:
  - Image: Python 3.9 with required libraries.
  - Resources: 4GB RAM, 2 CPU cores per instance.
  - Scaling: Minimum 2 instances, auto-scale based on Kafka topic backlog.
- **Monitoring**:
  - Expose health check endpoint for Kubernetes liveness probes.
  - Monitor CPU/memory via Prometheus.

## 10. Future Enhancements
- **Phase 2**: Support additional vector databases (e.g., Pinecone, Weaviate).
- **Phase 3**: Integrate with `CodeSmellAgent` for similarity-based code smell detection.
- **Phase 4**: Support multi-tenant indexing with tenant-specific collections.

## 11. Conclusion
The `MCPIndexAgent` enables efficient vector database indexing for code and metadata, supporting both cloud and on-premises deployments. Its database-agnostic design, Python implementation, and MCP integration ensure scalability and constraint compliance. The schemas, endpoints, and mini component diagram provide a robust foundation for the MVP, with extensibility for future phases.