from dataclasses import dataclass

from src.internals.types import PageProps


@dataclass
class SuccessProps(PageProps):
    """Props for `success` template."""
    message: str = 'Success!'
    currentPage: str
    redirect: str
