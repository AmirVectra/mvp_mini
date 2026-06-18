from mvp_lite.path_manager.set_local_paths import LocalPaths
from mvp_lite.path_manager.file_handler import *


class GlobalPaths(LocalPaths):
    """Set the global paths: app dir, output dir, and initialize logger."""

    # Folder name constant — change once here if it ever renames
    _CONFIG_FOLDER = "Config"

    # Valid environments — extend here if staging/uat added later
    _VALID_ENVS = {"DEV", "PROD"}

    def __init__(self):
        super().__init__()
        self._app_path: Path | None = None
        self._out_dir: Path | None = None
        self._env: str | None = None
        self._setup_global_paths()

    @property
    def app_path(self) -> Path:
        return self._app_path

    @property
    def out_dir(self) -> Path:
        return self._out_dir

    @property
    def env(self) -> str:
        """Expose the resolved environment (DEV / PROD) to callers."""
        return self._env

    def _setup_global_paths(self) -> None:
        """Resolve output paths and initialize the logger."""
        path_config = self._get_local_path("path_config")
        app_data    = FileHandler.load_json(path_config, "app_dir.json")

        self._env      = self._resolve_env(app_data)
        self._app_path = self._resolve_app_path(app_data)
        config_path    = self._resolve_config_path(path_config)
        self._out_dir  = self._resolve_out_dir(config_path)

        self._init_logger(path_config)


    def _get_local_path(self, key: str) -> Path:
        """
        Safe lookup into local_paths with a clear error if key is missing.
        Prevents silent KeyError from misconfigured path config.
        """
        if key not in self.local_paths:
            raise KeyError(
                f"'{key}' not found in local_paths. "
                f"Available keys: {list(self.local_paths.keys())}"
            )
        return Path(self.local_paths[key])

    def _resolve_env(self, app_data: dict) -> str:
        """
        Extract and validate ENV from app_dir.json.
        Fails fast with a clear message instead of silently falling through.
        """
        env = app_data.get("ENV", "").strip().upper()
        if env not in self._VALID_ENVS:
            raise ValueError(
                f"Unknown ENV '{env}' in app_dir.json. "
                f"Expected one of: {self._VALID_ENVS}"
            )
        return env

    @staticmethod
    def _resolve_app_path(app_data: dict) -> Path:
        """
        Convert APP_PATH from app_dir.json to a proper Path object.

        Handles cross-platform path strings:
        - Windows paths stored as strings (C:\\Users\\...) work on Windows
        - Posix paths (/home/user/...) work on Linux/Mac
        - Warns if path doesn't exist on the current machine
        """
        raw = app_data.get("APP_PATH", "").strip()
        if not raw:
            raise ValueError("APP_PATH is missing or empty in app_dir.json")

        # Normalize path separators regardless of OS where it was saved
        path = Path(raw.replace("\\", "/"))

        if not path.exists():
            lg.logger.warning(
                f"APP_PATH does not exist on this machine: {path}. "
                f"Proceeding — may fail later if accessed."
            )
        return path

    def _resolve_config_path(self, path_config: Path) -> Path:
        """
        Return the config directory based on ENV.
        Uses Path joining (OS independent) instead of string concatenation.
        """
        if self._env == "DEV":
            return self._get_local_path("config")

        elif self._env == "PROD":
            # _CONFIG_FOLDER constant replaces hardcoded "Config" string
            return self._app_path / self._CONFIG_FOLDER

    def _resolve_out_dir(self, config_path: Path) -> Path:
        """
        Read Output_Folder_Path.txt and return as Path.
        Single place to do this — eliminates the DEV/PROD duplication.
        """
        raw = FileHandler.read(config_path, "Output_Folder_Path.txt").strip()
        if not raw:
            raise ValueError(
                f"Output_Folder_Path.txt is empty under: {config_path}"
            )

        # Same cross-platform normalization as APP_PATH
        return Path(raw.replace("\\", "/"))

    def _init_logger(self, path_config: Path) -> None:
        """Initialize logger — separated from path logic for clarity."""
        lg.createLoggerObj(path_config, env=self._env)
        lg.logger.info(f"******** Set paths : Starts [{self._env}] ******")
