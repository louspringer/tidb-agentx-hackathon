#!/usr/bin/env python3
"""
Rate Limiting Module
Separate module for rate limiting functionality to avoid coupling with HTTPS enforcement.
"""

import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RateLimiting:
    """Rate limiting implementation to prevent abuse."""

    def __init__(self, redis_client) -> None:
        self.redis = redis_client
        self.default_limit = 100  # requests per minute
        self.default_window = 60  # seconds

    def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check if user has exceeded rate limit for endpoint."""
        key = f"rate_limit:{user_id}:{endpoint}"
        current = self.redis.get(key)

        if current is None:
            self.redis.setex(key, self.default_window, 1)
            return True

        count = int(current)
        if count >= self.default_limit:
            return False

        self.redis.incr(key)
        return True

    def get_remaining_requests(self, user_id: str, endpoint: str) -> int:
        """Get remaining requests for user on endpoint."""
        key = f"rate_limit:{user_id}:{endpoint}"
        current = self.redis.get(key)

        if current is None:
            return self.default_limit

        return max(0, self.default_limit - int(current))

    def reset_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Reset rate limit for user on endpoint."""
        key = f"rate_limit:{user_id}:{endpoint}"
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to reset rate limit for {user_id}:{endpoint}: {e}")
            return False

    def get_rate_limit_info(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        """Get detailed rate limit information."""
        key = f"rate_limit:{user_id}:{endpoint}"
        current = self.redis.get(key)
        ttl = self.redis.ttl(key)

        if current is None:
            return {
                "current_requests": 0,
                "remaining_requests": self.default_limit,
                "limit": self.default_limit,
                "window_seconds": self.default_window,
                "reset_time": time.time() + self.default_window,
            }

        current_count = int(current)
        return {
            "current_requests": current_count,
            "remaining_requests": max(0, self.default_limit - current_count),
            "limit": self.default_limit,
            "window_seconds": self.default_window,
            "reset_time": time.time() + (ttl if ttl > 0 else 0),
        }


if __name__ == "__main__":
    # Test rate limiting functionality
    import redis

    # Mock Redis client for testing
    mock_redis = redis.Redis(host="localhost", port=6379, db=0)
    rate_limiter = RateLimiting(mock_redis)

    # Test rate limit checking
    user_id = "test_user"
    endpoint = "api/deploy"

    print(f"Rate limit check: {rate_limiter.check_rate_limit(user_id, endpoint)}")
    print(
        f"Remaining requests: {rate_limiter.get_remaining_requests(user_id, endpoint)}"
    )
    print(f"Rate limit info: {rate_limiter.get_rate_limit_info(user_id, endpoint)}")
