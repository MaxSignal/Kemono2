from dataclasses import dataclass, field

from configs.derived_vars import is_development

from .discord import Discord
from .dlsite import DLSite
from .fanbox import Fanbox
from .fantia import Fantia
from .gumroad import Gumroad
from .patreon import Patreon
from .subscribestar import Subscribestar


@dataclass
class Paysites:
    discord: Discord = field(default_factory=Discord)
    dlsite: DLSite = field(default_factory=DLSite)
    fanbox: Fanbox = field(default_factory=Fanbox)
    fantia: Fantia = field(default_factory=Fantia)
    gumroad: Gumroad = field(default_factory=Gumroad)
    patreon: Patreon = field(default_factory=Patreon)
    subscribestar: Subscribestar = field(default_factory=Subscribestar)

    if (is_development):
        from .kemono_dev import KemonoDev
        kemonodev: KemonoDev = field(default_factory=KemonoDev)

    def __getitem__(self, key):
        return getattr(self, key)
