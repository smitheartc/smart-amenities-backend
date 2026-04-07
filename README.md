# SmartAmenities Backend

A FastAPI-based backend for the SmartAmenities Android app — provides route recommendations and admin management for amenities at DFW Airport Terminal D.

---

## Overview

- **Route Recommendations**: Graph-based Dijkstra routing using NetworkX; ranks amenities by walk time + crowd wait time
- **Admin Panel APIs**: Manage individual amenity status/crowd, apply zone-level controls, and trigger simulation scenarios
- **Database**: AWS RDS MySQL via SQLAlchemy; amenity state persists across restarts

Currently supports **Terminal D** only.

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.13+ |
| Poetry | 1.8+ |
| FastAPI | 0.135+ |
| NetworkX | 3.6+ |

---

## Getting Started

### 1. Install dependencies

```bash
poetry install
```

### 2. Run the development server

```bash
poetry run start
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## API Endpoints

### Route Recommendation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/route/recommend` | Returns ranked amenity recommendations from a user's location |

**Request body:**
```json
{
  "user_node": "COR_C",
  "amenity_type": "Restroom",
  "wheelchair_required": false
}
```

**Response:** ordered list of recommendations (sorted by `total_seconds = walk + wait`), each containing `amenity_id`, `path`, `walk_seconds`, `wait_seconds`, `crowd_level`, `status`.

Valid `amenity_type` values: `"Restroom"`, `"Family Restroom"`, `"Lactation Room"`, `"Gender-Neutral Restroom"`, `"Water Fountain"`

Valid `user_node` values: any graph node ID — gates (`D5`–`D40`), corridor intersections (`COR_W`, `COR_C`, `COR_E`), Skylink stations (`SKY_W`, `SKY_E`), security checkpoints (`SEC_D18`, `SEC_D30`)

---

### Admin

All admin endpoints are prefixed with `/api/admin`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/amenities` | List all amenities regardless of status |
| `PATCH` | `/api/admin/amenity/{id}` | Update a single amenity's status and/or crowd level |
| `DELETE` | `/api/admin/amenity/{id}/override` | Reset amenity to OPEN + UNKNOWN crowd |
| `PATCH` | `/api/admin/zone` | Bulk update crowd, avg usage time, or open/closed for a zone |
| `GET` | `/api/admin/scenarios` | List all simulation scenarios |
| `POST` | `/api/admin/scenario/apply` | Apply a simulation scenario by ID |

**Zone values:** `"All Zones"`, `"East Zone"` (D5–D18), `"Central Zone"` (D19–D30), `"West Zone"` (D31–D40)

**PATCH /api/admin/amenity/{id} body:**
```json
{
  "status": "Closed",
  "crowd_level": "Long Wait"
}
```

**PATCH /api/admin/zone body:**
```json
{
  "zone": "East Zone",
  "crowd_level": "Medium Wait",
  "avg_usage_minutes": 7,
  "is_open": true
}
```

**POST /api/admin/scenario/apply body:**
```json
{
  "scenario_id": 1
}
```

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `amenities` | Amenity records — status, crowd level, location, accessibility flags |
| `crowd_readings` | Audit log — every crowd level change is recorded here with a timestamp |
| `simulation_scenarios` | Named scenarios with JSON override configs (e.g. "D22 Closed") |
| `users` | User accounts |

---

## Project Structure

```
smart-amenities-backend/
├── app/
│   ├── main.py                        # FastAPI app entry point + lifespan setup
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── map.py                 # POST /api/route/recommend
│   │       └── admin.py              # Admin endpoints
│   ├── core/
│   │   └── database.py               # SQLAlchemy engine + session
│   ├── models/
│   │   └── models.py                 # SQLAlchemy ORM models + enums
│   ├── schemas/
│   │   └── schemas.py                # Pydantic request/response schemas
│   └── services/
│       └── terminal_d_graph_service.py  # NetworkX graph + Dijkstra routing
├── data/
│   └── mock_airport_nodes.json       # Terminal D graph definition
├── pyproject.toml
└── README.md
```

---

## Architecture

- **API layer**: FastAPI with automatic OpenAPI docs
- **Routing engine**: NetworkX graph loaded at startup from `mock_airport_nodes.json`; live amenity status overlaid from DB on each request
- **Database**: SQLAlchemy ORM → AWS RDS MySQL
- **Validation**: Pydantic schemas for all request/response types

---

## Running for Production

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
