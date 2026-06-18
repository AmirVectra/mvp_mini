import copy
import sys
from pathlib import Path
from mvp_lite.path_manager import logger_config as lg

from mvp_lite.path_manager.set_io_file_paths import IO_Paths


def setCommonPaths(part_num):
    """Orchestrator to build paths
       returns: object of IO_Paths"""

    # Create the object
    objIOPaths = IO_Paths()
    objIOPaths.setPaths(part_num)
    # setProgramPaths(objIOPaths, part_num)
    objIOPaths.prepareIOPaths(part_num)
    lg.logger.info("*************** Set Paths: Ends ********************* \n")
    return objIOPaths