from .set_app_dir import *
from .set_output_dir import *
from . import logger_config as lg


@dataclass
class IO_Paths(LocalPaths):
    """Define the global variables and the values """


    INPUT_DRAWSHEETS_FILE_NAME='drawsheets_input.json'
    INPUT_DRAWVIEWS_FILE_NAME='drawviews_input.json'
    OUTPUT_DRAWVIEWS_FILE_NAME='drawviews_output.json'

    MVP_LITE_INPUT_DRAWSHEETS_FILE_PATH:Path | None=None
    MVP_LITE_INPUT_DRAWVIEWS_FILE_PATH:Path | None=None
    MVP_LITE_OUTPUT_DRAWVIEWS_FILE_PATH:Path | None=None



    # Objects initialized to attributes
    output_paths = SetOutputDirs()
    templates = Templates()
    references = References()
    program_prefix: str | None = None
    env: str | None = None

    _locked_attrs: set = None  # Internal tracker for frozen attributes
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IO_Paths, cls).__new__(cls)
        return cls._instance

    def __setattr__(self, key, value):
        # Ensure _locked_attrs always exists before we touch it
        if getattr(self, "_locked_attrs", None) is None:
            object.__setattr__(self, "_locked_attrs", set())

        # Always allow setting internal/private attributes
        if key.startswith("_"):
            object.__setattr__(self, key, value)
            return

        locked = self._locked_attrs
        current_value = getattr(self, key, None)

        # Prevent reassignment if locked
        if key in locked:
            raise AttributeError(f"Attribute '{key}' is frozen and cannot be reassigned.")

        # Allow assignment only once
        if current_value is None:
            object.__setattr__(self, key, value)
            locked.add(key)
        else:
            locked.add(key)
            raise AttributeError(f"Attribute '{key}' is frozen after first assignment.")

    def __init__(self):
        super().__init__()

    def setPaths(self, part_num):
        """
        Set program-specific file paths based on config and environment.
        Loads path configuration, resolves file suffixes, and assigns them
        as attributes for later access.
        """
        progIO_Data = FileHandler.load_json(self.local_paths["path_config"], "program_io.json")
        self.program_prefix = progIO_Data["PROGRAM_PREFIX"].lower()
        self.env = progIO_Data["ENV"].upper()
        dictSuffix = lg.loggerManager.getFileSuffixes()

        # Iterate over the file suffixes and create the status files
        for key, value in dictSuffix.items():
            fileName = f'{self.program_prefix}{value}'
            statusFolderPath = self.output_paths.LOG_PATH / part_num / fileName
            identifier = key.replace("SUFFIX", "PATH")

            if self.env == "PROD":
                # fPath = self.output_paths.TEMP_DATA_PATH / fileName
                fPath = self.output_paths.LOG_PATH / part_num / fileName
                setattr(self, identifier, fPath)
            else:
                setattr(self, identifier, statusFolderPath)

        return None





    def prepareIOPaths(self, part_name=''):
        """
        Form the folder and paths for the file which are fixed or known
        args: part_name : str
        """
        env_paths = {
            "PROD": {
                "out_dir": self.output_paths.TEMP_DATA_PATH
            },
            "DEV": {
                "out_dir": self.output_paths.out_dir
            },
        }
        paths = env_paths[self.env]

        partDir =  paths["out_dir"] / part_name


        self.MVP_LITE_INPUT_DRAWSHEETS_FILE_PATH = partDir / self.INPUT_DRAWSHEETS_FILE_NAME
        self.MVP_LITE_INPUT_DRAWVIEWS_FILE_PATH = partDir / self.INPUT_DRAWVIEWS_FILE_NAME
        self.MVP_LITE_OUTPUT_DRAWVIEWS_FILE_PATH = partDir / self.OUTPUT_DRAWVIEWS_FILE_NAME



        return self
