from dataclasses import dataclass

from mvp_lite.path_manager.set_global_paths import *
from mvp_lite.path_manager.dir_utilities import DirectoryOPS as dir_ops


@dataclass
class Templates(GlobalPaths):
    # Predefined attributes
    PSD_FILE_PREFIX: str | None = None
    DIMDB_FILE_PREFIX: str | None = None
    USD_FILE_PREFIX: str | None = None
    UNITDIMDB_FILE_PREFIX: str | None = None

    # Private attributes
    _root_path = {}

    def __post_init__(self):
        super().__init__()
        self.buildPaths()

    @property
    def root_path(self):
        return self._root_path

    def getName(self, app_data):
        return app_data["TEMPLATES_FOLDER"]["NAME"]

    def buildPaths(self):
        appData = FileHandler.load_json(self.local_paths["path_config"], "app_dir.json")
        rootFolder = self.getName(appData)  # here, templates act as root folder
        templatesData = appData["TEMPLATES_FOLDER"]
        env = appData["ENV"].upper()

        if env == "PROD":
            pathRoot = self.app_path / rootFolder
        elif env == "DEV":
            pathRoot = self.out_dir / rootFolder

        self._root_path = pathRoot
        # Create the directory if it doesn't exist
        dir_ops.validate(pathRoot)

        for key, value in templatesData.items():
            if key != "NAME":
                setattr(self, key, value)  # 👈 assign prefix to predefined attribute
        return None


@dataclass
class References(GlobalPaths):
    # Predefined attributes, add new folders as attributes from app_dir.json
    # will be updated as an attribute dynamically. Usage: references.new_attribute_name
    STD_NAAMS: Path | None = None
    STD_SHAPES: Path | None = None
    STD_SHAPE_ANGLE: Path | None = None
    STD_SHAPE_RT: Path | None = None
    STD_SHAPE_RT_NF: Path | None = None
    STD_SHAPE_CHANNEL: Path | None = None
    STD_SHAPE_UNISTRUT: Path | None = None
    STD_PURCH: Path | None = None
    STD_PURCH_JLR: Path | None = None

    def __post_init__(self):
        super().__init__()
        self.buildPaths()

    def getName(self, app_data):
        return app_data["REFERENCE_FOLDER"]["NAME"]

    def buildPaths(self):
        appData = FileHandler.load_json(self.local_paths["path_config"], "app_dir.json")
        rootFolder = self.getName(appData)
        refData = appData["REFERENCE_FOLDER"]
        env = appData["ENV"].upper()

        if env == "PROD":
            basePath = self.app_path
        elif env == "DEV":
            basePath = self.out_dir

        for key, value in refData.items():
            if key != "NAME" :
                # create folder path: base_path / NAME / <key without _PREFIX>
                fullpath = basePath / rootFolder / value
                # Create the directory if it doesn't exist
                dir_ops.validate(fullpath)
                setattr(self, key, fullpath)  # assign path to predefined attribute
        return None

