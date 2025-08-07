# Technical Specification for ParserAgent Implementation

*Generated on August 07, 2025, at 10:09 AM EDT*

## 1. Overview

The `ParserAgent` is an autonomous component in the AI-based code analyzer and modernization application, responsible for parsing source code files, generating Abstract Syntax Trees (ASTs), and performing initial language detection. It operates within an agentic architecture coordinated by the `MCPOrchestratorAgent` using Multi-Agent Constraint Programming (MCP). The agent processes files fetched by the `VCSConnectorAgent`, produces structured outputs for the `MetadataExtractorAgent`, and stores results via the `StorageAgent`.

### 1.1 Responsibilities
- **Language Detection**: Identify the programming language of each file (e.g., Python, JavaScript/TypeScript, Java, C++).
- **AST Generation**: Parse source code to produce an AST in a standardized JSON format.
- **Constraint Compliance**: Adhere to MCP constraints (e.g., resource limits, parsing deadlines).
- **Event Publishing**: Notify other agents (e.g., `MetadataExtractorAgent`) upon completion via a message bus (e.g., Kafka).
- **Error Handling**: Manage parsing errors gracefully, logging issues and reporting to the orchestrator.

### 1.2 Constraints
- **Resource Constraints**:
  - Maximum 4GB RAM per parsing task.
  - Maximum 2 CPU cores per task.
- **Temporal Constraints**:
  - Parse 100K lines of code within 60 seconds (MVP target).
- **Dependency Constraints**:
  - Requires file content from `VCSConnectorAgent`.
  - Must complete before `MetadataExtractorAgent` processes metadata.
- **Security Constraints**:
  - Ensure no sensitive data (e.g., credentials) is included in ASTs.
  - Log parsing events for compliance auditing.

### 1.3 Integration Points
- **Input**: Receives file paths and content from `VCSConnectorAgent` via a `CodeFetched` event.
- **Output**: Produces an AST and language metadata, published as an `ASTGenerated` event.
- **Coordination**: Interacts with `MCPOrchestratorAgent` for task assignment and constraint enforcement.
- **Storage**: Sends parsed data to `StorageAgent` for persistence in MongoDB.

### 1.4 Component diagram
```mermaid
classDiagram
    %% Group core agents in a single subgraph
    subgraph CoreAgents
        ParserAgent
        MCPOrchestratorAgent
        VCSConnectorAgent
        MetadataExtractorAgent
        StorageAgent
    end

    %% Agent Definitions
    class ParserAgent {
        +parseCode()
        +generateAST()
    }
    class MCPOrchestratorAgent {
        +solveConstraints()
        +coordinateAgents()
    }
    class VCSConnectorAgent {
        +fetchCode()
        +publishCodeFetched()
    }
    class MetadataExtractorAgent {
        +extractMetadata()
        +computeMetrics()
    }
    class StorageAgent {
        +storeData()
        +redactSensitiveData()
    }

    %% Relationships
    MCPOrchestratorAgent --> ParserAgent : Coordinates
    VCSConnectorAgent --> ParserAgent : Sends CodeFetched
    ParserAgent --> MetadataExtractorAgent : Sends ASTGenerated
    ParserAgent --> StorageAgent : Stores AST
    VCSConnectorAgent --> GitHub : Connects
    VCSConnectorAgent --> GitLab : Connects
    VCSConnectorAgent --> Bitbucket : Connects (Phase 2)
    StorageAgent --> MongoDB : Stores
    StorageAgent --> S3 : Stores
    ParserAgent --> Kafka : Publishes to

    %% Phase Annotations
    note for Bitbucket "Phase 2"
  ```

## 2. Data Schema

The `ParserAgent` uses the following schemas for input, output, and storage, extending the BRD’s schema to support parsing-specific data.

### 2.1 Input Schema
Received via the `CodeFetched` event:
```json
{
  "event_id": "UUID",
  "file_id": "UUID",
  "repository_id": "UUID",
  "file_path": "string",
  "content_ref": "string", // Reference to raw content in S3
  "hash": "string", // SHA-256 hash for versioning
  "constraints": {
    "resource_limit": { "cpu": "integer", "memory": "string" },
    "deadline": "timestamp",
    "priority": "enum(high, medium, low)"
  }
}
```

### 2.2 Output Schema
Published as the `ASTGenerated` event:
```json
{
  "event_id": "UUID",
  "file_id": "UUID",
  "repository_id": "UUID",
  "language": "string", // e.g., "Python", "JavaScript"
  "ast": "json", // Standardized AST in JSON format
  "constraints_satisfied": "boolean",
  "constraint_violations": ["string"],
  "error_message": "string | null",
  "timestamp": "timestamp"
}
```

### 2.3 Storage Schema
Stored via `StorageAgent` in MongoDB:
```json
{
  "metadata_id": "UUID",
  "file_id": "UUID",
  "language": "string",
  "ast": "json",
  "created_at": "timestamp",
  "constraints_satisfied": "boolean",
  "constraint_violations": ["string"]
}
```

## 3. Endpoints

The `ParserAgent` exposes internal endpoints for communication within the agentic system, using a REST-like interface over a message bus (e.g., Kafka topics). These are not external APIs but internal message handlers.

### 3.1 Process File
- **Topic**: `parser.process`
- **Request**:
  ```typescript
  interface ProcessFileRequest {
    event_id: string;
    file_id: string;
    repository_id: string;
    file_path: string;
    content_ref: string;
    hash: string;
    constraints: {
      resource_limit?: { cpu: number; memory: string };
      deadline?: string;
      priority: "high" | "medium" | "low";
    };
  }
  ```
- **Response** (Published to `parser.result`):
  ```typescript
  interface ProcessFileResponse {
    event_id: string;
    file_id: string;
    repository_id: string;
    language: string;
    ast: object;
    constraints_satisfied: boolean;
    constraint_violations?: string[];
    error_message?: string;
    timestamp: string;
  }
  ```

### 3.2 Health Check
- **Topic**: `parser.health`
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

## 4. Python Implementation

The `ParserAgent` is implemented in Python, using libraries like `astroid` (Python), `esprima` (JavaScript/TypeScript via Pyodide), and `javalang` (Java). It runs as a worker process, consuming messages from a Kafka topic and publishing results.

### 4.1 Dependencies
```bash
pip install kafka-python astroid esprima javalang psutil python-magic
```

### 4.2 Core Implementation
```python
import json
import time
import uuid
import magic
from kafka import KafkaConsumer, KafkaProducer
from astroid import parse as python_parse
import esprima
import javalang
import psutil
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class ParserAgent:
    def __init__(self, kafka_bootstrap_servers: str, s3_client):
        self.producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
        self.consumer = KafkaConsumer(
            'parser.process',
            bootstrap_servers=kafka_bootstrap_servers,
            group_id='parser_agent_group'
        )
        self.s3_client = s3_client
        self.supported_languages = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java'
        }

    def detect_language(self, file_path: str, content: str) -> str:
        """Detect the programming language of a file."""
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(content.encode('utf-8'))
        extension = file_path.lower().split('.')[-1]
        if extension in self.supported_languages:
            return self.supported_languages[extension]
        raise ValueError(f"Unsupported file type: {mime_type}")

    def parse_code(self, language: str, content: str) -> Dict:
        """Parse code and generate AST."""
        try:
            if language == 'Python':
                ast = python_parse(content)
                return ast.as_string()  # Convert to JSON-compatible format
            elif language in ['JavaScript', 'TypeScript']:
                ast = esprima.parseScript(content, {'jsx': True})
                return json.loads(json.dumps(ast.toDict()))
            elif language == 'Java':
                ast = javalang.parse.parse(content)
                return json.loads(json.dumps(ast.to_dict()))  # Custom to_dict method
            else:
                raise ValueError(f"Unsupported language: {language}")
        except Exception as e:
            raise ValueError(f"Parsing failed: {str(e)}")

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

    def process_file(self, message: Dict):
        """Process a file and publish results."""
        event_id = str(uuid.uuid4())
        file_id = message['file_id']
        repository_id = message['repository_id']
        file_path = message['file_path']
        content_ref = message['content_ref']
        constraints = message.get('constraints', {})

        start_time = time.time()
        try:
            # Fetch content from S3
            content = self.s3_client.get_object(Bucket='code-storage', Key=content_ref)['Body'].read().decode('utf-8')

            # Detect language
            language = self.detect_language(file_path, content)

            # Parse code
            ast = self.parse_code(language, content)

            # Check constraints
            constraints_satisfied, constraint_violations = self.check_constraints(constraints, start_time)

            # Prepare response
            response = {
                'event_id': event_id,
                'file_id': file_id,
                'repository_id': repository_id,
                'language': language,
                'ast': ast,
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
                'language': None,
                'ast': None,
                'constraints_satisfied': False,
                'constraint_violations': ["Parsing error"],
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

        # Publish result
        self.producer.send('parser.result', json.dumps(response).encode('utf-8'))

    def run(self):
        """Main loop to consume and process messages."""
        for message in self.consumer:
            try:
                msg = json.loads(message.value.decode('utf-8'))
                self.process_file(msg)
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

### 4.3 Configuration
- **Kafka Topics**:
  - Subscribe to: `parser.process`
  - Publish to: `parser.result`, `parser.health`
- **Environment Variables**:
  - `KAFKA_BOOTSTRAP_SERVERS`: Kafka server address (e.g., `localhost:9092`).
  - `S3_BUCKET`: S3 bucket name for raw code storage.
- **Constraints Example**:
  ```json
  {
    "resource_limit": { "cpu": 2, "memory": "4GB" },
    "deadline": "2025-08-07T10:15:00Z",
    "priority": "high"
  }
  ```

## 5. Error Handling and Logging
- **Error Handling**:
  - Catch parsing exceptions and include in `error_message`.
  - Validate constraints and report violations in `constraint_violations`.
  - Retry transient failures (e.g., S3 access errors) up to 3 times.
- **Logging**:
  - Log all events to `AuditLog` via `ComplianceAgent`:
    ```json
    {
      "event_id": "UUID",
      "type": "parser_process",
      "timestamp": "timestamp",
      "user_id": "UUID",
      "details": "Parsed file {file_id}",
      "compliance_status": "compliant",
      "constraint_violations": []
    }
    ```
  - Use Python’s `logging` module for debugging:
    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('ParserAgent')
    ```

## 6. MCP Integration
The `ParserAgent` integrates with MCP via the `check_constraints` method, ensuring compliance with resource, temporal, and dependency constraints. The `MCPOrchestratorAgent` assigns tasks based on a constraint satisfaction problem (CSP) solved using a library like Google OR-Tools.

- **CSP Model**:
  - **Variables**: Parsing tasks (e.g., parse file X).
  - **Domains**: Available `ParserAgent` instances.
  - **Constraints**:
    - Resource: CPU ≤ 2 cores, memory ≤ 4GB.
    - Temporal: Complete within deadline.
    - Dependency: Wait for `CodeFetched` event.
  - **Solver**: Use OR-Tools to assign tasks optimally.

## 7. Testing and Validation
### 7.1 Unit Tests
```python
import unittest
from unittest.mock import MagicMock

class TestParserAgent(unittest.TestCase):
    def setUp(self):
        self.s3_client = MagicMock()
        self.agent = ParserAgent(kafka_bootstrap_servers='localhost:9092', s3_client=self.s3_client)

    def test_detect_language_python(self):
        file_path = 'test.py'
        content = 'def hello(): pass'
        self.assertEqual(self.agent.detect_language(file_path, content), 'Python')

    def test_parse_python(self):
        content = 'def hello(): pass'
        ast = self.agent.parse_code('Python', content)
        self.assertIsInstance(ast, str)

    def test_constraints_violation(self):
        constraints = {
            'resource_limit': {'cpu': 1, 'memory': '1GB'},
            'deadline': (datetime.now() - timedelta(seconds=1)).isoformat()
        }
        satisfied, violations = self.agent.check_constraints(constraints, time.time())
        self.assertFalse(satisfied)
        self.assertIn('Deadline exceeded', violations)

if __name__ == '__main__':
    unittest.main()
```

### 7.2 Success Criteria
- Parse 100K lines in <60 seconds.
- 99% accuracy in language detection.
- 100% constraint satisfaction for hard constraints.
- Zero data leaks in AST output.

## 8. Deployment
- **Environment**: Docker container with Kubernetes for scaling.
- **Configuration**:
  - Image: Python 3.9 with required libraries.
  - Resources: 4GB RAM, 2 CPU cores per instance.
  - Scaling: Minimum 2 instances, auto-scale based on Kafka topic backlog.
- **Monitoring**:
  - Expose health check endpoint for Kubernetes liveness probes.
  - Monitor CPU/memory usage via Prometheus.

## 9. Future Enhancements
- **Phase 2**: Add support for Java and C++ parsing using `javalang` and `libclang`.
- **Phase 3**: Integrate with `CodeSmellAgent` for inline code smell detection during parsing.
- **Phase 4**: Support custom parser plugins for niche languages.

## 10. Conclusion
The `ParserAgent` is a critical component of the code analyzer, providing robust parsing and language detection within the agentic, MCP-driven architecture. Its implementation ensures scalability, constraint compliance, and seamless integration with other agents. The provided schemas, endpoints, and Python code form a solid foundation for the MVP, with extensibility for future phases.