from pathlib import Path


class LocalPaths:
    # prog_prefix_level : Path
    PATH_CONFIG_DIR = "path_config"
    CONFIG_DIR = "Config"  # define app level config folder

    def __init__(self):
        self._local_paths = {}
        self.setupLocalPaths()

    @property
    def local_paths(self):
        return self._local_paths

    @property
    def config_dir(self):
        return self._local_paths["config"]

    def setupLocalPaths(self):

        # Get the directory of the current script i.e. path_manager
        current_dir = Path(__file__).resolve().parent

        # Program prefix level lies one level above the current dir
        dirProject_Prefix = current_dir.parents[0]

        # Construct the path to the path_config directory
        pathConfig = dirProject_Prefix / self.PATH_CONFIG_DIR

        if not pathConfig.exists():
            raise FileNotFoundError(f"Path config directory not found: {pathConfig}")

        # Construct the path to the path_config directory
        config_dir = dirProject_Prefix / self.CONFIG_DIR

        if not config_dir:
            raise FileNotFoundError(f"Config directory not found: {config_dir}")

        # Initialize the attributes
        self._local_paths["prog_prefix_level"] = dirProject_Prefix
        self._local_paths["path_config"] = pathConfig
        self._local_paths["config"] = config_dir

        # setattr(self, "PROG_PREFIX_LVL", dirProject_Prefix)
        # setattr(self, "PATH_CONFIG", pathConfig)
        # setattr(self, "CONFIG", config_dir)
