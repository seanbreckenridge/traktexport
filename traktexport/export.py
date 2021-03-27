from time import sleep
from typing import Dict, Any, Iterator, List
from urllib.parse import urljoin

import backoff  # type: ignore[import]
from trakt.core import CORE, BASE_URL  # type: ignore[import]
from trakt.errors import RateLimitException  # type: ignore[import]
from logzero import logger  # type: ignore[import]

# for some reason, if I dont import this, even if I'm not
# using any code from there, this fails to authenticate
import trakt.users  # type: ignore

# expononentailly backoff, but dont start at one second
def expo_higher() -> Iterator[int]:
    e = backoff.expo()
    for _ in range(3):
        next(e)
    yield from e


# This uses the bare CORE._handle_request instead of the wrapper
# types so that I have access to more info
#
# the trakt module here is used for authentication, I just
# create the URLs/save the entire response
@backoff.on_exception(expo_higher, (RateLimitException,))
def _trakt_request(endpoint: str, method: str = "get", data: Any = None) -> Any:
    # endpoint: The URL to make a request to, doesn't include the domain
    # method is lowercase because _handle_request expects it to be
    url = urljoin(BASE_URL, endpoint)
    logger.debug(f"Requesting '{url}'...")
    json_data: Any = CORE._handle_request(method=method.lower(), url=url, data=data)
    sleep(2)
    return json_data


def _trakt_paginate(endpoint_bare: str, limit: int = 100) -> Iterator[Any]:
    page = 1
    while True:
        items: List[Any] = _trakt_request(f"{endpoint_bare}?limit={limit}&page={page}")
        if len(items) == 0:
            break
        logger.debug(f"First item: {items[0]}")
        yield from items
        page += 1


def export(username: str) -> Dict[str, Any]:
    return {
        "username": username,
        "followers": _trakt_request(f"users/{username}/followers"),
        "following": _trakt_request(f"users/{username}/following"),
        "settings": _trakt_request("users/settings"),
        "likes": _trakt_request("users/likes"),
        "profile": _trakt_request(f"users/{username}"),
        "comments": _trakt_request(f"users/{username}/comments"),
        "lists": _trakt_request(f"users/{username}/lists"),
        "ratings": _trakt_request(f"users/{username}/ratings"),
        "recommendations": _trakt_request(f"users/{username}/recommendations"),
        "watchlist": _trakt_request(f"users/{username}/watchlist"),
        "watched": _trakt_request(f"users/{username}/watched/movies")
        + _trakt_request(f"users/{username}/watched/shows"),
        "collection": _trakt_request(f"users/{username}/collection/movies")
        + _trakt_request(f"users/{username}/collection/shows"),
        "stats": _trakt_request(f"users/{username}/stats"),
        "history": list(_trakt_paginate(f"users/{username}/history")),
    }
