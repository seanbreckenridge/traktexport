# some DAL https://beepb00p.xyz/exports.html#dal
# code to parse the export into an ADT-like format
#
# this uses dataclasses sometimes so that I can possibly
# fix datetimes for items which I watched
# a *long* time ago, i.e. movies I watched
# as a kid but added when I created my account

import sys
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


class Season(NamedTuple):
    number: int
    ids: SiteIds
    show: Show


class Episode(NamedTuple):
    title: str
    season: int
    episode: int
    ids: SiteIds
    show: Show


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


class WatchListEntry(NamedTuple):
    listed_at: datetime
    listed_at_id: int
    media_type: str
    media_data: Union[Movie, Show]


@dataclass
class Rating:
    rated_at: datetime
    rating: int
    media_type: str
    media_data: Union[Movie, Show, Season, Episode]


@dataclass
class HistoryEntry:
    history_id: int
    watched_at: datetime
    action: str
    media_type: str
    media_data: Union[Movie, Episode]


class TraktExport(NamedTuple):
    username: str
    followers: List[Follow]
    following: List[Follow]
    likes: List[Like]
    stats: Dict[str, Any]
    settings: Dict[str, Any]
    watchlist: List[WatchListEntry]
    ratings: List[Rating]
    history: List[HistoryEntry]


def _parse_trakt_datetime(ds: str) -> datetime:
    return datetime.astimezone(datetime.fromisoformat(ds.rstrip("Z")), tz=timezone.utc)


def _parse_followers(d: Any) -> Iterator[Follow]:
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
        elif media_type == "list":
            media_data = _parse_trakt_list(media_data_raw)
        else:
            print(f"_parse_likes: No case to parse: {l}", file=sys.stderr)
            continue
        yield Like(
            liked_at=_parse_trakt_datetime(l["liked_at"]),
            media_type=media_type,
            media_data=media_data,
        )


def _parse_ids(d: Any) -> SiteIds:
    return SiteIds(
        trakt_id=d["trakt"],
        trakt_slug=d.get("slug"),
        imdb_id=d.get("imdb"),
        tmdb_id=d.get("tmdb"),
        tvdb_id=d.get("tvdb"),
        tvrage_id=d.get("tvrage"),
    )


def _parse_media(d: Any) -> Dict[str, Any]:
    return dict(
        title=d["title"],
        year=d["year"],
        ids=_parse_ids(d["ids"]),
    )


def _parse_movie(d: Any) -> Movie:
    return Movie(**_parse_media(d))


def _parse_show(d: Any) -> Show:
    return Show(**_parse_media(d))


def _parse_season(d: Any, show_data: Any) -> Season:
    return Season(
        number=d["number"],
        show=_parse_show(show_data),
        ids=_parse_ids(d["ids"]),
    )


def _parse_episode(d: Any, show_data: Any) -> Episode:
    return Episode(
        title=d["title"],
        season=d["season"],
        episode=d["number"],
        show=_parse_show(show_data),
        ids=_parse_ids(d["ids"]),
    )


def _parse_watchlist(d: Any) -> Iterator[WatchListEntry]:
    for i in d:
        media_type = i["type"]
        media_data_raw = i[media_type]
        media_data: Union[Movie, Show]
        if media_type == "movie":
            media_data = _parse_movie(media_data_raw)
        elif media_type == "show":
            media_data = _parse_show(media_data_raw)
        else:
            print(f"_parse_watchlist: No case to parse: {i}", file=sys.stderr)
            continue
        yield WatchListEntry(
            listed_at_id=i["id"],
            listed_at=_parse_trakt_datetime(i["listed_at"]),
            media_type=media_type,
            media_data=media_data,
        )


def _parse_ratings(d: Any) -> Iterator[Rating]:
    for i in d:
        media_type = i["type"]
        media_data_raw = i[media_type]
        media_data: Union[Movie, Show, Season, Episode]
        if media_type == "movie":
            media_data = _parse_movie(media_data_raw)
        elif media_type == "show":
            media_data = _parse_show(media_data_raw)
        elif media_type == "season":
            media_data = _parse_season(media_data_raw, i["show"])
        elif media_type == "episode":
            media_data = _parse_episode(media_data_raw, i["show"])
        else:
            print(f"_parse_ratings: No case to parse: {i}", file=sys.stderr)
            continue
        yield Rating(
            rated_at=_parse_trakt_datetime(i["rated_at"]),
            rating=i["rating"],
            media_type=media_type,
            media_data=media_data,
        )


def _parse_history(d: Any) -> Iterator[HistoryEntry]:
    for h in d:
        media_type = h["type"]
        media_data_raw = h[media_type]
        media_data: Union[Movie, Episode]
        if media_type == "movie":
            media_data = _parse_movie(media_data_raw)
        elif media_type == "episode":
            media_data = _parse_episode(media_data_raw, h["show"])
        else:
            print(f"_parse_history: No case to parse: {h}", file=sys.stderr)
            continue
        yield HistoryEntry(
            history_id=h["id"],
            watched_at=_parse_trakt_datetime(h["watched_at"]),
            action=h["action"],
            media_type=media_type,
            media_data=media_data,
        )


def parse_export(p: Path) -> TraktExport:
    data: Any = json.loads(p.read_text())

    # is there any point in parsing 'watched', if we're also parsing 'history'?
    # going to only parse history for now, since its better structured for parsing
    # and seems to have more info
    #
    # need to parse 'history'

    return TraktExport(
        username=data["username"],
        stats=data["stats"],
        settings=data["settings"],
        followers=list(_parse_followers(data["followers"])),
        following=list(_parse_followers(data["followers"])),
        likes=list(_parse_likes(data["likes"])),
        watchlist=list(_parse_watchlist(data["watchlist"])),
        ratings=list(_parse_ratings(data["ratings"])),
        history=list(_parse_history(data["history"])),
    )