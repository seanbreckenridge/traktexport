from os import environ, path, makedirs
import platform
import trakt.core  # type: ignore[import]

# trakt is configured by modifying module-level variables
# set those up here, is setup before any other imports

if "XDG_DATA_HOME" in environ:
    data_dir = environ["XDG_DATA_HOME"]
elif platform.system() == "Windows":
    data_dir = path.expanduser("~/.traktexport")
else:
    data_dir = path.expanduser("~/.local/share")
makedirs(data_dir, exist_ok=True)
default_cfg_path = path.join(data_dir, "traktexport.json")
traktexport_cfg = environ.get("TRAKTEXPORT_CFG", default_cfg_path)
trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH
trakt.core.CONFIG_PATH = traktexport_cfg
