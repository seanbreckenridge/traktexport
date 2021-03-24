from typing import Dict, Any

from trakt.users import User  # type: ignore[import]


def export(username: str) -> Dict[str, Any]:
    my = User(username)
    return {
        "username": username,
        "followers": [u.username for u in my.followers],
        "following": [u.username for u in my.followers],
        "stats": my.get_stats(),
        "ratings": {
            _type: my.get_ratings(media_type=_type)
            for _type in ("movies", "shows", "seasons", "episodes")
        },
        "watched": {
            "movies": [m.to_json() for m in my.watched_movies],
            "shows": [s.to_json() for s in my.watched_shows],
        },
        "watchlist": {
            "movies": [m.to_json() for m in my.watchlist_movies],
            "shows": [s.to_json() for s in my.watchlist_shows],
        },
    }
