from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__(self.message)


class NotFoundError(AppError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=code, message=message, status_code=404, details=details or {})


class ConflictError(AppError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=code, message=message, status_code=409, details=details or {})


class BusinessRuleError(AppError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=code, message=message, status_code=422, details=details or {})
