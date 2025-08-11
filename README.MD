# Project Setup & Usage

## Prerequisites

- [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/install/)

---

## Getting Started

### 1. **Build the Docker Containers**
```bash
docker compose build
```

### 2. **Start the Containers**
```bash
docker compose up
```

This will launch all three containers:
- **project-tracker-db-1**  
  _PostgreSQL database_
- **project-tracker-redis-data**  
  _Redis database_
- **project-tracker-backend-fastapi**  
  _Backend DB API_
- **project-tracker-workfllow-fastapi**  
  _Agentic workflow API_
- **project-tracker-frontend-fastapi**  
  _Chatbot App API_
- **project-tracker-mcp-db**  
  _MCP server to DB_
- **project-tracker-mcp-gemini**  
  _MCP server to Gemini_

![img.png](containers.png)
### 3. **Access the FastAPI Database CRUD**
Open your browser and go to:
http://localhost:8000/docs#/
![img_3.png](fastapi_test_page.png)

Here you can interact with all FastAPI endpoints using the Swagger UI.

### 4. **Test Out All pytest Test Cases**
To run all the test cases, follow these steps:

1. **Open a shell inside the running backend container:**
   ```bash
   docker exec -it project-tracker-backend-fastapi sh
   ```
2. **Run the pytest:**
```bash
pytest -vv -s --show-capture=all
```

[![Watch the video](pytest_screenshot.png)](pytest.mp4)
The link to video: [pytest.mp4](pytest.mp4)

### 5. **Test Out the Agentic Workflow**
To run the agentic workflow, follow these steps:

Just go to http://localhost:7860/

The example user prompts used in the demo: [test_prompts.txt](workflow%2Ftest_prompts.txt)

The link to video: [Recording 2025-08-09 204404.mp4](Recording%202025-08-09%20204404.mp4)

## 6. **Architecture Overview**

This project implements an agentic workflow system integrating multiple components to manage projects and tasks efficiently. The core architecture is designed for scalability, observability, and smooth user interaction.
![img.png](project_tracker_overview.png)
---

### Key Components

#### 1. Workflow Nodes

- **Orange Boxes (LLM Nodes):**  
  These nodes use large language models (LLMs) to perform tasks such as identifying intent (planning), clarifying intent/ details, analyzing, and producing the final answer.  
  _Example nodes:_ `Plan`, `Clarify`, `Analyze After Check`, `Final Answer`.

- **Purple Boxes (Database Query Nodes):**  
  These nodes query the PostgreSQL database to fetch existing project and task data, enabling the workflow to make informed decisions.  
  _Example nodes:_ `Query Tasks`, `Query Projects`, `Check Project Exist`, `Check Task Exist`.

- **Pink Boxes (Database Create Nodes):**  
  Nodes responsible for creating new entries in the database, such as adding projects or tasks.  
  _Example nodes:_ `Create Project`, `Create Task`.

---
#### 2. Internal Prompt Engineering Technique and Design
All the prompts used are within [mcp-server/src/utils/gemini_prompt](mcp-server%2Fsrc%2Futils%2Fgemini_prompts)

Modular Prompt Templates per Node: Each LLM node (`Plan`, `Clarify`, `Analyze After Check`, `Final Answer`) has a purpose-built prompt template guiding the model’s behavior precisely for its task.

Separation of Concerns: Each prompt targets a specific subtask (intent detection, clarification, analysis, final response), reducing complexity and easing maintenance.

Dynamic Context Injection: Prompts incorporate the current conversation context and relevant database query results from previous nodes to maintain continuity across multiple user turns and data interactions.

Few-Shot and Instruction-Based Prompting: Examples and clear instructions are embedded in prompts to reduce ambiguity and ensure output consistency.

Prompt Safety Guardrails: Prompts contain safety instructions not to answer some particular sensitive information i.e. API Key for now.

Progressive Refinement via Clarify Node: If user input or outputs are incomplete, prompts in the Clarify node solicit additional information to improve understanding.

In production environment, what can be done better in terms of prompt?
- Provide more examples on what the agent should not respond to (i.e. api key, password, PII)
- Version control should be applied to each node for traceability on model performance.

---

#### 3. Data and Context Management

- **Langgraph Redis**  
  - For development and testing, conversation context is managed using Redis, which temporarily holds session states. This allows the agent to maintain context across multiple user inputs within the same workflow.
  - This is especially important for nodes like the **Clarify** node, where the user may need to provide additional information or partial input. Using in-memory context ensures that the agent does not lose track of previous context when the user inputs are incomplete or spread over multiple interactions.

- **Guardrails for Sensitive Data:**
  - Currently, basic guardrails are in place that use keyword-based detection to prevent accidental leakage of sensitive information such as passwords, API keys, and access tokens.
  - In a production environment, can use an online streaming ML model to redact PII, for example using Microsoft Presidio.

---

#### 4. Backend and Data Persistence

- **PostgreSQL:**  
  Serves as the primary relational database storing `Project` and `Task` entities, queried and updated by workflow nodes.

- **FastAPI Backend:**  
  Hosts the REST API, interacts with the MCP Server, PostgreSQL database, and message broker for background jobs.

- **FastAPI Workflow:**  
  Hosts the REST API, wrapping agentic workflow.

- **MCP Servers:**  
  Acts as the orchestrator for tool calls, mediating between the LLMs, the API for database queries, and external APIs (if anymore).

---

#### 5. Background Processing & Monitoring (Production Considerations)

- **Message Broker & Background Jobs:**  
  - Triggered on project/task creation, update, or deletion to send notification emails (e.g., SMTP server integration).  
  - Batch jobs archive projects/tasks that are complete or expired for more than two years.  
  - Periodic summary jobs (weekly/monthly) generate reports on projects/tasks.

- **Monitoring with DataDog:**
  - Logs and metrics such as error rates, latency, request counts, and throughput are sent to DataDog for real-time monitoring and alerting. 
  - The performance of the LLM agent can also be monitored by user satisfaction rates in terms of answer quality (frontend development for interaction is required) and user retention rate. 
  - Additionally, smaller models can be employed to evaluate relevance and assist with continuous quality assessment.

---

#### 6. User Interaction

Users interact with the system primarily through the **agentic workflow** interface, which processes intents, queries, and updates tasks/projects accordingly.

---

#### 7. Summary Flow

1. User send request to agentic workflow API.
2. Workflow nodes perform planning and clarifying with LLM tools.  
3. Database query nodes check existing data in PostgreSQL.  
4. Based on checks, creation nodes add new projects or tasks.  
5. Final answers are composed and returned to the user.  
6. Context is managed in-memory during development and Redis in production.  
7. All operations generate logs monitored by DataDog in production
8. Background jobs handle asynchronous email notifications and archiving in production.



## 7. Project Structure

```plaintext
.
├── backend/
│   ├── database_api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── enum/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests/
│   ├── __init__.py
│   ├── Dockerfile
│   └── start.sh
├── frontend/
│   ├── __init__.py
│   ├── demo.py/
├── mcp-server-db/
│   ├── src/
│   │   ├── handlers/
│   │   ├── utils/
│   │   └── server.ts
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── mcp-server-gemini/
│   ├── src/
│   │   ├── handlers/
│   │   ├── utils/
│   │   └── server.ts
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── workflow/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── chatbot.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── node_1.py
│   │   ├── node_2.py
│   │   ├── node_3.py
│   │   ├── ...
│   ├── agent_context.py
│   ├── agent_state.py
│   ├── agent_workflow.py
│   ├── cli.py
│   ├── guardrail.py
│   ├── setup_mcp.py
│   └── utils.py
├── .env
├── .gitignore
├── .pre-commit-config.yaml
└── docker-compose.yaml
