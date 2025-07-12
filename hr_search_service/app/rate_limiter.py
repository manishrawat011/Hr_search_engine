# app/rate_limiter.py
import time
from collections import defaultdict
from typing import Dict, Tuple

# Configuration for the rate limiter
RATE_LIMIT_COUNT = 5  # Max requests allowed
RATE_LIMIT_WINDOW_SECONDS = 60  # Time window in seconds (e.g., 5 requests per minute)

class RateLimiter:
    """
    A simple, in-memory rate limiter.
    This implementation is naive and suitable for a single instance.
    For distributed systems, a shared, persistent store like Redis would be required.
    """
    def __init__(self):
        # Stores {client_key: [(timestamp1, count1), (timestamp2, count2), ...]}
        # We'll keep track of individual request timestamps to manage the sliding window.
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def _clean_old_requests(self, client_key: str):
        """Removes timestamps outside the current rate limit window."""
        current_time = time.time()
        # Filter out requests older than the window
        self._requests[client_key] = [
            t for t in self._requests[client_key]
            if current_time - t < RATE_LIMIT_WINDOW_SECONDS
        ]

    def check_limit(self, client_key: str) -> bool:
        """
        Checks if the client has exceeded the rate limit.

        Args:
            client_key (str): A unique identifier for the client (e.g., IP address).

        Returns:
            bool: True if the request is allowed, False if rate-limited.
        """
        self._clean_old_requests(client_key)
        return len(self._requests[client_key]) < RATE_LIMIT_COUNT

    def record_request(self, client_key: str):
        """
        Records a request for the given client.
        Should only be called if check_limit returned True.

        Args:
            client_key (str): A unique identifier for the client.
        """
        self._requests[client_key].append(time.time())

# Global instance of the RateLimiter
# In a real application, this might be managed by a dependency injection framework
# or be part of a larger application state.
rate_limiter = RateLimiter()

