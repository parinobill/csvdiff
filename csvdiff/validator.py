"""Validate CSV diff inputs and configurations."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationError:
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field}] {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, message: str) -> None:
        self.errors.append(ValidationError(field=field, message=message))

    def __str__(self) -> str:
        if self.is_valid:
            return "OK"
        return "\n".join(str(e) for e in self.errors)


def validate_key_column(
    key: str, columns: List[str], result: Optional[ValidationResult] = None
) -> ValidationResult:
    result = result or ValidationResult()
    if not key:
        result.add_error("key", "Key column must not be empty.")
    elif key not in columns:
        result.add_error("key", f"Key column '{key}' not found in columns: {columns}")
    return result


def validate_columns_exist(
    requested: List[str], available: List[str], result: Optional[ValidationResult] = None
) -> ValidationResult:
    result = result or ValidationResult()
    missing = [c for c in requested if c not in available]
    if missing:
        result.add_error("columns", f"Columns not found: {missing}")
    return result


def validate_diff_inputs(
    key: str,
    columns_a: List[str],
    columns_b: List[str],
    include_columns: Optional[List[str]] = None,
) -> ValidationResult:
    result = ValidationResult()
    validate_key_column(key, columns_a, result)
    validate_key_column(key, columns_b, result)
    if columns_a != columns_b:
        result.add_error("columns", f"Column mismatch: {columns_a} vs {columns_b}")
    if include_columns:
        validate_columns_exist(include_columns, columns_a, result)
    return result
