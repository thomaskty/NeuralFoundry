# NeuralFoundry : All in one assistant

## 🟢 Key Features Implemented

### 1. Multi-user Support
- Each user has a unique ID and profile.
- Users can create, view, and manage multiple chat sessions.

### 2. Chat Sessions
- Each user can create multiple chat sessions.
- Each chat session stores metadata (`title`, `created_at`) and is linked to its creator.

### 3. Message Memory & Context
- Chat messages (user + assistant) are stored in the database.
- Each message is converted into a **vector embedding** using a HuggingFace model (`embedding dimension = 384`).

### 4. Contextual Response Generation
- When a user sends a query, the system:
  1. Retrieves **top 5 most similar past messages** from that chat session via vector similarity search.
  2. Passes these retrieved conversation snippets as context to the LLM.
  3. Generates an assistant response based on the context, maintaining chat continuity.

### 5. Routers & API
- **User Router:** Create users, fetch user info, list user chats.
- **Chat Router:** Create chats (user-linked or generic), send messages, fetch messages, delete chats, list all chats.
- Clear RESTful hierarchy:
  - `/users/{user_id}/chats` → user-specific chats
  - `/chats/{chat_id}` → chat-specific operations
- Prepared for future authentication and permission enforcement.

### 6. Database & Storage
- PostgreSQL used as the main DB.
- Vector embeddings stored using `pgvector`.
- `ChatSession` ↔ `User` relationship implemented.
- `ChatMessage` ↔ `ChatSession` relationship implemented.
---

#### Setting up postgresql with Docker
```commandline
1. docker pull postgres:15
2. docker run --name NeuralFoundryPostgreServer -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=postgres -p 5432:5432 -d postgres:15
3. docker exec -it NeuralFoundryPostgreServer psql -U postgres
4. create database neuralfoundry;
```
#### setting up pgadmin with Docker
```commandline
5. docker run --name NeuralFoundryPgAdminServer -p 5050:80 -e PGADMIN_DEFAULT_EMAIL=<> -e PGADMIN_DEFAULT_PASSWORD=<> -d dpage/pgadmin4
6. docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' NeuralFoundryPostgreServer
7. register pgadmin with the above ip address, username(postgres) and password(above password) and name postgres-neural-foundry
```

## pgvector setup
```commandline
docker pull postgres:16
docker pull pgvector/pgvector:pg16
docker run --name pgvector -e POSTGRES_PASSWORD=<> -p 5433:5432 -d pgvector/pgvector:pg16

docker network create pgnet
docker network connect pgnet pgvector
docker run -d --name pgadmin --network pgnet -e PGADMIN_DEFAULT_EMAIL=<> -e PGADMIN_DEFAULT_PASSWORD=<> -p 5050:80 dpage/pgadmin4
```

## running the bash script 
```commandline
chmod +x run_all.sh; ./run_all.sh
```
