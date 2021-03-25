# some DAL https://beepb00p.xyz/exports.html#dal
# code to parse the export into an ADT-like format
#
# this uses dataclasses so that I can possibly
# fix datetimes for items which I watched
# a *long* time ago, i.e. movies I watched
# as a kid but added when I created my account

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import NamedTuple, List, Dict, Any, Optional, Iterator, Union
from dataclasses import dataclass

TRAKT_BASE = "https://trakt.tv/"


# Note: I currently don't parse the following, because I don't have anything there
#
# collection
# comments
# lists
# recommendations
#
# TODO: add some stuff there are re-do an export so I can parse it


class Follow(NamedTuple):
    followed_at: datetime
    username: str


class SiteIds(NamedTuple):
    trakt_id: int
    trakt_slug: Optional[str]
    imdb_id: Optional[str]
    tmdb_id: Optional[int]
    tvdb_id: Optional[int]
    tvrage_id: Optional[int]


class Movie(NamedTuple):
    title: str
    year: int
    ids: SiteIds


class Show(NamedTuple):
    title: str
    year: int
    ids: SiteIds


class Episode(NamedTuple):
    title: str
    season: int
    episode: int
    ids: SiteIds
    show: Show


class Rating(NamedTuple):
    rated_at: datetime
    rating: int
    media_type: str


class Comment(NamedTuple):
    comment_id: int
    text: str
    created_at: datetime
    updated_at: datetime
    likes: int
    username: str


class TraktList(NamedTuple):
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    likes: int
    username: str


class Like(NamedTuple):
    liked_at: datetime
    media_type: str
    media_data: Union[TraktList, Comment]


class TraktExport(NamedTuple):
    username: str
    followers: List[Follow]
    following: List[Follow]
    likes: List[Like]
    stats: Dict[str, Any]
    settings: Dict[str, Any]


def _parse_trakt_datetime(ds: str) -> datetime:
    return datetime.astimezone(datetime.fromisoformat(ds.rstrip("Z")), tz=timezone.utc)


def _parse_users(d: Any) -> Iterator[Follow]:
    for u in d:
        yield Follow(
            followed_at=_parse_trakt_datetime(u["followed_at"]),
            username=u["user"]["username"],
        )


def _parse_comment(d: Any) -> Comment:
    return Comment(
        comment_id=d["id"],
        text=d["comment"],
        created_at=_parse_trakt_datetime(d["created_at"]),
        updated_at=_parse_trakt_datetime(d["updated_at"]),
        likes=d["likes"],
        username=d["user"]["username"],
    )


def _parse_trakt_list(d: Any) -> TraktList:
    return TraktList(
        name=d["name"],
        description=d["description"],
        created_at=_parse_trakt_datetime(d["created_at"]),
        updated_at=_parse_trakt_datetime(d["updated_at"]),
        likes=d["likes"],
        username=d["user"]["username"],
    )


def _parse_likes(d: Any) -> Iterator[Like]:
    for l in d:
        media_type = l["type"]
        media_data_raw = l[media_type]
        media_data: Union[TraktList, Comment]
        if media_type == "comment":
            media_data = _parse_comment(media_data_raw)
        else:
            media_data = _parse_trakt_list(media_data_raw)
        yield Like(
            liked_at=_parse_trakt_datetime(l["liked_at"]),
            media_type=media_type,
            media_data=media_data,
        )


def parse_export(p: Path) -> TraktExport:
    data: Any = json.loads(p.read_text())

    # need to parse 'ratings', 'history', 'watched' and 'watchlist'

    return TraktExport(
        username=data["username"],
        stats=data["stats"],
        settings=data["settings"],
        followers=list(_parse_users(data["followers"])),
        following=list(_parse_users(data["followers"])),
        likes=list(_parse_likes(data["likes"])),
    )
