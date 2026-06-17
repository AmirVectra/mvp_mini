from dataclasses import dataclass
from ..path_manager.set_global_paths import *
from ..path_manager.dir_utilities import DirectoryOPS as dir_ops


@dataclass
class SetOutputDirs(GlobalPaths):
    """Based on the env builds the output dir and the class is flexible to deal with
        different prog structures. Just need to provide dir name in build paths
        method"""

    # Define the variables want to use globally
    TOOL_FOLDER_PATH: Path| None = None
    TEMP_DATA_PATH: Path| None = None
    DIMENSION_DATABASES_PATH: Path| None = None
    DRAWINGS_PATH: Path| None = None
    DIMENSION_DATABASE_BACKUP_PATH: Path| None = None
    LOG_PATH: Path| None = None
    PART_SWEEP_DATA_BACKUP_PATH: Path| None = None
    PART_SWEEP_DATA_WITH_ADA_PATH: Path| None = None
    TEMP_UNIT_SWEEP_DATA_PATH: Path| None = None
    UNIT_DATABASES_PATH: Path| None = None
    UNIT_SWEEP_DATA_PATH: Path| None = None
    UNIT_SWEEP_DATA_BACKUP_PATH: Path| None = None
    UNPROCESSED_PARTS_PATH: Path| None = None

    # Can't be initialized later
    _tool_name = None

    def __post_init__(self):
        """Automatically invoked after object creation."""
        super().__init__()
        outDirData = FileHandler.load_json(self.local_paths["path_config"], "output_dir.json")
        self.buildPaths(outDirData)

    @property
    def tool_name(self):
        return self._tool_name

    def buildPaths(self, outDirData, dir_name="AUTO2D_OUTPUT_FILES"):
        env = outDirData["ENV"].upper()

        if env == "PROD":
            self.setProdPaths(out_dir_data=outDirData, dir_name=dir_name)
        elif env == "DEV":
            self.setDevPaths(out_dir_data=outDirData)

    def setProdPaths(self, out_dir_data, dir_name):
        # Currently AUTO2D_OUTPUT_FILES
        outputDirStruct = out_dir_data[dir_name]
        toolFileName = outputDirStruct["CONFIG_FOLDER"]["TOOL_FOLDER_PATH_FILE"]
        path = self.out_dir / outputDirStruct["CONFIG_FOLDER"]["NAME"] / toolFileName
        dir_ops.validate(path.parent)
        toolName = self.getToolName(path)

        # Iterate over the program output folders, validate and store the paths
        for key, value in outputDirStruct.items():
            if key != "CONFIG_FOLDER" and isinstance(value, str):  # skip config
                path = self.out_dir / value / toolName
                dir_ops.validate(path)
                setattr(self, f"{key}_PATH", path)
            elif key != "CONFIG_FOLDER" and isinstance(value, dict):
                values = list(value.values())
                path = self.out_dir / values[0]
                dir_ops.validate(path)
                setattr(self, f"{key}_PATH", path)

        # Create the mapped output folders (Python programs)
        mappedData = out_dir_data["MAP"]
        tempFolder = mappedData[""]
        tempFolderPath = self.out_dir / tempFolder
        # Iterate over the mapped folders, create and store the paths
        for key, value in mappedData.items():
            if key != "":
                path = tempFolderPath / toolName / key
                dir_ops.validate(path)
                # self._mapped_folder_paths[key] = path
                setattr(self, f"{key}_PATH", path)

    def setDevPaths(self, out_dir_data):
        # Fetch the log folder name
        LogFoldName = out_dir_data["LOG_FOLDER"]
        logFoldPath = self.out_dir / LogFoldName
        dir_ops.validate(logFoldPath)
        self.LOG_PATH = logFoldPath

    def getToolName(self, file_path):
        """
        Read the first non-empty line from a text file.
        """

        with open(file_path, "r", encoding="utf-8") as f:

            for line in f:
                value = line.strip()

                # Skip empty lines
                if not value:
                    continue

                # Handle both Windows and Linux style paths
                normalized = value.replace("\\", "/")

                # Path case
                if "/" in normalized:
                    self.TOOL_FOLDER_PATH = Path(normalized)
                    self._tool_name = self.TOOL_FOLDER_PATH.name

                # Plain tool name case
                else:
                    self.TOOL_FOLDER_PATH = None
                    self._tool_name = value

                return self._tool_name

        raise ValueError(f"No valid tool name found in '{file_path}'")

    # def fetchToolName(self, configData):
    #     """Read the tool_folder_path and returns the tool name"""
    #     path = self.out_dir / configData["NAME"]
    #     dir_ops.validate(path)
    #
    #     # check the presence of tool path if doesn't exist, through an error and exit
    #     toolPath = FileHandler.read(path, configData["TOOL_FOLDER_PATH_FILE"])
    #
    #     if not toolPath.strip():  # catches '' and whitespace-only
    #         lg.logger.error(f"There is no tool path provided in Tool_Folder_Path.txt")
    #         lg.loggerManager.saveLogsToFile(self.out_dir / "LOG" / "error.log")
    #         raise Warning("Tool_Folder_Path.txt is empty")
    #
    #     # Update the tool folder paths as root folder
    #     # Changes made here self.TOOL_FOLDER_PATH = Path(toolPath)
    #     self.TOOL_FOLDER_PATH = Path(toolPath.splitlines()[0].strip())
    #     self._tool_name = self.TOOL_FOLDER_PATH.name
    #
    #     return self.tool_name
