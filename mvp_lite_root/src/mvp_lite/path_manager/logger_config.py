import logging
import logging.config
import io
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
import yaml
import atexit

logger = None
loggerManager = None


class LoggerManager:
    def __init__(self, configPath, environment: str = "DEV"):
        """
        Initialize LoggerManager:
          - Load logger configuration
          - Setup in-memory handler
          - Attach handler to environment logger
          - Register exit hook to flush logs
        """
        # --- Environment setup ---
        self._env = environment
        self._logFilePath: Path | None = None
        self._errorLogFilePath: Path | None = None
        self._start_time = time.time()  # ⏱ Capture program start time
        self._has_errors = False
        self._errorLogStream = io.StringIO()

        # --- Load logger config from YAML ---
        config_file = configPath / "logger_config.yaml"
        with open(config_file, "r") as f:
            self._config = yaml.safe_load(f)
        logging.config.dictConfig(self._config)

        # --- In-memory log handler (stores logs in StringIO) ---
        self._logStream = io.StringIO()
        memory_handler = logging.StreamHandler(self._logStream)

        formatter = logging.Formatter(
            '[%(levelname)s] [%(asctime)s] [%(module)s] - %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S'
        )
        memory_handler.setFormatter(formatter)

        error_handler = logging.StreamHandler(self._errorLogStream)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # --- Attach handler to environment-specific logger ---
        self._logger = logging.getLogger(self._env)
        self._logger.addHandler(memory_handler)
        self._logger.addHandler(ErrorTrackerHandler(self))

        # --- Ensure logs are flushed to file at program exit ---
        atexit.register(self._flushLogsOnExit)

    def getLogger(self) -> logging.Logger:
        return logging.getLogger(self._env)

    def getFileSuffixes(self) -> dict:
        return self._config.get("file_suffixes", {})

    def getConfigValue(self, key: str, default=None):
        return self._config.get(key, default)

    def saveLogsToFile(self, filePath):
        """Write all collected logs to the given file path at the end."""
        # append total runtime at end
        # Todo: Change 'a' to 'w' if wants log to be overwritten everytime
        with open(filePath, "a") as f:
            f.write(self._logStream.getvalue())

            elapsed = time.time() - self._start_time
            f.write(f"\n[INFO] Total execution time: {elapsed:.2f} seconds\n")

    def saveErrorLogsToFile(self, filePath: Path):
        """Write only ERROR and CRITICAL logs."""

        error_logs = self._errorLogStream.getvalue()

        # Generate file only when errors exist
        if not error_logs.strip():
            return

        with open(filePath, "a", encoding="utf-8") as f:
            f.write(error_logs)

    def setLogFilePath(self, infoPath: Path, errorPath: Path):
        """Update or assign the log file path anytime in the flow."""
        self._logFilePath = infoPath
        self._errorLogFilePath = errorPath

        formatter = logging.Formatter(
            '[%(levelname)s] [%(asctime)s] [%(module)s] - %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S'
        )

        # --- Info rotating handler ---
        info_handler = RotatingFileHandler(
            infoPath,
            mode='a',
            maxBytes= 1024 * 1024,  # 2 MB
            # maxBytes=2 * 1024 * 1024,  # 2 MB
            backupCount=2,
            encoding="utf-8"
        )
        info_handler.setLevel(logging.DEBUG)
        info_handler.setFormatter(formatter)
        self._logger.addHandler(info_handler)


    def _flushLogsOnExit(self):
        """Internal function bound to atexit."""
        if self._logFilePath:
            self.saveLogsToFile(self._logFilePath)

        if self._has_errors and self._errorLogFilePath:
            self.saveErrorLogsToFile(self._errorLogFilePath)


def createLoggerObj(path, env):
    """Function to initialize create obj and initialize global variables"""
    global logger, loggerManager
    loggerManager = LoggerManager(configPath=path, environment=env)
    logger = loggerManager.getLogger()

    return loggerManager


class ErrorTrackerHandler(logging.Handler):

    def __init__(self, manager):
        super().__init__(level=logging.ERROR)
        self.manager = manager

    def emit(self, record):
        self.manager._has_errors = True
