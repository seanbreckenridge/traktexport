from typing import List, Set, Iterator

from .dal import (
    parse_export,
    FullTraktExport,
    PartialHistoryExport,
    TraktExport,
    HistoryEntry,
)


def read_and_merge_exports(files: List[str]) -> FullTraktExport:
    exp: List[TraktExport] = []
    for fl in files:
        with open(fl, "r") as f:
            exp.append(parse_export(f))

    return merge_exports(exp)


def _merge_history_entries(unsorted: List[TraktExport]) -> Iterator[HistoryEntry]:
    emitted: Set[int] = set()
    for u in unsorted:
        for hist in u.history:
            if hist.history_id in emitted:
                continue
            yield hist
            emitted.add(hist.history_id)


def merge_exports(unsorted: List[TraktExport]) -> FullTraktExport:
    full_exports: List[FullTraktExport] = []
    partial_exports: List[PartialHistoryExport] = []

    full_exports.sort(key=lambda e: len(e.history))
    partial_exports.sort(key=lambda e: len(e.history))

    # sort exports
    for u in unsorted:
        if isinstance(u, FullTraktExport):
            full_exports.append(u)
        else:
            partial_exports.append(u)

    latest_full_export = full_exports[-1]
    trakt_data = latest_full_export._asdict()
    hist = list(_merge_history_entries(unsorted))
    hist.sort(key=lambda h: h.watched_at, reverse=True)  # ordered to most recent first
    trakt_data["history"] = hist

    return FullTraktExport(**trakt_data)
