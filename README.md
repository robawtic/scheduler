# Heijunka Scheduling System

A workforce management system that optimizes employee scheduling across workstations in a manufacturing environment.

## Features

- Schedule generation with constraint satisfaction
- Employee qualification and skill tracking
- Workstation management with required qualifications
- Call-in handling and schedule adjustments
- Multi-period daily scheduling
- REST API and CLI interfaces

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
# Option 1: Using pip directly
pip install -r requirements.txt

# Option 2: Using the installation script
python install_dependencies.py
```

> **Note:** The project uses FastAPI 0.95.2 with Pydantic 1.10.8 and typing-extensions 4.2.0 for compatibility. If you encounter dependency errors, make sure these specific versions are installed.

3. Set up the database:
- Create a PostgreSQL database
- Copy `.env.example` to `.env` and update the database connection settings
- Run database migrations:
```bash
alembic upgrade head
```

## Usage

### REST API

Start the API server:
```bash
uvicorn main:app --reload
```

If you encounter a "Port already in use" error, you can use the utility script to stop the process:
```bash
# Kill process using port 8080 (default)
python scripts\kill_api_process.py
```

The API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### CLI

The system provides a command-line interface for common operations:

```bash
# Generate a schedule
python cli.py generate --team-id 1 --start-date 2024-01-01 --periods 4

# Publish a schedule
python cli.py publish SCHEDULE_ID

# Handle a call-in
python cli.py call-in SCHEDULE_ID EMPLOYEE_ID
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
isort .
```

4. Run linters:
```bash
flake8
mypy .
```

## Architecture

The system follows Domain-Driven Design principles with a layered architecture:

- `domain/`: Core business logic and entities
- `application/`: Application services and use cases
- `infrastructure/`: Database and external service implementations
- `presentation/`: API and CLI interfaces

## License

MIT License 
