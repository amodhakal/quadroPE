# MLH PE Hackathon

**Stack:** Flask · Peewee ORM · PostgreSQL · Redis · Docker

## Docs map

- `docs/API.md` — endpoint behavior, request/response examples, and evaluation notes.
- `docs/runbook.md` — operational checks, common failures, and incident escalation flow.
- `docs/failure-manual.md` — postmortem template for documenting incidents.
- `docs/performance-bottleneck-report.md` — performance test template and bottleneck tracking.
- `docs/extended-guide.md` — extended project notes (profiles, testing, and workflow quick refs).

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** installed so you can clone and push your project

## Docker Services

| Service | Description | Ports |
| -------- | ----------- | ---- |
| **app** | Flask application (6 replicas) | 5000 |
| **postgres** | PostgreSQL 16 database | 5432 |
| **redis** | Redis 7 cache | 6379 |
| **nginx** | Reverse proxy / load balancer | 80 |
| **prometheus** | Metrics collection & monitoring | 9090 |
| **grafana** | Visualization dashboards | 3000 (admin/admin) |

## Quick Start

1. **Clone the repository and move into it**

    ```bash
    git clone <repo-url>
    cd quadroPE
    ```

2. **Configure your environment file (`.env`)**

    Create a `.env` file from the template (`.env` is gitignored and should **not** be committed):

    **macOS/Linux**

    ```bash
    cp .env.example .env
    ```

    **Windows PowerShell**

    ```powershell
    Copy-Item .env.example .env
    ```

3. **Start all services**

    ```bash
    docker compose up --build
    ```

4. **Health check**

    ```bash
    curl http://127.0.0.1/health  
    ```

    Expected response:

    ```json
    {"status":"ok"}
    ```

## Accessing Services

| Service | URL | Credentials |
| -------- | --- | ------------ |
| App | http://127.0.0.1   | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |

## Stopping Services

```bash
docker compose down
```

To also remove volumes (database data):

```bash
docker compose down -v
```

## Project Structure

```text
PE-Hackathon/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── database.py          # DatabaseProxy, BaseModel, connection hooks
│   ├── cache.py             # Redis cache utilities
│   ├── log_store.py         # Log storage utilities
│   ├── metrics_store.py     # Metrics storage utilities
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── url.py
│   │   └── event.py
│   ├── routes/              # API endpoints
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── urls.py
│   │   ├── events.py
│   │   ├── logs.py
│   │   ├── metrics.py
│   │   ├── prometheus.py
│   │   ├── dashboard.py
│   │   └── fail.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── alerts.py
│       ├── events.py
│       └── logger.py
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # App container definition
├── nginx/                   # Nginx configuration
│   └── nginx.conf
├── prometheus/              # Prometheus configuration
│   └── prometheus.yml
├── grafana/                 # Grafana dashboards & provisioning
│   ├── dashboards/
│   └── provisioning/
├── scripts/                 # Utility scripts
│   ├── generate_traffic.py
│   ├── load_csv.py
│   └── test_locust.py
├── tests/                   # Test suite
├── data/                    # CSV data files
├── loadtests/               # Load test reports
├── docs/                    # Documentation
├── pyproject.toml           # Project metadata + dependencies
├── .env.example             # Environment template
└── README.md
```
