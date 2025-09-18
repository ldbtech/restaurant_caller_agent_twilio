# backend-Risona

## Project Overview

**backend-Risona** is a modular backend system composed of several microservices, each responsible for a specific domain of the application. The architecture is designed for scalability, maintainability, and ease of development.

---

## Microservices Overview

### 1. auth-service
Handles authentication, authorization, and user management. Integrates with Firebase and Redis for secure token storage and validation.
- **Main Tech:** Python, gRPC, Firebase, Redis
- **Key Files:** `main.py`, `app/services/`, `requirements.txt`
- **Install dependencies:**
  ```bash
  pip install -r auth-service/requirements.txt
  ```

### 2. llm-service
Provides LLM (Large Language Model) capabilities, menu loading, and retrieval. Integrates with Ollama, ChromaDB, and supports FastAPI for serving endpoints.
- **Main Tech:** Python, FastAPI, gRPC, Ollama, ChromaDB
- **Key Files:** `app/`, `Dockerfile`, `requirements.txt`
- **Install dependencies:**
  ```bash
  pip install -r llm-service/requirements.txt
  ```

### 3. gateway-service
Acts as the API gateway, routing requests to the appropriate microservices. Handles HTTP/gRPC traffic and environment configuration.
- **Main Tech:** Python, FastAPI, gRPC
- **Key Files:** `app/`, `Dockerfile`, `docker-compose.yml`, `requirements.txt`
- **Install dependencies:**
  ```bash
  pip install -r gateway-service/requirements.txt
  ```

### 4. db-service
Manages database operations, including Firestore integration and gRPC endpoints for data access.
- **Main Tech:** Python, Firestore, gRPC
- **Key Files:** `app/`, `run_server.py`, `requirements.txt`
- **Install dependencies:**
  ```bash
  pip install -r db-service/requirements.txt
  ```

### 5. twilio-service
Handles communication via Twilio, exposing endpoints for messaging and integration with other services.
- **Main Tech:** Python, FastAPI, gRPC, Twilio
- **Key Files:** `app/`, `Dockerfile`, `requirements.txt`
- **Install dependencies:**
  ```bash
  pip install -r twilio-service/requirements.txt
  ```

### 6. ollama-service
Contains deployment and service manifests for the Ollama LLM infrastructure (Kubernetes YAMLs).
- **Main Tech:** Kubernetes
- **Key Files:** `ollama-deployment.yaml`, `ollama-service.yaml`, `ollama-external.yaml`

---

## General Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ldbtech/backend-flikor.git
   cd backend-flikor
   ```
2. **Python version:** Use Python 3.10+ (recommended: 3.12)
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. **Install dependencies for each service as needed.**

---

## Running the Services

Each service can be run independently. Navigate to the service directory and follow its instructions (see above for dependencies). Example for `auth-service`:

```bash
cd auth-service
python main.py
```

Some services may require environment variables (see `.env` files or documentation in each service directory).

---

## Development & Contribution

- Add new dependencies to the appropriate `requirements.txt` and run `pip freeze > requirements.txt` if needed.
- Use `.gitignore` to avoid committing virtual environments or large binaries.
- Pull requests and issues are welcome!

---

## Contact & Support

For questions, open an issue on the [GitHub repository](https://github.com/ldbtech/backend-flikor) or contact the maintainers.
