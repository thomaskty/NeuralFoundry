#!/usr/bin/env python3
"""
Populate database with realistic test data for RAG testing.
Creates users, KBs, documents with tricky content, and chat conversations.
"""
import requests
import time
from typing import List, Dict

BASE_URL = "http://localhost:8000/api/v1"


# ANSI color codes
class Color:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_step(text: str):
    print(f"{Color.BOLD}{Color.BLUE}▶ {text}{Color.RESET}")


def print_success(text: str):
    print(f"{Color.GREEN}✅ {text}{Color.RESET}")


def print_info(text: str):
    print(f"{Color.CYAN}ℹ️  {text}{Color.RESET}")


# ============================================================================
# TEST DOCUMENTS - Tricky content to test RAG understanding
# ============================================================================

DOCUMENTS = {
    "fastapi_advanced.txt": """
FastAPI Advanced Concepts - Internal Documentation

Authentication in FastAPI:
FastAPI uses OAuth2 with Password (and hashing), JWT tokens for authentication.
The recommended approach is to use OAuth2PasswordBearer for token-based auth.
Password hashing should be done using bcrypt or passlib.
IMPORTANT: Never store passwords in plain text. Always hash with bcrypt.

Middleware Configuration:
FastAPI supports ASGI middleware. Common middleware includes:
- CORSMiddleware: For handling Cross-Origin Resource Sharing
- TrustedHostMiddleware: For validating Host headers
- GZipMiddleware: For compressing responses
Note: Middleware order matters! CORS should be added first.

Database Connection Pooling:
For production, use connection pooling with asyncpg or databases library.
Recommended pool size: min=10, max=50 for moderate traffic.
Always use async database drivers (asyncpg, aiomysql, motor).

Performance Tips:
1. Use async/await for I/O operations
2. Enable response caching for read-heavy endpoints
3. Use background tasks for non-critical operations
4. Implement rate limiting to prevent abuse
5. Use Redis for session management and caching

Common Pitfall: Blocking operations in async functions will kill performance.
Solution: Use run_in_executor for CPU-bound tasks.
""",

    "python_antipatterns.txt": """
Python Anti-Patterns and Common Mistakes

Mutable Default Arguments:
WRONG: def append_to(element, to=[]):
RIGHT: def append_to(element, to=None):
    if to is None:
        to = []
Explanation: Default mutable arguments are evaluated once at function definition,
not each time the function is called. This causes shared state bugs.

Exception Handling:
WRONG: except Exception: pass
RIGHT: except SpecificException as e: logger.error(f"Error: {e}")
Never use bare except clauses. Always catch specific exceptions.
Never silently ignore exceptions without logging.

Global Variables:
Avoid global variables. They make code hard to test and reason about.
If you must use them, use module-level constants in UPPER_CASE.
For shared state, use dependency injection or context managers.

String Concatenation in Loops:
WRONG: for item in items: result += item
RIGHT: result = "".join(items)
String concatenation in loops is O(n²) due to immutability.

Memory Leaks:
Common causes: circular references, unclosed file handles, global caches.
Solution: Use context managers (with statements), weak references, and proper cleanup.

The GIL (Global Interpreter Lock):
Python's GIL means only one thread executes Python bytecode at a time.
For CPU-bound tasks: use multiprocessing, not threading.
For I/O-bound tasks: threading or asyncio works fine.
""",

    "docker_best_practices.txt": """
Docker Best Practices for Production

Multi-stage Builds:
Always use multi-stage builds to reduce image size.
Example pattern:
FROM python:3.11 as builder
# Install dependencies
FROM python:3.11-slim
# Copy only necessary artifacts

Image Security:
1. Never run containers as root - use USER directive
2. Scan images for vulnerabilities with trivy or snyk
3. Use minimal base images (alpine, distroless)
4. Keep base images updated regularly
5. Don't include secrets in images - use Docker secrets or env vars

Layer Optimization:
Order Dockerfile commands from least to most frequently changing.
Correct order: base image → system packages → dependencies → app code
This maximizes cache utilization and speeds up builds.

Health Checks:
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
Always implement health checks for orchestration systems.

Resource Limits:
Set memory and CPU limits in docker-compose or Kubernetes.
Prevents one container from consuming all host resources.
Recommended: memory limit = 2x expected usage, CPU = 1-2 cores per service.

Volume Management:
Use named volumes for persistent data, not bind mounts in production.
Bind mounts are for development only.
Always backup volumes before upgrades.

Networking:
Use bridge networks for inter-container communication.
Never expose unnecessary ports to host.
Use Docker secrets for sensitive configuration.
""",

    "rag_system_design.txt": """
RAG System Design - Architecture Guide

Vector Database Selection:
Options: Pinecone, Weaviate, Qdrant, pgvector
For small-medium scale: pgvector (PostgreSQL extension) is sufficient
For large scale (>10M vectors): dedicated vector DB like Pinecone
Trade-off: Simplicity vs Performance vs Cost

Embedding Models:
Popular choices:
- sentence-transformers/all-MiniLM-L6-v2: 384 dims, fast, good quality
- text-embedding-ada-002 (OpenAI): 1536 dims, best quality, paid
- e5-small-v2: 384 dims, good balance
Dimension size affects: storage, search speed, accuracy

Chunking Strategy:
Fixed-size chunking: Simple but may break context
Semantic chunking: Better quality but slower
Recommended: 500-1000 tokens with 100-200 token overlap
Critical: Preserve paragraph/sentence boundaries

Retrieval Parameters:
top_k: Number of chunks to retrieve (typically 3-10)
similarity_threshold: Minimum cosine similarity (0.70-0.85)
Higher threshold = more precise but may miss relevant info
Lower threshold = more recall but may include noise

Context Window Management:
Total context = system prompt + retrieved chunks + chat history + user query
Must fit within LLM's context window (8K, 32K, 128K tokens)
Typical allocation: 30% system, 40% KB chunks, 20% chat history, 10% buffer

Re-ranking:
After initial retrieval, re-rank chunks using cross-encoder
Improves precision by 15-30% but adds latency
Only use for high-value queries or when precision is critical

Hybrid Search:
Combine vector search (semantic) with keyword search (BM25)
Vector search finds conceptually similar content
Keyword search finds exact term matches
Best results: weighted combination (0.7 vector + 0.3 keyword)

Caching Strategy:
Cache embeddings for common queries
Cache retrieval results for 5-15 minutes
Invalidate cache when documents are added/updated
Significantly reduces latency for repeat queries
""",

    "microservices_patterns.txt": """
Microservices Design Patterns

Service Discovery:
Pattern: Services register themselves in a service registry (Consul, Eureka)
Client-side discovery: Client queries registry and load balances
Server-side discovery: Router queries registry (e.g., Kubernetes service)
Trade-off: Client-side = less network hops, Server-side = simpler clients

Circuit Breaker:
Prevents cascading failures in distributed systems.
States: Closed (normal) → Open (failing) → Half-open (testing recovery)
Implementation: Use resilience4j, Hystrix, or custom with exponential backoff
When to use: Any service-to-service call that might fail

API Gateway:
Single entry point for all client requests
Responsibilities: routing, authentication, rate limiting, caching
Tools: Kong, Traefik, AWS API Gateway, Nginx
Anti-pattern: Don't make it a monolithic bottleneck

Saga Pattern:
Manages distributed transactions across services
Two types: Choreography (event-driven) vs Orchestration (centralized)
Compensating transactions handle rollbacks
When to use: Multi-service transactions that need atomicity

Event Sourcing:
Store all changes as sequence of events, not current state
Enables: audit trail, temporal queries, event replay
Challenges: increased complexity, eventual consistency
When to use: Finance, audit-heavy domains, complex business logic

CQRS (Command Query Responsibility Segregation):
Separate read and write models
Write model: optimized for updates, enforces business rules
Read model: optimized for queries, denormalized
When to use: Different read/write patterns, high read:write ratio

Strangler Fig Pattern:
Gradually replace legacy monolith with microservices
New features go to new services
Old features gradually migrated
When to use: Modernizing legacy systems without big-bang rewrite
"""
}

# ============================================================================
# CHAT CONVERSATIONS - Test chat history context
# ============================================================================

CONVERSATIONS = [
    {
        "title": "FastAPI Authentication Discussion",
        "messages": [
            {"role": "user", "content": "How should I implement authentication in FastAPI?"},
            {"role": "assistant",
             "content": "For FastAPI authentication, I recommend using OAuth2 with JWT tokens. Use OAuth2PasswordBearer for token-based auth and always hash passwords with bcrypt. Never store plain text passwords."},
            {"role": "user", "content": "What about middleware order?"},
            {"role": "assistant",
             "content": "Middleware order is crucial! CORS middleware should be added first, followed by authentication middleware, then other middleware. The order determines the execution sequence."},
            {"role": "user", "content": "Can you remind me about the password hashing?"},
        ]
    },
    {
        "title": "Python Performance Optimization",
        "messages": [
            {"role": "user", "content": "My Python string concatenation is slow. What's wrong?"},
            {"role": "assistant",
             "content": "String concatenation in loops is O(n²) because strings are immutable in Python. Use ''.join(items) instead for O(n) performance."},
            {"role": "user", "content": "What about the GIL? Should I use threading?"},
            {"role": "assistant",
             "content": "The GIL means only one thread executes Python bytecode at a time. For CPU-bound tasks, use multiprocessing. For I/O-bound tasks, threading or asyncio works fine."},
            {"role": "user", "content": "Tell me more about the string concatenation issue"},
        ]
    },
    {
        "title": "Docker Production Setup",
        "messages": [
            {"role": "user", "content": "What are the most important Docker security practices?"},
            {"role": "assistant",
             "content": "Key Docker security practices: 1) Never run as root, 2) Use minimal base images, 3) Scan for vulnerabilities, 4) Keep images updated, 5) Don't include secrets in images."},
            {"role": "user", "content": "Should I use bind mounts or volumes?"},
            {"role": "assistant",
             "content": "Use named volumes for production, not bind mounts. Bind mounts are for development only. Named volumes are more secure and portable."},
            {"role": "user", "content": "What about multi-stage builds?"},
        ]
    },
    {
        "title": "RAG System Architecture",
        "messages": [
            {"role": "user", "content": "Which vector database should I use for RAG?"},
            {"role": "assistant",
             "content": "For small-medium scale, pgvector is sufficient. For large scale (>10M vectors), use dedicated vector DBs like Pinecone or Qdrant. pgvector offers simplicity, while dedicated DBs offer better performance."},
            {"role": "user", "content": "What's a good chunking strategy?"},
            {"role": "assistant",
             "content": "Recommended chunking: 500-1000 tokens with 100-200 token overlap. Preserve paragraph boundaries. Semantic chunking gives better quality but is slower than fixed-size chunking."},
            {"role": "user", "content": "How do I allocate my context window?"},
        ]
    }
]

# ============================================================================
# TRICKY TEST QUESTIONS
# ============================================================================

TRICKY_QUESTIONS = [
    {
        "question": "What's the problem with using mutable default arguments in Python?",
        "expected_kb": "python_antipatterns.txt",
        "expected_terms": ["mutable", "default", "evaluated once", "shared state"]
    },
    {
        "question": "Should I use threading or multiprocessing for CPU-intensive tasks in Python?",
        "expected_kb": "python_antipatterns.txt",
        "expected_terms": ["GIL", "multiprocessing", "CPU-bound"]
    },
    {
        "question": "What's the correct order for adding middleware in FastAPI?",
        "expected_kb": "fastapi_advanced.txt",
        "expected_terms": ["CORS", "first", "order matters"]
    },
    {
        "question": "What's the recommended pool size for database connections in production?",
        "expected_kb": "fastapi_advanced.txt",
        "expected_terms": ["min=10", "max=50", "connection pooling"]
    },
    {
        "question": "Should I use bind mounts or named volumes in production Docker?",
        "expected_kb": "docker_best_practices.txt",
        "expected_terms": ["named volumes", "production", "bind mounts", "development"]
    },
    {
        "question": "How should I structure my Dockerfile for optimal caching?",
        "expected_kb": "docker_best_practices.txt",
        "expected_terms": ["least to most", "base image", "dependencies", "app code"]
    },
    {
        "question": "What's a good similarity threshold for RAG retrieval?",
        "expected_kb": "rag_system_design.txt",
        "expected_terms": ["0.70", "0.85", "threshold", "precision"]
    },
    {
        "question": "What's the difference between choreography and orchestration in Saga pattern?",
        "expected_kb": "microservices_patterns.txt",
        "expected_terms": ["event-driven", "centralized", "Saga"]
    },
    {
        "question": "When should I use CQRS pattern?",
        "expected_kb": "microservices_patterns.txt",
        "expected_terms": ["read", "write", "different", "separate models"]
    },
    {
        "question": "What's the recommended chunk size for RAG systems?",
        "expected_kb": "rag_system_design.txt",
        "expected_terms": ["500-1000", "tokens", "overlap", "100-200"]
    }
]


# ============================================================================
# MAIN POPULATION LOGIC
# ============================================================================

def create_user() -> str:
    """Create a test user"""
    print_step("Creating test user...")
    response = requests.post(
        f"{BASE_URL}/users",
        json={"username": "demo_user"}
    )
    if response.status_code == 201:
        user_id = response.json()["id"]
        print_success(f"User created: {user_id}")
        return user_id
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None


def create_kb_with_documents(user_id: str) -> str:
    """Create KB and upload all test documents"""
    print_step("Creating knowledge base...")
    response = requests.post(
        f"{BASE_URL}/users/{user_id}/knowledge-bases",
        json={
            "title": "Technical Documentation Hub",
            "description": "Comprehensive technical docs covering FastAPI, Python, Docker, RAG, and Microservices"
        }
    )

    if response.status_code != 201:
        print(f"❌ Failed to create KB: {response.text}")
        return None

    kb_id = response.json()["kb_id"]
    print_success(f"KB created: {kb_id}")

    # Upload all documents
    print_step(f"Uploading {len(DOCUMENTS)} documents...")
    for filename, content in DOCUMENTS.items():
        files = {"file": (filename, content, "text/plain")}
        response = requests.post(
            f"{BASE_URL}/knowledge-bases/{kb_id}/upload",
            files=files
        )
        if response.status_code == 202:
            print_success(f"✓ Uploaded: {filename}")
        else:
            print(f"❌ Failed to upload {filename}: {response.text}")

    print_info("Waiting 15 seconds for document processing...")
    for i in range(15):
        print(f"⏳ Processing... {i + 1}/15s", end='\r')
        time.sleep(1)
    print()
    print_success("Documents processed!")

    return kb_id


def create_chats_with_history(user_id: str, kb_id: str) -> List[str]:
    """Create multiple chats with conversation history"""
    print_step(f"Creating {len(CONVERSATIONS)} chats with conversation history...")

    chat_ids = []

    for conv in CONVERSATIONS:
        # Create chat
        response = requests.post(
            f"{BASE_URL}/users/{user_id}/chats",
            json={"title": conv["title"]}
        )

        if response.status_code != 201:
            print(f"❌ Failed to create chat: {response.text}")
            continue

        chat_id = response.json()["chat_id"]
        chat_ids.append(chat_id)
        print_success(f"✓ Chat created: {conv['title']}")

        # Attach KB
        requests.post(f"{BASE_URL}/chats/{chat_id}/knowledge-bases/{kb_id}")

        # Add conversation history (except last message which we'll use for testing)
        for msg in conv["messages"][:-1]:
            response = requests.post(
                f"{BASE_URL}/chats/{chat_id}/messages",
                json=msg
            )
            time.sleep(0.5)  # Small delay between messages

        print_info(f"  Added {len(conv['messages']) - 1} messages to chat history")

    return chat_ids


def save_test_scenarios(user_id: str, kb_id: str, chat_ids: List[str]):
    """Save test scenarios to a file for later use"""
    print_step("Saving test scenarios...")

    scenarios = {
        "user_id": user_id,
        "kb_id": kb_id,
        "chat_ids": chat_ids,
        "tricky_questions": TRICKY_QUESTIONS,
        "conversations": CONVERSATIONS
    }

    import json
    with open("test_scenarios.json", "w") as f:
        json.dump(scenarios, f, indent=2)

    print_success("Test scenarios saved to test_scenarios.json")


def print_summary(user_id: str, kb_id: str, chat_ids: List[str]):
    """Print summary and next steps"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}🎉 DATABASE POPULATED SUCCESSFULLY!{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}\n")

    print(f"{Color.BOLD}Created Resources:{Color.RESET}")
    print(f"  👤 User ID: {Color.YELLOW}{user_id}{Color.RESET}")
    print(f"  📚 KB ID: {Color.YELLOW}{kb_id}{Color.RESET}")
    print(f"  💬 Chats created: {Color.YELLOW}{len(chat_ids)}{Color.RESET}")
    print(f"  📄 Documents uploaded: {Color.YELLOW}{len(DOCUMENTS)}{Color.RESET}")

    print(f"\n{Color.BOLD}Test the System:{Color.RESET}")
    print(f"  1. Pick any chat ID from: {chat_ids[0][:8]}...")
    print(f"  2. Try these tricky questions:\n")

    for i, q in enumerate(TRICKY_QUESTIONS[:3], 1):
        print(f"     {i}. {Color.CYAN}{q['question']}{Color.RESET}")
        print(f"        Expected to use: {Color.YELLOW}{q['expected_kb']}{Color.RESET}\n")

    print(f"\n{Color.BOLD}Test Chat History:{Color.RESET}")
    print(f"  The last message in each chat is intentionally incomplete.")
    print(f"  Send it to test if the system uses conversation history!\n")

    for i, conv in enumerate(CONVERSATIONS[:2], 1):
        print(f"     {i}. Chat: {Color.CYAN}{conv['title']}{Color.RESET}")
        print(f"        Last message: {Color.YELLOW}{conv['messages'][-1]['content']}{Color.RESET}\n")

    print(f"{Color.BOLD}Quick Test Command:{Color.RESET}")
    print(f'  curl -X POST "{BASE_URL}/chats/{chat_ids[0]}/messages" \\')
    print(f'    -H "Content-Type: application/json" \\')
    print(f'    -d \'{{"role": "user", "content": "{TRICKY_QUESTIONS[0]["question"]}"}}\'')

    print(f"\n{Color.CYAN}{'=' * 70}{Color.RESET}\n")


def main():
    """Main population function"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}🚀 POPULATING DATABASE WITH TEST DATA{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.RESET}\n")

    # Create user
    user_id = create_user()
    if not user_id:
        return

    # Create KB with documents
    kb_id = create_kb_with_documents(user_id)
    if not kb_id:
        return

    # Create chats with conversation history
    chat_ids = create_chats_with_history(user_id, kb_id)

    # Save test scenarios
    save_test_scenarios(user_id, kb_id, chat_ids)

    # Print summary
    print_summary(user_id, kb_id, chat_ids)


if __name__ == "__main__":
    main()