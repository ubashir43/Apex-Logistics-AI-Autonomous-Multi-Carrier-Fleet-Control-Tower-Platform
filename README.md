<p align="center">
  <img src="frontend/assets/favicon.svg" width="80" alt="Apex Logistics AI Logo" />
</p>

<h1 align="center">Apex Logistics AI</h1>
<p align="center">
  <strong>Autonomous Multi-Carrier Logistics Intelligence &amp; Fleet Control Tower Platform</strong><br/>
  <sub>Version 6.0.0 · Production-Ready · Docker-Native · 44,800+ Lines of Code</sub>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.125.0-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://www.docker.com"><img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://nginx.org"><img src="https://img.shields.io/badge/Nginx-Alpine%201.27-009639?style=flat-square&logo=nginx&logoColor=white" alt="Nginx"></a>
  <a href="https://scikit-learn.org"><img src="https://img.shields.io/badge/ML-Huber%20GBDT-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="ML"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <a href="#-key-capabilities">Key Capabilities</a> ·
  <a href="#-system-architecture">Architecture</a> ·
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-docker-deployment">Docker Deploy</a> ·
  <a href="#-api-reference">API Reference</a>
</p>

---

## Overview

**Apex Logistics AI** is an enterprise-grade, production-ready platform for autonomous logistics operations — built for 3PL freight forwarders, linehaul carriers, and enterprise transportation management systems (TMS). It combines four core intelligence engines into a unified, deployable stack:

| Engine | What It Does | Key Metric |
|---|---|---|
| **Topography-Adaptive ETA** | Predicts freight arrival times using terrain-aware road circuity and Huber-loss GBDT | **0.51 h MAE** · p95 = 0.90 ms |
| **Multi-Carrier Telemetry** | Unified real-time tracking across DHL, FedEx, UPS, and TCS | 4 carriers · live WebSocket |
| **Exception Radar** | Proactively detects at-risk shipments and triggers autonomous resolution | **84% WISMO deflection** |
| **ReAct Dispatch Agent** | Closed-loop Reason → Act → Observe agent with schema-validated tools | Autonomous resolution |

> **Research Companion:** The ETA prediction engine is the subject of a peer-reviewed IEEE manuscript. See the full benchmark replication package at [ubashir43/topography-freight-eta](https://github.com/ubashir43/topography-freight-eta).

---

## 🌟 Key Capabilities

### Topography-Adaptive ETA Prediction Engine
- Dynamically models route distances using elevation differentials and physical roadway terrain curvature via the circuity function $\kappa(\Delta h, d)$
- Trained with Huber loss ($\delta = 1.35$) for resilience against linehaul congestion shocks, border delays, and adverse weather spikes
- Benchmarked at **p95 = 0.90 ms** per query, supporting **15,000+ queries/sec** on commodity hardware
- Achieves **42.7% MAE reduction** over static OSRM routing baselines

### Real-Time Multi-Carrier Telemetry
- Unified ingestion and normalization across **DHL Express**, **FedEx Ground**, **UPS Worldwide**, and **TCS Express**
- Real-time waypoint event logging, milestone progression tracking, and automated dwell time detection
- Live WebSocket push to Operations Control Tower dashboards

### Preemptive Exception Radar & Autonomous Resolution
- Closed-loop **ReAct** (Reason → Act → Observe) agentic framework with deterministic, schema-validated tool calls
- Proactively identifies at-risk linehaul shipments before SLA breach
- Triggers autonomous reroutes, auto-notifies dispatchers, and deflects **84% of WISMO inquiries**

### Interactive Operations Control Tower
- High-density fleet radar dashboard with real-time shipment visualization
- $6 \times 6$ regional transit matrix heatmaps, corridor velocity analysis, and carrier SLA compliance monitors
- Glassmorphism CSS3 design system — no JavaScript framework bloat

### Multi-Tenant RBAC & Data Isolation
- Strict tenant-level data partitioning across shipment records, vector memory, and carrier telemetry
- Three security personas: **Super Admin** (global infrastructure) · **Fleet Dispatcher** (carrier SLA & exceptions) · **Client Portal** (waybill self-service)
- JWT authentication with bcrypt password hashing and role-based route guards

---

## 🏗 System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          CLIENTS & EXTERNAL CONSUMERS                        │
│     Web Control Tower  ·  Mobile Waybill Tracking  ·  Enterprise TMS / EDI   │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │  HTTP / WebSocket (:80 / :443)
                                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                      NGINX REVERSE PROXY & API GATEWAY                       │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ SSL / TLS   │  │ Static Assets    │  │ Gzip       │  │ WebSocket      │  │
│  │ Termination │  │ Cache (7d TTL)   │  │ Compression│  │ Tunnel (/ws/*) │  │
│  └─────────────┘  └──────────────────┘  └────────────┘  └────────────────┘  │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │  Internal Docker Network
                                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     APEX LOGISTICS AI · FASTAPI BACKEND                      │
│                                                                               │
│  ┌───────────────────┐  ┌────────────────────┐  ┌────────────────────────┐   │
│  │  Auth & RBAC JWT  │  │  Topography-Aware  │  │  Huber GBDT ETA        │   │
│  │  Tenant Isolation │  │  Circuity Engine   │  │  Predictor (δ = 1.35)  │   │
│  └───────────────────┘  └────────────────────┘  └────────────────────────┘   │
│  ┌───────────────────┐  ┌────────────────────┐  ┌────────────────────────┐   │
│  │  Exception Radar  │  │  Multi-Carrier     │  │  ReAct Autonomous      │   │
│  │  & Dwell Profiler │  │  Sync & Normalize  │  │  Dispatch Agent (LLM)  │   │
│  └───────────────────┘  └────────────────────┘  └────────────────────────┘   │
│  ┌───────────────────┐  ┌────────────────────┐  ┌────────────────────────┐   │
│  │  3-Tier Sentiment │  │  RAG Knowledge     │  │  Intent Router &       │   │
│  │  (BERT + VADER)   │  │  Base Pipeline     │  │  WISMO Deflection      │   │
│  └───────────────────┘  └────────────────────┘  └────────────────────────┘   │
├───────────────────────────────────────────────────────────────────────────────┤
│  PERSISTENT STORAGE                                                           │
│  ├── SQLite / PostgreSQL   (Shipments, Waybills, Tenants, Users, Audit Logs) │
│  └── Vector Store          (Paraphrase Multilingual MiniLM-L12 Embeddings)   │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| **API & Runtime** | Python 3.11+, FastAPI, Uvicorn | High-throughput async REST APIs and WebSocket streams |
| **Machine Learning** | Scikit-Learn, NumPy, SciPy | Huber Gradient Boosting, topography circuity calibration |
| **NLP & Sentiment** | Multilingual BERT, VADER, 15-language lexicons | 3-tier sentiment analysis and emotional escalation detection |
| **Agentic Framework** | ReAct (Reason + Act), LLM Function Calling | Autonomous exception resolution and shipment diversion |
| **RAG Pipeline** | SentenceTransformers (MiniLM-L12), NumPy cosine | Tenant-isolated knowledge base retrieval and contextual responses |
| **Database** | SQLite (dev) / PostgreSQL (prod), SQLAlchemy 2.0 | ACID-compliant persistence with multi-tenant isolation |
| **Reverse Proxy** | Nginx 1.27 Alpine | TLS termination, static caching, gzip, WebSocket tunneling |
| **Frontend** | Vanilla ES6+ JavaScript, CSS3 Glassmorphism | 26,700+ lines — zero framework dependencies |
| **Containerization** | Docker, Docker Compose v3.8 | Reproducible multi-service orchestration with health checks |
| **Security** | JWT (python-jose), bcrypt, RBAC middleware | Token-based auth with role-guarded API routes |

---

## 📂 Project Structure

```
apex-logistics-ai/
│
├── backend/                          # FastAPI Application (18,100+ lines Python)
│   ├── app/
│   │   ├── ai/                       # ReAct agent, LLM integration, tool definitions
│   │   ├── api/                      # REST route handlers (13 modules)
│   │   ├── models/                   # SQLAlchemy ORM schemas (11 models)
│   │   ├── services/                 # Business logic: ETA, geospatial, sentiment, tracking
│   │   ├── middleware/               # Auth, rate limiting, performance monitoring
│   │   ├── knowledge/                # RAG document processing and vector indexing
│   │   ├── websocket/                # Real-time connection manager
│   │   └── main.py                   # Application entrypoint and lifespan hooks
│   ├── scripts/                      # Database seeders and data generation
│   ├── tests/                        # Automated test suites with evaluation benchmarks
│   ├── Dockerfile                    # Production multi-stage Python container
│   └── requirements.txt              # 102 pinned dependencies
│
├── frontend/                         # Control Tower Web UI (26,700+ lines)
│   ├── css/                          # 12 modular stylesheets (glassmorphism design system)
│   ├── js/                           # REST client, auth, telemetry, WebSocket handlers
│   ├── pages/                        # Dashboard, admin, login, onboarding, tracking
│   ├── widget/                       # Embeddable customer chat widget (<script> embed)
│   └── Dockerfile                    # Alpine Nginx static server
│
├── docker-compose.yml                # Production multi-service orchestration
├── nginx.conf                        # Enterprise reverse proxy configuration
├── .env.example                      # Annotated production environment template
├── .dockerignore                     # Build-context exclusions
├── .gitignore                        # Repository ignore rules
├── LICENSE                           # MIT License
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|:---|:---|
| Python | 3.11 or later |
| Git | 2.30+ |
| Docker *(optional, for production)* | 24.0+ with Compose v2 |

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/ubashir43/apex-logistics-ai.git
cd apex-logistics-ai

# 2. Configure environment
cp .env.example .env                  # Edit .env with your LLM API key

# 3. Create and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate              # Windows: .\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Seed the logistics database with realistic freight data
python scripts/seed_rich_logistics_database.py

# 6. Start the backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In a separate terminal, serve the frontend:
```bash
# From project root
cd frontend
python -m http.server 5500
```

Alternatively, launch everything with one command:
```powershell
.\START_SYSTEM.bat
```

### Access Points

| Portal | URL | Credentials |
|:---|:---|:---|
| **Operations Control Tower** | [localhost:5500/pages/client-dashboard.html](http://localhost:5500/pages/client-dashboard.html) | Fleet Dispatcher |
| **Super Admin Console** | [localhost:5500/pages/admin.html](http://localhost:5500/pages/admin.html) | Super Admin |
| **Interactive API Docs** | [localhost:8000/docs](http://localhost:8000/docs) | — |
| **Health Check** | [localhost:8000/api/health](http://localhost:8000/api/health) | — |

---

## 🐳 Docker Deployment

Apex Logistics AI ships with production-ready Docker configuration for deployment on any Linux VPS, AWS EC2, DigitalOcean Droplet, or PaaS platform (Coolify, Railway, etc.).

```bash
# 1. Clone and configure
git clone https://github.com/ubashir43/apex-logistics-ai.git
cd apex-logistics-ai
cp .env.example .env
nano .env                             # Set JWT_SECRET_KEY, LLM_API_KEY, etc.

# 2. Build and launch
docker compose up -d --build

# 3. Verify
docker compose ps
curl -s http://localhost:8000/api/health | jq .
```

### Container Architecture

| Container | Port | Image | Purpose |
|:---|:---|:---|:---|
| `apex-backend` | `8000` | Python 3.13-slim | FastAPI backend, ML engine, ReAct agent |
| `apex-web` | `80` | Nginx 1.27-alpine | Reverse proxy, static assets, WebSocket tunnel |

### Health Response

```json
{
  "status": "healthy",
  "service": "apex-logistics-ai",
  "version": "6.0.0",
  "database": "connected",
  "websocket": { "connections": 0, "rooms": 0 }
}
```

### Operations

```bash
docker compose logs -f backend        # Live backend logs
docker compose logs -f web            # Nginx access/error logs
docker compose down                   # Graceful shutdown
docker compose up -d --build          # Rebuild after code changes
```

---

## 🔌 API Reference

> Interactive documentation is auto-generated at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Core Endpoints

| Method | Endpoint | Description | Auth |
|:---|:---|:---|:---|
| `GET` | `/api/health` | Service health, DB connectivity, WebSocket status | None |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT bearer token | None |
| `POST` | `/api/auth/signup` | Register new user account | None |

### Logistics & Fleet Management

| Method | Endpoint | Description | Auth |
|:---|:---|:---|:---|
| `GET` | `/api/shipments` | Query paginated fleet waybills with carrier/status filters | Bearer |
| `POST` | `/api/shipments` | Ingest new commercial freight waybill | Bearer |
| `GET` | `/api/shipments/{id}/telemetry` | Real-time GPS waypoint history and transit milestones | Bearer |
| `POST` | `/api/logistics/predict-eta` | Topography-adaptive GBDT ETA calculation | Bearer |
| `GET` | `/api/logistics/zones` | Retrieve delivery zones with speed factors and risk scores | Bearer |

### AI & Autonomous Operations

| Method | Endpoint | Description | Auth |
|:---|:---|:---|:---|
| `POST` | `/api/ai/chat` | Conversational AI with intent routing and sentiment analysis | Bearer |
| `GET` | `/api/ai/health` | AI subsystem health (LLM, sentiment, embeddings) | Bearer |
| `POST` | `/api/widget/{api_key}/chat` | Public-facing embeddable chat widget endpoint | API Key |

### Administration

| Method | Endpoint | Description | Auth |
|:---|:---|:---|:---|
| `GET` | `/api/admin/system-health` | Cross-carrier performance audit and system metrics | Super Admin |
| `GET` | `/api/admin/tenants` | Multi-tenant management and provisioning | Super Admin |
| `GET` | `/api/admin/logistics-health` | Global logistics KPIs and exception breakdown | Super Admin |

---

## 🖥 Web Portals

| Portal | Path | Role | Description |
|:---|:---|:---|:---|
| **Fleet Control Tower** | `/pages/client-dashboard.html` | Dispatcher | Live fleet tracking, corridor velocity radar, exception management |
| **Super Admin Console** | `/pages/admin.html` | Super Admin | Cross-carrier analytics, tenant provisioning, system health |
| **Knowledge Base Manager** | `/pages/knowledge-base.html` | Admin | Upload PDFs, DOCX, CSV, images; train RAG retrieval pipeline |
| **Widget Management** | `/pages/widget-management.html` | Admin | Configure and deploy embeddable customer chat widgets |
| **Login Portal** | `/pages/login.html` | All | Authentication with 1-click test credential access |

---

## ⚙ Environment Configuration

All configuration is managed through environment variables defined in `.env`:

| Variable | Default | Description |
|:---|:---|:---|
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLAlchemy connection string (SQLite or PostgreSQL) |
| `JWT_SECRET_KEY` | *(must set)* | 64-character cryptographic key for JWT validation |
| `LLM_API_KEY` | *(must set)* | API key for LLM provider (OpenRouter / Anthropic / OpenAI) |
| `LLM_MODEL` | `anthropic/claude-sonnet-4` | Primary LLM for ReAct exception agent |
| `LLM_FALLBACK_MODEL` | `anthropic/claude-3-haiku` | Fallback model for cost-efficient operations |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | SentenceTransformer model for RAG embeddings |
| `HUBER_DELTA` | `1.35` | Huber loss transition threshold for ETA training |
| `CIRCUITY_BASELINE` | `1.27` | Baseline planar circuity constant $\kappa_0$ |
| `CIRCUITY_EXPONENT` | `0.88` | Elevation gradient attenuation exponent $\gamma$ |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (restrict in production) |
| `ENVIRONMENT` | `production` | Runtime environment flag |
| `LOG_LEVEL` | `INFO` | Application log verbosity |

> **Security Note:** Generate a production JWT secret with: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## 📄 License

Released under the [MIT License](LICENSE).

Copyright © 2026 Apex Logistics AI Contributors.
