from fastapi import APIRouter
import os
import redis

router = APIRouter()


# ============================================================
# FASTAPI HEALTH
# ============================================================

@router.get("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint for the FastAPI service.
    """
    return {
        "status": "healthy"
    }


# ============================================================
# REDIS HEALTH
# ============================================================

@router.get("/health/redis")
def redis_health_check() -> dict[str, str]:
    """
    Check whether the Redis server is reachable.
    """

    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
        )

        client.ping()

        return {
            "status": "healthy",
            "service": "redis",
        }

    except redis.exceptions.RedisError as error:
        return {
            "status": "unhealthy",
            "service": "redis",
            "error": str(error),
        }