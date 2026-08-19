import hashlib
import time
from typing import Dict, Optional, Tuple
from src.models import StudentRequestDomainModel


class IdempotencyCache:
    """In-memory idempotency cache using SHA-256 hashes to prevent duplicate request processing."""

    def __init__(self, ttl_seconds: int = 86400):
        self.ttl_seconds = ttl_seconds
        # Maps hash -> (timestamp, StudentRequestDomainModel)
        self._cache: Dict[str, Tuple[float, StudentRequestDomainModel]] = {}

    def generate_hash(self, student_name: str, raw_text: str, student_id: str = "") -> str:
        """Compute SHA-256 hash of normalized request content."""
        normalized_str = f"{student_name.strip().lower()}|{student_id.strip().lower()}|{raw_text.strip().lower()}"
        return hashlib.sha256(normalized_str.encode("utf-8")).hexdigest()

    def get(self, request_hash: str) -> Optional[StudentRequestDomainModel]:
        """Check if request hash exists and is within TTL."""
        if request_hash in self._cache:
            entry_time, record = self._cache[request_hash]
            if time.time() - entry_time <= self.ttl_seconds:
                return record
            else:
                del self._cache[request_hash]
        return None

    def store(self, request_hash: str, record: StudentRequestDomainModel) -> None:
        """Store processed request record with current timestamp."""
        self._cache[request_hash] = (time.time(), record)

    def clear(self) -> None:
        """Clear cache (used for testing)."""
        self._cache.clear()


# Global singleton instance
idempotency_cache = IdempotencyCache()
