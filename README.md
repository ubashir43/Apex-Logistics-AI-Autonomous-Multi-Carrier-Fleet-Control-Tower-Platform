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
  <a href="#-api-reference">API Reference</a> ·
  <a href="#-web-portals">Web Portals</a>
</p>

---

## Overview

**Apex Logistics AI** is an enterprise-grade, production-ready autonomous logistics intelligence platform engineered for commercial 3PL freight forwarders, intermodal carriers, and modern Transportation Management Systems (TMS). It bridges the operational divide between backend telemetry streams and customer-facing operations across four core pillars:

| Engine | What It Does | Key Metric |
|---|---|---|
| **Topography-Adaptive ETA** | Predicts freight arrival times using terrain-aware road circuity and Huber-loss GBDT | **0.51 h MAE** · p95 = 0.90 ms |
| **Multi-Carrier Telemetry** | Unified tracking across FedEx, DHL, UPS, Maersk, and Linehaul | 258+ live waybills · WebSocket |
| **Exception Radar** | Proactively detects at-risk shipments and triggers autonomous resolution | **84.5% deflection** · 0.763 sentiment |
| **ReAct Dispatch Agent** | Closed-loop Reason → Act → Observe agent with schema-validated tools | Autonomous policy synthesis |

> **Research Companion:** The ETA prediction engine is the subject of a peer-reviewed IEEE manuscript. See the full benchmark replication package at [ubashir43/Topography-Adaptive-Road-Circuity-Multi-Carrier-Freight-Transportation-ETA-Prediction](https://github.com/ubashir43/Topography-Adaptive-Road-Circuity-Multi-Carrier-Freight-Transportation-ETA-Prediction).

---

## 🌟 Key Capabilities

### Topography-Adaptive ETA Prediction Engine
- Dynamically models route distances using elevation differentials and physical roadway terrain curvature via the circuity function $\kappa(\Delta h, d)$
- Trained with Huber loss ($\delta = 1.35$) for resilience against linehaul congestion shocks, customs holds, and adverse weather spikes
- Benchmarked at **p95 = 0.90 ms** per query, supporting **15,000+ queries/sec** on commodity hardware
- Achieves **42.7% MAE reduction** over static flat-SLA routing baselines down to **0.51 hours**

### Real-Time Multi-Carrier Telemetry
- Unified ingestion and normalization across **FedEx Ground**, **DHL Express**, **UPS Worldwide**, **Maersk Line**, and **Regional Linehaul**
- Real-time waypoint event logging, milestone progression tracking, and automated dwell time detection across 258+ commercial waybills
- Live WebSocket push to Operations Control Tower dashboards

### Preemptive Exception Radar & Autonomous Resolution
- Closed-loop **ReAct** (Reason → Act → Observe) agentic framework with deterministic, schema-validated tool calls
- Proactively identifies at-risk linehaul shipments before SLA breach
- Triggers autonomous reroutes, auto-notifies dispatchers, and deflects **84.5% of repetitive WISMO inquiries**

### Interactive Fleet Dispatcher Control Tower
- High-density fleet radar dashboard with real-time shipment visualization
- Milestone audit timelines (Order Created $\rightarrow$ Picked Up $\rightarrow$ In Transit $\rightarrow$ Customs Clearance $\rightarrow$ Out for Delivery $\rightarrow$ Delivered)
- 6-Zone regional transit matrix, corridor velocity analysis, and carrier SLA compliance monitors
- Modern CSS3 glassmorphism design system — zero JavaScript framework bloat

### Super Admin Executive Governance & TMS Gateway Monitor
- Executive governance suite providing real-time gateway health monitoring for FedEx Web Services, DHL REST, UPS API, Maersk EDI, and Linehaul
- High-level platform KPIs: deflection rates, emotion sentiment trajectory, and tenant provisioning
- Strict tenant-level data partitioning with role-based JWT route guards

### Apex Logistics Copilot (Personal AI for Fleet Management)
- Embedded conversational AI assistant powered by Tenant #2 (`Apex Logistics Copilot`)
- Features branded FedEx Purple design styling (`#4d148c` / `#7c3aed`), instant waybill lookups, ML transit forecasts, and intelligent human agent escalation

---

## 🏗 System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          CLIENTS & EXTERNAL CONSUMERS                        │
│    Fleet Control Tower  ·  Super Admin Console  ·  Apex Logistics Copilot    │
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
│  │  & Dwell Profiler │  │  TMS Gateway Sync  │  │  Dispatch Agent (LLM)  │   │
│  └───────────────────┘  └────────────────────┘  └────────────────────────┘   │
│  ┌───────────────────┐  ┌────────────────────┐  ┌────────────────────────┐   │
│  │  3-Tier Sentiment │  │  RAG Knowledge     │  │  Fast-Path WISMO       │   │
│  │  (BERT + VADER)   │  │  Base Pipeline     │  │  Router (< 1 ms)       │   │
│  └───────────────────┘  └────────────────────┘  └────────────────────────┘   │
├───────────────────────────────────────────────────────────────────────────────┤
│  PERSISTENT STORAGE                                                           │
│  ├── SQLite / PostgreSQL   (258 Waybills, Telemetry, Tenants, Users, Audits) │
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
| **Database** | SQLite WAL (dev) / PostgreSQL (prod), SQLAlchemy 2.0 | ACID-compliant persistence with multi-tenant isolation |
| **Reverse Proxy** | Nginx 1.27 Alpine | TLS termination, static caching, gzip, WebSocket tunneling |
| **Frontend** | Vanilla ES6+ JavaScript, CSS3 Glassmorphism | 26,700+ lines — zero framework dependencies |
| **Branding System** | FedEx Purple Palette (`#4d148c` / `#7c3aed`) | Custom SVG autonomous freight cube mark & High-DPI Favicon |
| **Containerization** | Docker, Docker Compose v3.8 | Reproducible multi-service orchestration with health checks |
| **Security** | JWT (python-jose), bcrypt, RBAC middleware | Token-based auth with role-guarded API routes |

---

## 📂 Project Structure

```
Apex-Logistics-AI-Autonomous-Multi-Carrier-Fleet-Control-Tower-Platform/
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
│   ├── scripts/                      # Database seeders, normalizers, and tenant scripts
│   ├── tests/                        # Automated test suites with evaluation benchmarks
│   ├── Dockerfile                    # Production multi-stage Python container
│   └── requirements.txt              # Pinned production dependencies
│
├── frontend/                         # Control Tower Web UI (26,700+ lines)
│   ├── assets/                       # High-DPI Favicon SVG & brand assets
│   ├── css/                          # 12 modular stylesheets (glassmorphism design system)
│   ├── js/                           # REST client, auth, telemetry, WebSocket handlers
│   ├── pages/                        # Control Tower, Super Admin, Login, Signup, Onboarding
│   ├── widget/                       # Embeddable Apex Logistics Copilot widget (embed.js)
│   ├── logo-preview.html             # Asset showcase for Favicon and Vector Brandmark
│   └── Dockerfile                    # Alpine Nginx static server
│
├── docker-compose.yml                # Production multi-service orchestration
├── nginx.conf                        # Enterprise reverse proxy configuration
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
git clone https://github.com/ubashir43/Apex-Logistics-AI-Autonomous-Multi-Carrier-Fleet-Control-Tower-Platform.git
cd Apex-Logistics-AI-Autonomous-Multi-Carrier-Fleet-Control-Tower-Platform

# 2. Configure environment
cp .env.example .env                  # Edit .env with your configuration

# 3. Create and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate              # Windows: .\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the backend daemon
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In a separate terminal, serve the frontend:
```bash
# From project root
cd frontend
python -m http.server 5500
```

Alternatively, launch both services with one command:
```powershell
.\START_SYSTEM.bat
```

### Access Points & Default Credentials

| Portal | URL | Default Credentials | Role / Purpose |
|:---|:---|:---|:---|
| **Fleet Control Tower** | [localhost:5500/pages/client-dashboard.html](http://localhost:5500/pages/client-dashboard.html) | `dispatcher@apexlogistics.com` / `Dispatch2026!` | Tactical Fleet Operations & Waybill Radar |
| **Super Admin Console** | [localhost:5500/pages/admin.html](http://localhost:5500/pages/admin.html) | `admin@behavioral-ai.com` / `Admin1234!` | Executive Governance & TMS Gateway Monitor |
| **Apex Logistics Copilot** | [localhost:5500/widget-test.html](http://localhost:5500/widget-test.html) | Direct interactive access | Personal AI Widget for Fleet Management System |
| **Corporate Website** | [localhost:5500/index.html](http://localhost:5500/index.html) | Public | Enterprise Fleet Landing with Live Copilot |
| **Interactive API Docs** | [localhost:8000/docs](http://localhost:8000/docs) | OpenAPI / Swagger | Full REST API test interface |
| **Brand Showcase** | [localhost:5500/logo-preview.html](http://localhost:5500/logo-preview.html) | Public | High-DPI Favicon & Vector Mark Verification |

---

## 🐳 Docker Deployment

Apex Logistics AI ships with production-ready Docker configuration for deployment on any Linux VPS, AWS EC2, DigitalOcean Droplet, or PaaS platform (Coolify, Railway, etc.).

```bash
# 1. Clone and configure
git clone https://github.com/ubashir43/Apex-Logistics-AI-Autonomous-Multi-Carrier-Fleet-Control-Tower-Platform.git
cd Apex-Logistics-AI-Autonomous-Multi-Carrier-Fleet-Control-Tower-Platform
cp .env.example .env

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

### Administration & TMS Monitoring

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
| **Super Admin Console** | `/pages/admin.html` | Super Admin | TMS gateway monitoring, tenant provisioning, executive deflection KPIs |
| **Apex Logistics Copilot** | `/widget-test.html` | Public / Consignee | Dedicated interactive personal AI for fleet tracking and resolution |
| **Knowledge Base Manager** | `/pages/knowledge-base.html` | Admin | Carrier SLA, tariff matrix, and customs compliance document RAG |
| **Widget Management** | `/pages/widget-management.html` | Admin | Configure and deploy embeddable customer chat widgets |
| **Login Portal** | `/pages/login.html` | All | Authentication with 1-click test credential access |

---

## 📄 License

Released under the [MIT License](LICENSE).

Copyright © 2026 Apex Logistics AI Contributors.
