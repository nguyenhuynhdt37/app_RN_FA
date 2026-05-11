# FastAPI Master Architecture 2026 — Implementation Playbook

Complete code patterns, checklists, and reference implementations.

---

## 1. Core Setup

### `app/core/config.py`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "DeliveryAPI"
    DEBUG: bool = False

    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

settings = Settings()
```

### `app/core/security.py`
```python
from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"exp": expire, "sub": str(subject)}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")
```

### `app/core/logging.py`
```python
import logging
import sys
import structlog

def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=level)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
    )

logger = structlog.get_logger()
```

---

## 2. Database Layer

### `app/db/session.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL), echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### `app/db/base.py`
```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

---

## 3. Redis Cache

### `app/cache/redis.py`
```python
import json
import functools
from typing import Callable, Any
import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)

def cache(ttl: int = 300, key_prefix: str = ""):
    """Decorator for async service methods. Caches JSON-serializable return values."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{key_prefix or func.__name__}:{args}:{kwargs}"
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

async def invalidate_cache(pattern: str) -> None:
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
```

---

## 4. Global Exception Handler

### `app/main.py`
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import auth, wallet, orders, restaurants
from app.api.ws import tracking

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.DEBUG)
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# --- Global Exception Handlers ---
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status_code": 422, "code": "VALIDATION_ERROR", "detail": exc.errors()},
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status_code": 400, "code": "BAD_REQUEST", "detail": str(exc)},
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status_code": 500, "code": "INTERNAL_ERROR", "detail": "An unexpected error occurred."},
    )

# --- Routers ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(restaurants.router, prefix="/api/v1/restaurants", tags=["Restaurants"])
app.include_router(tracking.router, prefix="/ws", tags=["WebSocket"])
```

---

## 5. Example Module: Wallet (Complete)

### `app/schemas/wallet.py`
```python
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class TopUpRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=50_000_000, description="VND amount to top up")
    payment_method: Literal["momo", "vnpay", "bank_transfer"]

    @field_validator("amount")
    @classmethod
    def amount_must_be_round(cls, v: Decimal) -> Decimal:
        if v % 1000 != 0:
            raise ValueError("Amount must be a multiple of 1,000 VND")
        return v

class WalletTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    driver_id: int
    amount: Decimal
    transaction_type: str
    status: str
    created_at: datetime

class WalletBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: int
    balance: Decimal
    updated_at: datetime
```

### `app/models/wallet.py`
```python
from decimal import Decimal
from sqlalchemy import Numeric, String, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.base import Base, TimestampMixin

class TransactionType(str, enum.Enum):
    TOP_UP = "top_up"
    WITHDRAWAL = "withdrawal"
    COMMISSION = "commission"
    BONUS = "bonus"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Wallet(Base, TimestampMixin):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("drivers.id"), unique=True, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))

class WalletTransaction(Base, TimestampMixin):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("drivers.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    transaction_type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType))
    status: Mapped[TransactionStatus] = mapped_column(SAEnum(TransactionStatus), default=TransactionStatus.PENDING)
    reference_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
```

### `app/services/wallet.py`
```python
from decimal import Decimal
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wallet import Wallet, WalletTransaction, TransactionType, TransactionStatus
from app.schemas.wallet import TopUpRequest, WalletTransactionResponse, WalletBalanceResponse
from app.cache.redis import cache, invalidate_cache
from app.core.logging import logger

class WalletService:

    def __init__(self, db: AsyncSession):
        self.db = db

    @cache(ttl=60, key_prefix="wallet_balance")
    async def get_balance(self, driver_id: int) -> WalletBalanceResponse:
        result = await self.db.execute(select(Wallet).where(Wallet.driver_id == driver_id))
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise ValueError(f"Wallet not found for driver {driver_id}")
        return WalletBalanceResponse.model_validate(wallet)

    async def top_up(self, driver_id: int, payload: TopUpRequest) -> WalletTransactionResponse:
        try:
            # 1. Lock and fetch wallet row
            result = await self.db.execute(
                select(Wallet).where(Wallet.driver_id == driver_id).with_for_update()
            )
            wallet = result.scalar_one_or_none()
            if not wallet:
                raise ValueError("Wallet not found")

            # 2. Create transaction record (PENDING)
            txn = WalletTransaction(
                driver_id=driver_id,
                amount=payload.amount,
                transaction_type=TransactionType.TOP_UP,
                status=TransactionStatus.PENDING,
            )
            self.db.add(txn)
            await self.db.flush()  # get txn.id without committing

            # 3. Update balance
            wallet.balance += payload.amount
            txn.status = TransactionStatus.SUCCESS

            await self.db.commit()
            await self.db.refresh(txn)

            # 4. Invalidate cached balance
            await invalidate_cache(f"wallet_balance:({driver_id},)*")

            logger.info("wallet.top_up.success", driver_id=driver_id, amount=str(payload.amount))
            return WalletTransactionResponse.model_validate(txn)

        except Exception as e:
            await self.db.rollback()
            logger.error("wallet.top_up.failed", driver_id=driver_id, error=str(e))
            raise
```

### `app/api/v1/wallet.py`
```python
from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.wallet import TopUpRequest, WalletTransactionResponse, WalletBalanceResponse
from app.services.wallet import WalletService
from app.core.dependencies import get_current_driver

router = APIRouter()

@router.get("/balance", response_model=WalletBalanceResponse, status_code=status.HTTP_200_OK)
async def get_wallet_balance(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_driver_id: Annotated[int, Depends(get_current_driver)],
):
    service = WalletService(db)
    return await service.get_balance(current_driver_id)

@router.post("/top-up", response_model=WalletTransactionResponse, status_code=status.HTTP_201_CREATED)
async def top_up_wallet(
    payload: TopUpRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_driver_id: Annotated[int, Depends(get_current_driver)],
):
    service = WalletService(db)
    result = await service.top_up(current_driver_id, payload)
    # Fire-and-forget: send push notification
    background_tasks.add_task(_notify_top_up, current_driver_id, payload.amount)
    return result

async def _notify_top_up(driver_id: int, amount) -> None:
    # TODO: integrate push notification service
    pass
```

---

## 6. WebSocket: Real-Time Driver Tracking

### `app/api/ws/tracking.py`
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, WebSocket] = {}

    async def connect(self, driver_id: int, ws: WebSocket):
        await ws.accept()
        self.active[driver_id] = ws

    def disconnect(self, driver_id: int):
        self.active.pop(driver_id, None)

    async def broadcast_to_order(self, order_id: int, data: dict):
        # In production, use Redis Pub/Sub to fan out across instances
        message = json.dumps(data)
        for ws in self.active.values():
            try:
                await ws.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/tracking/{driver_id}")
async def driver_location_ws(websocket: WebSocket, driver_id: int):
    await manager.connect(driver_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Expected: {"lat": 10.776, "lng": 106.700, "order_id": 42}
            lat = data.get("lat")
            lng = data.get("lng")
            order_id = data.get("order_id")

            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                await websocket.send_json({"error": "Invalid GPS coordinates"})
                continue

            await manager.broadcast_to_order(order_id, {
                "driver_id": driver_id,
                "lat": lat,
                "lng": lng,
            })
    except WebSocketDisconnect:
        manager.disconnect(driver_id)
```

---

## 7. Dependencies

### `app/core/dependencies.py`
```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_driver(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        payload = decode_token(token)
        driver_id = int(payload["sub"])
        return driver_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "detail": "Invalid or expired token"},
        )
```

---

## 8. Background Tasks Pattern

```python
# Always inject BackgroundTasks via FastAPI DI — never create threads manually.
from fastapi import BackgroundTasks

@router.post("/orders/{order_id}/confirm")
async def confirm_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = OrderService(db)
    order = await service.confirm(order_id)
    background_tasks.add_task(send_confirmation_email, order.customer_email, order_id)
    background_tasks.add_task(send_push_notification, order.driver_id, "New order assigned!")
    return order
```

---

## 9. Checklist Before Pushing Any Module

- [ ] Schema has both `Request` and `Response` classes
- [ ] All Pydantic models use `ConfigDict(from_attributes=True)` for ORM compat
- [ ] SQLAlchemy model has `TimestampMixin`
- [ ] Service methods are all `async def`
- [ ] DB calls use `await`
- [ ] Mutations wrapped in `try/except` with `rollback()`
- [ ] Router has zero business logic
- [ ] Cached endpoints invalidate on mutation
- [ ] Global exception handler returns `{status_code, code, detail}` JSON
- [ ] Sensitive routes protected with `Depends(get_current_driver)`

---

## 10. Stack Reference

| Layer | Library | Version |
|-------|---------|---------|
| Web Framework | FastAPI | ≥ 0.111 |
| Validation | Pydantic V2 | ≥ 2.7 |
| ORM | SQLAlchemy (Async) | ≥ 2.0 |
| DB Driver | asyncpg | ≥ 0.29 |
| Cache | redis[asyncio] | ≥ 5.0 |
| Auth | python-jose + bcrypt | latest |
| Settings | pydantic-settings | ≥ 2.2 |
| Logging | structlog | ≥ 24.0 |
| Migrations | Alembic | ≥ 1.13 |
| Testing | pytest-asyncio + httpx | latest |
