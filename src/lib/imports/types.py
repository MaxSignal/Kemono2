from dataclasses import dataclass
from re import RegexFlag
from re import compile as compile_regexp
from typing import List, TypeVar, Generic

T = TypeVar("T")
max_length = 1024


@dataclass
class ValidationResult(Generic[T]):
    is_valid: bool
    errors: List[str] = None
    modified_result: T = None


def patreonKey(key: str, errors: List[str]):
    req_length = 43
    key_length = len(key)

    if key_length != req_length:
        errors.append(f'The key length of "{key_length}" is not a valid Patreon key. Required length: "{req_length}".')

    return errors


def fanboxKey(key: str, errors: List[str]):
    key_length = len(key)
    pattern_str = r"^\d+_\w+$"
    pattern = compile_regexp(pattern=pattern_str, flags=RegexFlag.IGNORECASE)

    if key_length > max_length:
        errors.append(f'The key length of "{key_length}" is over the maximum of "{max_length}".')

    if not pattern.match(key):
        errors.append(f'The key doesn\'t match the required pattern of "{pattern_str}".')

    return errors


def fantiaKey(key: str, errors: List[str]):
    req_lengths = [32, 64]
    key_length = len(key)

    if not any(list(key_length != length for length in req_lengths)):
        errors.append(
            f'The key length of "{key_length}" is not a valid Fantia key. '
            f'Accepted lengths: {", ".join(req_lengths)}.'
        )

    if (not key.islower()):
        errors.append('The key is not in lower case.')

    return errors


def gumroadKey(key: str, errors: List[str]):
    min_length = 200
    key_length = len(key)

    if (key_length < min_length):
        errors.append(f'The key length of "${key_length}" is less than minimum required "${min_length}".')

    if key_length > max_length:
        errors.append(f'The key length of "{key_length}" is over the maximum of "{max_length}".')

    return errors


def subscribestarKey(key: str, errors: List[str]):
    key_length = len(key)

    if key_length > max_length:
        errors.append(f'The key length of "{key_length}" is over the maximum of "{max_length}".')

    return errors


def dlsiteKey(key: str, errors: List[str]):
    key_length = len(key)

    if key_length > max_length:
        errors.append(f'The key length of "{key_length}" is over the maximum of "{max_length}".')

    return errors


def discordKey(key: str, errors: List[str]):
    pattern_str = r"(mfa.[a-z0-9_-]{20,})|([a-z0-9_-]{23,28}.[a-z0-9_-]{6,7}.[a-z0-9_-]{27})"
    pattern = compile_regexp(pattern_str, RegexFlag.IGNORECASE)
    key_length = len(key)

    if key_length > max_length:
        errors.append(f'The key length of "{key_length}" is over the maximum of "{max_length}".')

    if not pattern.match(key):
        errors.append(f'The key doesn\'t match the required pattern of "{pattern_str}".')

    return errors


service_constraints = dict(
    patreon=patreonKey,
    fanbox=fanboxKey,
    fantia=fantiaKey,
    gumroad=gumroadKey,
    subscribestar=subscribestarKey,
    dlsite=dlsiteKey,
    discord=discordKey,
)
