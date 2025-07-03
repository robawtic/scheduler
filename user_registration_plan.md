# User Registration Implementation Plan

This document outlines the plan to implement user registration functionality in the Scheduler application. It includes changes to both the backend (FastAPI) and frontend (React) applications.

## 1. Backend Changes (FastAPI)

The backend needs a new endpoint to handle user creation and modifications to the authentication logic to use the database instead of hardcoded credentials.

### 1.1. Create User Database Model

We need a database model to store user information.

**File:** `infrastructure/models/user.py` (New File)

```python
from sqlalchemy import Column, Integer, String, Boolean
from infrastructure.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
```

### 1.2. Create User Domain Entity

Define the `User` entity in the domain layer.

**File:** `domain/entities/user.py` (New File)

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        orm_mode = True
```

### 1.3. Create User Repository Interface

Define the repository interface for user data access.

**File:** `domain/repositories/interfaces/user_repository.py` (New File)

```python
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.user import User
from infrastructure.models.user import User as UserModel


class UserRepositoryInterface(ABC):

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def create_user(self, username: str, password: str) -> User:
        pass

    @abstractmethod
    def get_user_for_auth(self, username: str) -> Optional[UserModel]:
        pass
```

### 1.4. Implement User Repository

Implement the repository for interacting with the user data in the database. We'''ll also need a password hashing utility.

**File:** `infrastructure/repositories/user_repository.py` (New File)

```python
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from domain.entities.user import User as UserEntity
from infrastructure.repositories.interfaces.user_repository import UserRepositoryInterface
from infrastructure.models.user import User as UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class UserRepository(UserRepositoryInterface):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        user = self.db_session.query(UserModel).filter(UserModel.username == username).first()
        if user:
            return UserEntity.from_orm(user)
        return None

    def create_user(self, username: str, password: str) -> UserEntity:
        hashed_password = get_password_hash(password)
        db_user = UserModel(username=username, hashed_password=hashed_password)
        self.db_session.add(db_user)
        self.db_session.commit()
        self.db_session.refresh(db_user)
        return UserEntity.from_orm(db_user)

    def get_user_for_auth(self, username: str) -> Optional[UserModel]:
        return self.db_session.query(UserModel).filter(UserModel.username == username).first()
```

### 1.5. Create User Registration API Model

Define the Pydantic model for the registration request body.

**File:** `presentation/api/models.py` (Append)

```python
# Add this to the end of the file

class UserCreate(BaseModel):
    """User creation request model."""
    username: str
    password: str
```

### 1.6. Create User Registration Endpoint

Create the new `/register` endpoint.

**File:** `presentation/api/routers/auth.py` (Modify)

```python
# Add these imports
from presentation.api.models import UserCreate, TokenResponse
from infrastructure.repositories.interfaces.user_repository import UserRepositoryInterface
from infrastructure.api.dependencies import get_user_repository
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException, status


# ... existing code ...

# Add this new endpoint to the router
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserCreate,
        user_repository: UserRepositoryInterface = Depends(get_user_repository)
):
    """
    Register a new user.
    """
    try:
        user = user_repository.create_user(username=user_data.username, password=user_data.password)
        return {"message": f"User {user.username} created successfully."}
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

# ... existing code ...
```

### 1.7. Update Login Endpoint

Modify the existing `/token` endpoint to authenticate against the database.

**File:** `presentation/api/routers/auth.py` (Modify)

```python
# ... imports ...
from infrastructure.repositories.user_repository import verify_password
from domain.entities.user import User as UserEntity
# ...

@router.post("/token", response_model=TokenResponse, response_model_exclude_unset=True)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(get_refresh_token_repository),
    user_repository: UserRepositoryInterface = Depends(get_user_repository)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user_model = user_repository.get_user_for_auth(form_data.username)
    if not user_model or not verify_password(form_data.password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_entity = UserEntity.from_orm(user_model)

    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={"sub": user_entity.username},
        roles=["viewer"],  # Default role
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user_entity.username},
        user_id=user_entity.id,
        refresh_token_repository=refresh_token_repository,
        device_info=None,
        ip_address=None
    )

    # Calculate token expiration time
    expires_at = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_at=expires_at
    )
```

### 1.8. Create Dependency Injection for Repository

**File:** `infrastructure/api/dependencies.py` (Modify)

```python
# ... existing imports
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.interfaces.user_repository import UserRepositoryInterface


# ... existing get_db and get_refresh_token_repository

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryInterface:
    return UserRepository(db)
```

## 2. Frontend Changes (React)

The frontend needs a new page and components to allow users to register.

### 2.1. Add Registration Route

**File:** `presentation/web-ui/src/App.tsx` (Modify)

```tsx
import React from ''';
import { BrowserRouter as Router, Route, Routes } from '''react-router-dom''';
// ... other imports
import Register from '''./pages/Register'''; // New import

function App() {
  return (
    <Router>
      <Routes>
        {/* ... other routes */}
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>
  );
}

export default App;
```

### 2.2. Create Registration Page

**File:** `presentation/web-ui/src/pages/Register.tsx` (New File)

```tsx
import React from ''';
import RegisterForm from '''../components/RegisterForm''';

const Register: React.FC = () => {
  return (
    <div>
      <h1>Register</h1>
      <RegisterForm />
    </div>
  );
};

export default Register;
```

### 2.3. Create Registration Form Component

**File:** `presentation/web-ui/src/components/RegisterForm.tsx` (New File)

```tsx
import React, { useState } from ''';
import { register } from '''../services/authService'''; // We will create this service

const RegisterForm: React.FC = () => {
  const [username, setUsername] = useState('''''');
  const [password, setPassword] = useState('''''');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const response = await register({ username, password });
      setMessage(response.message);
    } catch (err: any) {
      setError(err.message || '''Registration failed''');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <p style={{ color: '''red''' }}>{error}</p>}
      {message && <p style={{ color: '''green''' }}>{message}</p>}
      <div>
        <label>Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Register</button>
    </form>
  );
};

export default RegisterForm;
```

### 2.4. Create Authentication Service

**File:** `presentation/web-ui/src/services/authService.ts` (New File)

```typescript
import axios from '''axios''';
import { UserRegistration } from '''../types'''; // We will create this type

const API_URL = '''/api/auth'''; // Assuming the API is proxied

export const register = async (userData: UserRegistration) => {
  try {
    const response = await axios.post(`${API_URL}/register`, userData);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || '''An error occurred''');
  }
};
```

### 2.5. Define Type for Registration

**File:** `presentation/web-ui/src/types/index.ts` (Modify or Create)

```typescript
// Add this new type
export interface UserRegistration {
  username: string;
  password: string;
}
```

## 3. Database Migration

After creating the new `User` model, a database migration needs to be generated and applied.

1.  **Generate Migration:**
    ```bash
    alembic revision --autogenerate -m "Add user table"
    ```
2.  **Apply Migration:**
    ```bash
    alembic upgrade head
    ```

This concludes the implementation plan.
