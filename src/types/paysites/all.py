from dataclasses import dataclass, field
from .discord import Discord
from .dlsite import DLSite
from .fanbox import Fanbox
from .fantia import Fantia
from .gumroad import Gumroad
from .patreon import Patreon
from .subscribestar import Subscribestar

# from typing import List


@dataclass
class Paysites:
    discord: Discord = field(default_factory=Discord)
    dlsite: DLSite = field(default_factory=DLSite)
    fanbox: Fanbox = field(default_factory=Fanbox)
    fantia: Fantia = field(default_factory=Fantia)
    gumroad: Gumroad = field(default_factory=Gumroad)
    patreon: Patreon = field(default_factory=Patreon)
    subscribestar: Subscribestar = field(default_factory=Subscribestar)

    def __getitem__(self, key):
        return getattr(self, key)
