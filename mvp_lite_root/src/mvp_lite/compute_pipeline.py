
from drawsheet.deserialize import convertJSONToDrawSheetsList
from drawview.deserialize import convertJSONToDrawViewsDict
from drawview.serialize import convertDrawViewsToJSONFile

# for packaging
from mvp_lite.path_manager import set_paths as sp
from mvp_lite.mvp_core.scale_config import scaleConfigDict
from mvp_lite.mvp_core.run_mvp_lite import MVP_Lite
from mvp_lite.path_manager.file_handler import FileHandler
from mvp_lite.path_manager import logger_config as lg
from mvp_lite.path_manager.set_io_file_paths import IO_Paths


# # for developer
# from mvp_lite_root.src.mvp_lite.path_manager import set_paths as sp
# from mvp_lite_root.src.mvp_lite.mvp_core.scale_config import scaleConfigDict
# from mvp_lite_root.src.mvp_lite.mvp_core.run_mvp_lite import  MVP_Lite
# from mvp_lite_root.src.mvp_lite.path_manager.file_handler import FileHandler
# from mvp_lite_root.src.mvp_lite.path_manager import logger_config as lg
# from mvp_lite_root.src.mvp_lite.path_manager.set_io_file_paths import IO_Paths


DEFAULT_MVP_CONFIG = {'ctrViewMargin': 10}

def compute_Pipeline(part_num=None):
    if part_num is None:
        print("\033[91m part_num cannot be empty. Please provide existing part_num  \033[0m")

    """ Set the global paths """


    ioPaths = sp.setCommonPaths(part_num=part_num)

    # Check for the presence of status files
    # FileHandler.checkStatusFile(base_dir=ioPaths.LOG_FILE_PATH.parent, program_prefix=ioPaths.program_prefix)
    try:
        commonSP = IO_Paths()


        #---------------- STAGE-1 get all the required file paths. -----------------#

        drawViewsInputFilePath=commonSP.MVP_LITE_INPUT_DRAWVIEWS_FILE_PATH
        drawSheetsInputFilePath=commonSP.MVP_LITE_INPUT_DRAWSHEETS_FILE_PATH
        outputDrawViewsOutputFilePath=commonSP.MVP_LITE_OUTPUT_DRAWVIEWS_FILE_PATH


        #### get Drawview Objects from drawviews json file
        drawviewsIdObjectDict = convertJSONToDrawViewsDict(
            jsonPathOrData=str(drawViewsInputFilePath),
            scaleConfig=scaleConfigDict,
            applyInnerViewScale=False
        )
        if not drawviewsIdObjectDict:
            raise ValueError(
                f"No Drawview objects found in '{drawViewsInputFilePath}'."
            )

        # get First Drawsheet object from drawsheets json file
        sheetsObjectList = convertJSONToDrawSheetsList(
            jsonPathOrData=str(drawSheetsInputFilePath)
        )
        if not sheetsObjectList:
            raise ValueError(
                f"No Drawsheet objects found in '{drawSheetsInputFilePath}'."
            )
        #get first Sheet Object
        sheetObject=sheetsObjectList[0]

        # ----------- STAGE-2 CALL the CORE LOGIC that return positioned views --------#
        mvpLiteObject=MVP_Lite(drawsheetObject=sheetObject,viewsIdObjectDict=drawviewsIdObjectDict,
                                          scaleConfigDict=scaleConfigDict,MVP_Config=DEFAULT_MVP_CONFIG)

        updatedViewsIdObjectDict=mvpLiteObject.outputViewsIdObjectDict


        #---------------- STAGE-3 OUTPUT the updated Views -----------------------------#
        # convert updated Drawview Objects into json file.
        convertDrawViewsToJSONFile(
            viewsIdObjectDict=updatedViewsIdObjectDict,
            outputJSONFilePath=outputDrawViewsOutputFilePath,
            viewsAnchorTag="LB"
        )

        print("\033[92m MVP Lite | SUCCESS  \033[0m")

        # Generate the flag completion file
        FileHandler.write(ioPaths.COMPLETE_FILE_PATH)
    except:

        lg.logger.error("####### Exception occured  #######")
        FileHandler.write(ioPaths.COMPLETE_FILE_PATH)
        FileHandler.write(ioPaths.FAILED_FILE_PATH)
    return None



if __name__ == "__main__":
    compute_Pipeline(part_num='model2')
    pass
