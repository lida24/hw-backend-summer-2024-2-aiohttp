from dataclasses import dataclass
from hashlib import sha256

from aiohttp_session import Session


@dataclass
class Admin:
    id: int
    email: str
    password: str | None = None

    @staticmethod
    def hash_password(password: str) -> str:
        return sha256(password.encode()).hexdigest()

    def is_password_valid(self, password: str) -> bool:
        return self.password == self.hash_password(password)

    @classmethod
    def get_current_session(cls, session: Session) -> "Admin":
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])
