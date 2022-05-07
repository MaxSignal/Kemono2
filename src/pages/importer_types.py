from dataclasses import dataclass
from typing import List

from src.internals.types import PageProps
from src.types.kemono import Unapproved_DM


@dataclass
class ImportProps(PageProps):
    currentPage = "import"


@dataclass
class StatusPageProps(ImportProps):
    import_id: str
    is_dms: bool


@dataclass
class DMPageProps(ImportProps):
    import_id: str
    account_id: int
    dms: List[Unapproved_DM]
