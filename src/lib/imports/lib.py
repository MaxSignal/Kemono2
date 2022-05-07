from .types import service_constraints, ValidationResult


def validate_import_key(key: str, service: str) -> ValidationResult:
    """
    Validates the key according to the `service` rules
    """
    # Trim spaces from both sides.
    formatted_key = key.strip()
    errors = service_constraints[service](formatted_key, [])

    return ValidationResult[str](
        is_valid=not errors,
        errors=errors,
        modified_result=formatted_key
    )
