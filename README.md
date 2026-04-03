# SmartAmenities Backend

A FastAPI-based backend service for the SmartAmenities Android app, providing RESTful APIs for amenity data, navigation routing, and user management at DFW Airport.

---

## Overview

This backend serves the SmartAmenities mobile application by providing:

- **Amenity Data**: RESTful endpoints for retrieving amenity locations (restrooms, family restrooms, lactation rooms, water fountains) within airport terminals
- **Navigation Services**: Graph-based routing using NetworkX for turn-by-turn accessibility-aware navigation
- **User Management**: API endpoints for user authentication and preferences

Currently supports **Terminal D** with plans for expansion to other terminals.

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.13+ |
| Poetry | 1.8+ |
| NetworkX | 3.6+ |
| FastAPI | 0.135+ |

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd SmartAmenitiesBackend
```

### 2. Install Poetry

Install Poetry by following the official installation guide: https://python-poetry.org/docs/#installation

### 3. Install dependencies with Poetry

```bash
poetry install
```

### 4. Run the development server

```bash
poetry run start
```

The API will be available at `http://localhost:8000`

---

## API Endpoints

### Root
- `GET /` - Health check endpoint

### Amenities
- `GET /api/amenities` - Retrieve all amenities
- `GET /api/amenities/{id}` - Get specific amenity details
- `GET /api/amenities/search` - Search amenities by type/location

### Navigation
- `POST /api/navigation/route` - Calculate route between two points
- `GET /api/navigation/steps` - Get turn-by-turn navigation steps

### Users
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User authentication
- `GET /api/users/profile` - Get user profile and preferences

---

## Project Structure

```
SmartAmenitiesBackend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── dependencies.py  # API dependencies and middleware
│   │   └── routes/
│   │       ├── items.py     # Amenity-related endpoints
│   │       └── users.py     # User management endpoints
│   ├── core/                # Core configuration and utilities
│   ├── schemas/             # Pydantic models for request/response
│   └── services/            # Business logic and data services
├── tests/                   # Unit and integration tests
├── pyproject.toml           # Poetry configuration
└── README.md
```

---

## Architecture

**FastAPI + NetworkX** - Modern Python web framework with graph-based navigation.

- **API Layer**: FastAPI handles HTTP requests with automatic OpenAPI documentation
- **Graph Navigation**: NetworkX provides graph algorithms for shortest path calculations and accessibility routing
- **Data Models**: Pydantic schemas ensure type safety and validation
- **Dependency Injection**: FastAPI's dependency system for clean architecture

---

## Key Dependencies

| Library | Purpose |
|---------|---------|
| FastAPI | Modern web framework for building APIs |
| NetworkX | Graph creation and analysis for navigation |
| Uvicorn | ASGI server for running FastAPI |
| Pydantic | Data validation and serialization |

---

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
poetry run isort .
```

### API Documentation

When running, visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

---

## Deployment

The application can be deployed using:

- **Docker**: Containerized deployment
- **Heroku**: Cloud platform deployment
- **AWS/GCP**: Cloud infrastructure

Build for production:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## License

[Add license information here]
