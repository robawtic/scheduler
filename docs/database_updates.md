# Database Updates

## Overview

This document explains how to update the database schema when there are changes to the models in the Scheduler application.

## Background

The Scheduler application uses SQLAlchemy ORM to define database models. When changes are made to these models (adding/removing fields, creating new models, etc.), the database schema needs to be updated to reflect these changes.

## Update Process

### Using the Update Script

The simplest way to update the database is to use the provided script:

```bash
python scripts\update_database.py
```

This script calls the `create_database()` function from `infrastructure.database`, which uses SQLAlchemy's `metadata.create_all()` to create or update tables based on the current model definitions.

### What the Script Does

The script:
1. Adds the project root to the Python module path
2. Imports the `create_database()` function
3. Calls the function to update the database schema
4. Prints confirmation messages

### Alternative: Running the Application

Alternatively, simply starting the application will also update the database schema, as `create_database()` is called during application startup in `main.py`.

## Important Notes

- This approach works well for development but may not be suitable for production environments with existing data
- For production, consider using a proper database migration tool like Alembic
- Always back up your database before updating the schema in a production environment

## Model Files

The following model files define the database schema:

- `domain/models/ApiKeyModel.py`
- `domain/models/DepartmentModel.py`
- `domain/models/EmployeeModel.py`
- `domain/models/GroupModel.py`
- `domain/models/LineTypeModel.py`
- `domain/models/RefreshTokenModel.py`
- `domain/models/RoleModel.py`
- `domain/models/ScheduleModel.py`
- `domain/models/TeamMemberModel.py`
- `domain/models/TeamModel.py`
- `domain/models/UserModel.py`
- `domain/models/WorkstationModel.py`