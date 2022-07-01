from flask import Blueprint, redirect, url_for, g


from src.lib.artist import get_random_artist_keys
from src.lib.post import get_random_posts_keys

import random as rand

random = Blueprint('random', __name__)


@random.route('/posts/random')
def random_post():
    post = get_random_post()
    if post is None:
        return redirect('back')

    return redirect(url_for('post.get', service=post['service'], artist_id=post['user'], post_id=post['id']))


@random.route('/artists/random')
def random_artist():
    artist = get_random_artist()
    if artist is None:
        return redirect('back')

    return redirect(url_for('artists.get', service=artist['service'], artist_id=artist['id']))


def get_random_post():
    post_keys = get_random_posts_keys(1000)
    if len(post_keys) == 0:
        return None
    return rand.choice(post_keys)


def get_random_artist():
    artists = get_random_artist_keys(1000)
    if len(artists) == 0:
        return None
    return rand.choice(artists)
