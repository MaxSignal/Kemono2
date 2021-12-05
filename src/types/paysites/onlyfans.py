from dataclasses import dataclass
from .base import Paysite, Service_User, Service_Post


@dataclass
class User(Service_User):
    def profile(self, user_id: str) -> str:
        return f"https://onlyfans.com/{user_id}"


@dataclass
class Post(Service_Post):
    def link(self, post_id: str, user_id: str) -> str:
        return f"https://onlyfans.com/{post_id}/{user_id}"


@dataclass
class OnlyFans(Paysite):
    name: str = 'onlyfans'
    title: str = 'OnlyFans'
    user: User = User()
    post: Post = Post()
