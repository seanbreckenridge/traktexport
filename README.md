# traktexport

Export your Movies, TV shows and ratings from [`Trakt.tv`](https://trakt.tv/)

This isn't meant to be used to re-import info back into Trakt or export to another site, its just meant to save all my data so I have it locally, and can do analysis or graph my history.

## Installation

Requires `python3.6+`

To install with pip, run:

    pip install 'git+https://github.com/seanbreckenridge/traktexport'

## Usage

This uses OAuth to authenticate with the Trakt API, see [here](https://pytrakt.readthedocs.io/en/latest/getstarted.html#oauth-auth) for more info.

This requires a manual setup the first time you use it, after which credentials are stored and this can run without any interaction.

### Setup

- Go to https://trakt.tv/oauth/applications and create a new application
- Use `urn:ietf:wg:oauth:2.0:oob` for the Redirect URI
- Run `traktexport auth yourtraktusername`
- Follow the instructions, pasting in your Client ID/Secret from the Trakt dashboard, going to the link and pasting the generated pin back into the terminal

Once you've done that, this saves OAuth refresh info in `${XDG_DATA_HOME:-$HOME/.local/share}/traktexport.json` (can overwrite location with the `TRAKTEXPORT_CFG` environment variable)

### Export

Then, to export all your ratings/movies/shows, run:

`traktexport export yourtraktusername > dump.json`

The results are printed to STDOUT, so `> dump.json` saves it to `dump.json`

### Inspect

[`traktexport.dal`](./traktexport/dal.py) includes some code I use to parse the resulting JSON file into Python objects so its easier to manipulate

```python
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
```

```
python3 -m traktexport inspect data.json
Use 'data' to interact with the parsed TraktExport object

In [1]: data.history[0]
Out[1]: HistoryEntry(history_id=7353545729, watched_at=datetime.datetime(2021, 3, 22, 13, 33, 24, tzinfo=datetime.timezone.utc), action='watch', media_type='movie', media_data=Movie(title='Rain Man', year=1988, ids=SiteIds(trakt_id=304, trakt_slug='rain-man-1988', imdb_id='tt0095953', tmdb_id=380, tvdb_id=None, tvrage_id=None)))

In [2]: len(data.history)
Out[2]: 16063

In [3]: data.stats["movies"]["plays"]
Out[3]: 1511
```

Note: Doesn't currently parse:

- collection
- comments
- lists
- recommendations

... because I don't have any of those on trakt
