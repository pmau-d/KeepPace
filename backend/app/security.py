import threading
import time
from collections import defaultdict, deque
from datetime import timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.config import settings
from app.types import utcnow

_hasher = PasswordHasher()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


def create_access_token(user_id: str) -> str:
    now = utcnow()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Renvoie l'id utilisateur du jeton, ou None s'il est invalide ou expiré."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]}
        )
    except jwt.PyJWTError:
        return None
    return payload["sub"]


class LoginRateLimiter:
    """Limite les échecs de connexion par (adresse IP, email), en mémoire.

    Suffisant pour une instance unique ; derrière plusieurs workers il faudrait
    un stockage partagé (Redis) — voir README.
    """

    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _recent(self, key: str) -> deque[float]:
        attempts = self._failures[key]
        cutoff = time.monotonic() - self.window
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        return attempts

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent(key)) >= self.max_attempts

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._recent(key).append(time.monotonic())

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._failures.clear()
            else:
                self._failures.pop(key, None)


login_limiter = LoginRateLimiter(settings.LOGIN_MAX_ATTEMPTS, settings.LOGIN_LOCKOUT_MINUTES * 60)
