from dataclasses import dataclass

from src.internals.types import PageProps


@dataclass
class SuccessProps(PageProps):
    """Props for `success` template."""
    currentPage: str
    redirect: str
    message: str = 'Success!'
