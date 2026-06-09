import os
import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

db_pool = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    await redis_client.ping()
    yield
    await db_pool.close()
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello from DevOps test task", "status": "ok"}

@app.get("/health")
async def health():
    """Проверка подключения к БД и Redis"""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        await redis_client.ping()
        return {"status": "healthy", "database": "up", "redis": "up"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {str(e)}")
