# MLH PE Hackathon — Flask + Peewee + PostgreSQL Template

[New info here](/README_NEW.md)

A minimal hackathon starter template. You get the scaffolding and database wiring — you build the models, routes, and CSV loading logic.

**Stack:** Flask · Peewee ORM · PostgreSQL · uv

## **Important**

You need to work with around the seed files that you can find in [MLH PE Hackathon](https://mlh-pe-hackathon.com) platform. This will help you build the schema for the database and have some data to do some testing and submit your project for judging. If you need help with this, reach out on Discord or on the Q&A tab on the platform.

## Prerequisites

- **uv** — a fast Python package manager that handles Python versions, virtual environments, and dependencies automatically.
  Install it with:

  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  For other methods see the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).
- **PostgreSQL running locally** (Docker or a local install is fine)
- **Git** installed so you can clone and push your project

## uv Basics

`uv` manages your Python version, virtual environment, and dependencies automatically — no manual `python -m venv` needed.

| Command | What it does |
|---------|--------------|
| `uv sync` | Install all dependencies (creates `.venv` automatically) |
| `uv run <script>` | Run a script using the project's virtual environment |
| `uv add <package>` | Add a new dependency |
| `uv remove <package>` | Remove a dependency |

## Quick Start (copy/paste friendly)

If this is your first Flask + Postgres app, follow these exact steps in order:

1. **Clone the repository and move into it**

    ```bash
    git clone <repo-url>
    cd <repo-folder>
    ```

2. **Install dependencies**

    ```bash
    uv sync
    ```

3. **Create the PostgreSQL database**

    ```bash
    createdb hackathon_db
    ```

    If `createdb` is not available, open `psql` and run:

    ```sql
    CREATE DATABASE hackathon_db;
    ```

4. **Configure your environment file (`.env`)**

    - A `.env` file already exists in this repo. Update it if your Postgres username/password/port are different.
    - You can also reset it from the template:

    **macOS/Linux**

    ```bash
    cp .env.example .env
    ```

    **Windows PowerShell**

    ```powershell
    Copy-Item .env.example .env
    ```

5. **Run the app**

    ```bash
    uv run run.py
    ```

    You should see Flask start on `http://localhost:5000`.

6. **Health check (confirm it works)**

    ```bash
    curl http://localhost:5000/health
    ```

    Expected response:

    ```json
    {"status":"ok"}
    ```

## Project Structure

```
mlh-pe-hackathon/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── database.py          # DatabaseProxy, BaseModel, connection hooks
│   ├── models/
│   │   └── __init__.py      # Import your models here
│   └── routes/
│       └── __init__.py      # register_routes() — add blueprints here
├── .env.example             # DB connection template
├── .gitignore               # Python + uv gitignore
├── .python-version          # Pin Python version for uv
├── pyproject.toml           # Project metadata + dependencies
├── run.py                   # Entry point: uv run run.py
└── README.md
```

## How to Add a Model

1. Create a file in `app/models/`, e.g. `app/models/product.py`:

```python
from peewee import CharField, DecimalField, IntegerField

from app.database import BaseModel


class Product(BaseModel):
    name = CharField()
    category = CharField()
    price = DecimalField(decimal_places=2)
    stock = IntegerField()
```

1. Import it in `app/models/__init__.py`:

```python
from app.models.product import Product
```

1. Create the table (run once in a Python shell or a setup script):

```python
from app.database import db
from app.models.product import Product

db.create_tables([Product])
```

## How to Add Routes

1. Create a blueprint in `app/routes/`, e.g. `app/routes/products.py`:

```python
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.product import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products")
def list_products():
    products = Product.select()
    return jsonify([model_to_dict(p) for p in products])
```

2. Register it in `app/routes/__init__.py`:

```python
def register_routes(app):
    from app.routes.products import products_bp
    app.register_blueprint(products_bp)
```

## How to Load CSV Data

```python
import csv
from peewee import chunked
from app.database import db
from app.models.product import Product

def load_csv(filepath):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            Product.insert_many(batch).execute()
```

## Useful Peewee Patterns

```python
from peewee import fn
from playhouse.shortcuts import model_to_dict

# Select all
products = Product.select()

# Filter
cheap = Product.select().where(Product.price < 10)

# Get by ID
p = Product.get_by_id(1)

# Create
Product.create(name="Widget", category="Tools", price=9.99, stock=50)

# Convert to dict (great for JSON responses)
model_to_dict(p)

# Aggregations
avg_price = Product.select(fn.AVG(Product.price)).scalar()
total = Product.select(fn.SUM(Product.stock)).scalar()

# Group by
from peewee import fn
query = (Product
         .select(Product.category, fn.COUNT(Product.id).alias("count"))
         .group_by(Product.category))
```

## Tips

- Use `model_to_dict` from `playhouse.shortcuts` to convert model instances to dictionaries for JSON responses.
- Wrap bulk inserts in `db.atomic()` for transactional safety and performance.
- The template uses `teardown_appcontext` for connection cleanup, so connections are closed even when requests fail.
- Check `.env.example` for all available configuration options.

## Troubleshooting (common setup issues)

- **`uv: command not found`**
  - Re-open your terminal after installing `uv`, then run `uv --version` to confirm it is available.

- **`createdb: command not found`**
  - PostgreSQL client tools are not on your PATH yet.
  - Use `psql` and run `CREATE DATABASE hackathon_db;`, or add PostgreSQL's `bin` directory to your PATH.

- **Database connection errors when starting the app**
  - Confirm PostgreSQL is running.
  - Confirm `.env` values match your local setup (`DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`).
  - Confirm `DATABASE_URL` points to `hackathon_db`.

- **Health check doesn't return `{\"status\":\"ok\"}`**
  - Make sure the app is still running in the terminal where you started `uv run run.py`.
  - Double-check you are visiting `http://localhost:5000/health`.
  - If port `5000` is already used by another app, stop that process and re-run.
