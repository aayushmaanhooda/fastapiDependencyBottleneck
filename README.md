# FastAPI Connection Pool Bottleneck

Demonstrates how `Depends(get_session)` holds a DB connection open during post-DB work (e.g. external API calls), and how a session factory fixes it.

Reference: https://www.akanz.de/posts/fastapi-connection-pools/

---

## Setup

**1. Start the database**
```bash
docker compose up -d
```

**2. Create a `.env` file**
```
DATABASE_URL="postgresql://admin:postgres@localhost:5432/tododb"
```

**3. Install dependencies**
```bash
uv sync
```

---

## Run the experiment

**Bottleneck version** (connection held during entire request)
```bash
python3 main.py
```

**Optimized version** (connection released before post-DB work)
```bash
python3 solution.py
```

**Load test**
```bash
locust
```
Open http://localhost:8089 — set 20 users, spawn rate 5.

Point host at `http://localhost:8000` for bottleneck, `http://localhost:8001` for optimized.

---

## Results

### Bottleneck (`main.py`)
![Bottleneck results](bottelneck_img/Screenshot%202026-03-03%20at%2010.57.52%20AM.png)

### Optimized (`solution.py`)
![Optimized results](solution_img/Screenshot%202026-03-03%20at%2010.59.23%20AM.png)

| | Bottleneck | Optimized |
|---|---|---|
| Pool size | 3 connections | 3 connections |
| Connection held during sleep | yes | no |
| Expected p99 | high | ~500ms |

The pool is intentionally set to `pool_size=3, max_overflow=0` in `config.py` to make the bottleneck visible with 20 concurrent users.

---

Happy experimenting!
