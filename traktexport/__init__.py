from os import environ, path, makedirs
import platform
import trakt.core  # type: ignore[import]

# trakt is configured by modifying module-level variables
# set those up here, is setup before any other imports

operating_system = platform.system()
home_path = path.expanduser('~')
if operating_system in ("Linux", "Darwin"):
    data_dir = environ.get("XDG_DATA_HOME", path.join(home_path, ".local", "share"))
elif operating_system == "Windows":
    data_dir = path.join(home_path, '.traktexport')
    makedirs(data_dir, exist_ok=True)
else:
    data_dir = home_path
default_cfg_path = path.join(data_dir, "traktexport.json")
traktexport_cfg = environ.get("TRAKTEXPORT_CFG", default_cfg_path)
trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH
trakt.core.CONFIG_PATH = traktexport_cfg
