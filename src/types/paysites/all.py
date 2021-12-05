# from .base import Paysite
from .discord import Discord
from .dlsite import DLSite
from .fanbox import Fanbox
from .fantia import Fantia
from .gumroad import Gumroad
from .patreon import Patreon
from .subscribestar import Subscribestar
from .onlyfans import OnlyFans

# from typing import List


class Paysites:
    discord = Discord()
    dlsite = DLSite()
    fanbox = Fanbox()
    fantia = Fantia()
    gumroad = Gumroad()
    patreon = Patreon()
    subscribestar = Subscribestar()
    onlyfans = OnlyFans()
