from os import environ, path

import trakt.core  # type: ignore[import]

# trakt is configured by modifying module-level variables
# set those up here, is setup before any other imports

data_dir = environ.get("XDG_DATA_HOME", path.join(environ["HOME"], ".local", "share"))
default_cfg_path = path.join(data_dir, "traktexport.json")
traktexport_cfg = environ.get("TRAKTEXPORT_CFG", default_cfg_path)
trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH
trakt.core.CONFIG_PATH = traktexport_cfg
