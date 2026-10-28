# 🚚 Apex Logistics AI
### Autonomous Multi-Carrier Logistics Intelligence & Fleet Control Tower Platform (v6.0.0)

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.125.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com)
[![ML Engine](https://img.shields.io/badge/ML%20Engine-Huber%20GBDT%20%2B%20Circuity-orange.svg)](https://scikit-learn.org)
[![Nginx](https://img.shields.io/badge/Reverse%20Proxy-Nginx%20Alpine-009639.svg?logo=nginx&logoColor=white)](https://nginx.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, production-ready logistics operations platform integrating **Topography-Adaptive Road Circuity**, **Robust Gradient Boosted ETA Prediction ($p95 < 0.90\text{ ms}$)**, **Real-Time Multi-Carrier Linehaul Telemetry**, and **Autonomous ReAct Exception Resolution** for 3PL freight forwarders, linehaul carriers, and enterprise transportation management systems (TMS).

---

## 📋 Table of Contents

- [Key Capabilities](#-key-capabilities)
- [Enterprise System Architecture](#-enterprise-system-architecture)
- [Technology Stack](#-technology-stack)
- [Project Directory Layout](#-project-directory-layout)
- [Quick Start: Local Development](#-quick-start-local-development)
- [Production Deployment: Docker Compose](#-production-deployment-docker-compose)
- [API Gateway Reference](#-api-gateway-reference)
- [Control Tower & Web Portals](#-control-tower--web-portals)
- [Environment Variables & Configuration](#-environment-variables--configuration)
- [Health Monitoring & Verification](#-health-monitoring--verification)
- [License](#-license)

---

## 🌟 Key Capabilities

### 1. Topography-Adaptive Circuity & Robust GBDT ETA Engine
- **Nonlinear Circuity Modeling:** Dynamically scales route distances using elevation differential $\Delta h$ and physical roadway terrain curvature ($\kappa(\Delta h, d)$).
- **Outlier-Resilient Huber Loss:** Trained with $\delta = 1.35$ to neutralize linehaul congestion shocks, border delays, and adverse weather spikes without model divergence.
- **Ultra-Low Latency Inference:** Benchmarked at $p95 = 0.90\text{ ms}$ per query, supporting over $15,000\text{ queries/sec}$ under distributed load.

### 2. Multi-Carrier Telemetry Stream
- Unified telemetry ingestion across tier-1 international and regional carriers (**DHL Express**, **FedEx Ground**, **UPS Worldwide**, and **TCS Express**).
- Real-time tracking normalization, waypoint event logging, milestone progression, and automated dwell time detection.

### 3. Preemptive Exception Radar & Autonomous ReAct Resolution
- Closed-loop **Reason $\rightarrow$ Act $\rightarrow$ Observe** agent equipped with schema-validated deterministic tools.
- Proactively identifies at-risk linehaul shipments, triggers reroutes, auto-notifies dispatchers, and deflects up to **84% of WISMO ("Where Is My Order?") customer inquiries**.

### 4. Interactive Operations Control Tower
- High-density fleet map and shipment radar dashboard.
- Live corridor velocity analysis, $6 \times 6$ regional transit matrix heatmaps, carrier SLA compliance monitors, and real-time WebSocket alerts.

### 5. Multi-Tenant Role-Based Access Control (RBAC)
- Strict tenant data isolation with partitioned vector memory, shipment records, and carrier telemetry.
- Three built-in security personas: **Super Admin** (global infrastructure & tenant management), **Fleet Dispatcher** (carrier SLA & exception dispatch), and **Client Portal** (waybill self-service & tracking).

---

## 🏗 Enterprise System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENTS & EXTERNAL CONSUMERS                     │
│    Web Control Tower  │  Mobile Waybill Tracking  │  Enterprise TMS / EDI   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / WebSocket (:80 / :443)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NGINX REVERSE PROXY & GATEWAY                        │
│   • SSL/TLS Termination       • Static Asset Caching (HTML/JS/CSS)          │
│   • Rate Limiting & Gzip      • Reverse Proxy (/api/*, /ws/*)               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Internal Network
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     APEX LOGISTICS AI FASTAPI BACKEND                       │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐  │
│  │   Auth & RBAC JWT    │  │  Topography Circuity │  │  Huber GBDT ETA   │  │
│  │   Tenant Isolation   │  │  Distance Engine     │  │  Predictor Engine │  │
│  └──────────────────────┘  └──────────────────────┘  └───────────────────┘  │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐  │
│  │ Exception Radar &    │  │ Multi-Carrier Sync   │  │ ReAct Autonomous  │  │
│  │ Dwell Time Profiler  │  │ (DHL/FedEx/UPS/TCS)  │  │ Dispatch Agent    │  │
│  └──────────────────────┘  └──────────────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│  PERSISTENT STORAGE & CACHE                                                 │
│  • SQLite / PostgreSQL Database (Shipments, Waybills, Tenants, Audit Logs)  │
│  • Vector Store & Embeddings (Paraphrase Multilingual MiniLM L12)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API & Backend** | Python 3.11+, FastAPI, Uvicorn | Async REST APIs, WebSockets, high-throughput pipeline |
| **Machine Learning** | Scikit-Learn, LightGBM, NumPy, SciPy | Huber Gradient Boosting, topography circuity calibration |
| **Agentic Framework** | ReAct (Reason + Act), Function Calling | Automated exception handling, shipment diversion |
| **NLP & Sentiment** | Multilingual BERT, VADER, Lexicons | Customer intent routing, emotional escalation detection |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | ACID persistence, spatial indexing, multi-tenancy |
| **Web Reverse Proxy** | Nginx Alpine 1.27 | Static asset delivery, WebSocket tunneling, gzip compression |
| **Frontend** | Vanilla JavaScript (ES6+), CSS3 Glassmorphism | High-performance dashboard without bloated JS frameworks |
| **Containerization** | Docker, Docker Compose | Reproducible cross-platform containerized deployments |

---

## 📂 Project Directory Layout

```
behavioral-agentic-ai/
├── backend/
│   ├── app/
│   │   ├── ai/               # ReAct agent, LLM tool definitions, prompts
│   │   ├── api/              # REST controllers (shipments, logistics, auth, admin)
│   │   ├── models/           # SQLAlchemy schemas (Shipment, DeliveryZone, User)
│   │   ├── services/         # ETA predictor, circuity math, exception radar
│   │   ├── websocket/        # Real-time WebSocket connection manager
│   │   ├── database.py       # DB engine & session factory
│   │   └── main.py           # FastAPI application entrypoint & lifespan hooks
│   ├── scripts/              # Database seeders and benchmark generation scripts
│   ├── tests/                # Automated pytest test suites
│   ├── Dockerfile            # Production Python backend container spec
│   └── requirements.txt      # Pinned production Python dependencies
├── frontend/
│   ├── assets/               # SVG icons, logos, telemetry indicators
│   ├── css/                  # Glassmorphism design system & responsive styling
│   ├── js/                   # Live telemetry, REST client, WebSocket handlers
│   ├── pages/                # Control tower, admin console, tracking portal
│   ├── Dockerfile            # Alpine Nginx web container spec
│   └── index.html            # Public platform gateway & login
├── docker-compose.yml        # Multi-service production orchestration
├── nginx.conf                # Enterprise Nginx reverse proxy configuration
├── .env.example              # Production environment template
├── .dockerignore             # Docker build-context exclusions
├── .gitignore                # Git repository ignore rules
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start: Local Development

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Set Up Environment
```powershell
# Copy the environment template
cp .env.example .env

# Create and activate Python virtual environment
cd backend
python -m venv venv
.\venv\Scripts\activate   # On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Seed Realistic Logistics Database
Populate the database with sample commercial freight waybills, carrier telemetry, and delivery zones:
```powershell
python scripts/seed_rich_logistics_database.py
```

### 3. Start Development Servers
You can start the backend and frontend with one command:
```powershell
# In project root:
.\START_SYSTEM.bat
```
Alternatively, launch manually:
```powershell
# Terminal 1 (Backend):
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 (Frontend):
python -m http.server 5500
```

- **Operations Control Tower:** [http://localhost:5500/pages/client-dashboard.html](http://localhost:5500/pages/client-dashboard.html)
- **Super Admin Console:** [http://localhost:5500/pages/admin.html](http://localhost:5500/pages/admin.html)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Production Deployment: Docker Compose

Apex Logistics AI is engineered for production deployment on any Linux VPS, AWS EC2, DigitalOcean Droplet, or PaaS platform (e.g., Coolify).

### One-Command Deployment
```bash
# 1. Clone your production repository
git clone https://github.com/ubashir43/apex-logistics-ai.git
cd apex-logistics-ai

# 2. Configure production secrets
cp .env.example .env
nano .env  # Enter your JWT_SECRET_KEY, LLM keys, etc.

# 3. Launch the containerized stack
docker compose up -d --build
```

### Container Status & Logs
```bash
# Check running containers
docker compose ps

# View backend live logs
docker compose logs -f backend

# View web proxy logs
docker compose logs -f web
```

---

## 🔌 API Gateway Reference

Interactive OpenAPI documentation is automatically served at `/docs` and `/redoc`.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health` | Service health status, DB connectivity, WebSocket count | No |
| `POST` | `/api/auth/login` | Authenticate user & issue JWT bearer token | No |
| `GET` | `/api/shipments` | Query paginated fleet waybills with carrier filters | Bearer Token |
| `POST` | `/api/shipments` | Ingest new commercial freight waybill | Bearer Token |
| `GET` | `/api/shipments/{id}/telemetry` | Real-time GPS waypoint telemetry & transit history | Bearer Token |
| `POST` | `/api/logistics/predict-eta` | Real-time Topography-Adaptive GBDT ETA calculation | Bearer Token |
| `GET` | `/api/logistics/zones` | Retrieve spatial delivery zones, speed factors, risk | Bearer Token |
| `POST` | `/api/ai/agent/resolve-exception` | Trigger autonomous ReAct resolution for delayed freight | Bearer Token |
| `GET` | `/api/admin/system-health` | Cross-carrier performance audit & system metrics | Super Admin |

---

## 🖥 Control Tower & Web Portals

| Portal | URL Path | Default Role | Description |
|---|---|---|---|
| **Fleet Control Tower** | `/pages/client-dashboard.html` | Dispatcher / Client | Live fleet tracking, corridor velocity radar, exception management |
| **Super Admin Radar** | `/pages/admin.html` | Super Admin | Cross-carrier performance, tenant provisioning, system health |
| **Public Tracking Portal** | `/pages/login.html` | Public / Consignee | Waybill self-service, real-time ETA countdown, automated inquiry bot |

---

## ⚙ Environment Variables & Configuration

Key configuration parameters defined in `.env`:

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLAlchemy connection string (SQLite or PostgreSQL) |
| `JWT_SECRET_KEY` | *(Set a random 64-char string)* | Cryptographic key for JWT session validation |
| `LLM_API_KEY` | *(None)* | API key for LLM provider (OpenRouter, Anthropic, OpenAI) |
| `LLM_MODEL` | `anthropic/claude-sonnet-4` | Primary LLM model for ReAct exception agent |
| `HUBER_DELTA` | `1.35` | Huber loss transition threshold $\delta$ for ETA training |
| `CIRCUITY_BASELINE` | `1.27` | Baseline geometric circuity constant |
| `CIRCUITY_EXPONENT` | `0.88` | Elevation gradient attenuation exponent |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (lock down in production) |

---

## 🩺 Health Monitoring & Verification

Apex Logistics AI includes built-in container and endpoint health checks:

```bash
# Verify backend health endpoint
curl -s http://localhost:8000/api/health | jq .
```
Response:
```json
{
  "status": "healthy",
  "service": "apex-logistics-ai",
  "version": "6.0.0",
  "database": "connected",
  "websocket": {
    "connections": 0,
    "rooms": 0
  }
}
```

---

## 📄 License

This software is released under the **MIT License**. See [LICENSE](LICENSE) for full details.
