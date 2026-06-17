import copy
from drawsheet.classes import DrawSheet
from drawsheet.sheet_config.factory import runSheetConfigAlgorithm
from drawview.views_cluster.cluster import ViewCluster
from drawview.views_cluster.ortho_projections_set import OrthographicProjectionSet
from vct_o_geom.vector import Vector

### for packaging
from .scale_config import scaleConfigDict
from ..path_manager.set_io_file_paths import IO_Paths
### for developer
# from mvp_lite_root.src.mvp_lite.mvp_core.scale_config import scaleConfigDict
# from mvp_lite_root.src.mvp_lite.path_manager.set_io_file_paths import IO_Paths

DISPLAY_WORKING_AREA_RECT_CONFIG={'displayWorkingArea': False}
INTERVIEW_PADDING=15
NOPS_VIEWS_ARRANGE_ROW_SPACE=15
CLUSTER_PAD=20
DEFAULT_MVP_CONFIG={'ctrViewMargin': 10}


class MVP_Lite:
    """
    Lite implementation of the Multi View Placement (MVP) algorithm.

    This implementation supports placement of a single Orthographic
    Projection Set (OPS) and one Non-OPS view. Views are scaled and
    stacked within the available working area of a draw sheet, and
    the final placement is centered inside the working area.
    """

    def __init__(self,drawsheetObject,viewsIdObjectDict,scaleConfigDict,MVP_Config=None):
        """
        Initialize MVP Lite input/output paths, configuration, and
        runtime objects.
        """
        if MVP_Config is None:
            self.MVP_Config=DEFAULT_MVP_CONFIG
        self.MVP_Config=MVP_Config

        if viewsIdObjectDict is None:
            raise ValueError("No Drawviews Objects Found")
        self.inputViewsIdObjectDict = viewsIdObjectDict

        if drawsheetObject is None:
            raise ValueError("No Drawsheets Objects Found")

        self.inputDrawsheetObject = drawsheetObject

        if scaleConfigDict is None:
            raise ValueError("No Scale Config Found")
        self.internalScaleConfig=scaleConfigDict

        self.outputViewsIdObjectDict=None

        self.runLogic()


    #
    # def getDrawSheetObject(self, drawsheetFilePath: Path):
    #     """
    #     Load and return the first DrawSheet object from a JSON file.
    #
    #     :param drawsheetFilePath: Path to the DrawSheets JSON file.
    #     :type drawsheetFilePath: Path
    #
    #     :returns: First DrawSheet object found in the input file.
    #     :rtype: DrawSheet
    #
    #     :raises ValueError:
    #         If the file path is None or no DrawSheet objects are found.
    #     """
    #     if drawsheetFilePath is None:
    #         raise ValueError("Drawsheets JSON path cannot be None.")
    #
    #     # Convert DrawSheet JSON into DrawSheet objects.
    #     sheetsObjectList = convertJSONToDrawSheetsList(
    #         jsonPathOrData=str(drawsheetFilePath)
    #     )
    #
    #     if not sheetsObjectList:
    #         raise ValueError(
    #             f"No Drawsheet objects found in '{drawsheetFilePath}'."
    #         )
    #
    #     return sheetsObjectList[0]
    #
    # def getDrawViewsIdObjectDict(self, drawviewsFilePath: Path, scaleConfigDict):
    #     """
    #     Load DrawView objects from a JSON file.
    #
    #     :param drawviewsFilePath: Path to the DrawViews JSON file.
    #     :type drawviewsFilePath: Path
    #
    #     :param scaleConfigDict: View scaling configuration.
    #     :type scaleConfigDict: dict
    #
    #     :returns:
    #         Dictionary mapping view IDs to DrawView objects.
    #     :rtype: dict
    #
    #     :raises ValueError:
    #         If the file path is None or no DrawView objects are found.
    #     """
    #     if drawviewsFilePath is None:
    #         raise ValueError("DrawViews JSON file path cannot be None.")
    #
    #     # Convert DrawView JSON into view objects.
    #     drawviewsIdObjectDict = convertJSONToDrawViewsDict(
    #         jsonPathOrData=str(drawviewsFilePath),
    #         scaleConfig=scaleConfigDict,
    #         applyInnerViewScale=False
    #     )
    #
    #     if not drawviewsIdObjectDict:
    #         raise ValueError(
    #             f"No Drawview objects found in '{drawviewsFilePath}'."
    #         )
    #
    #     return drawviewsIdObjectDict

    def getRectangleWorkingArea(self,drawsheetObject:DrawSheet):
        """
        Compute and return the available working area of the draw sheet.

        :returns: Working area rectangle.
        :rtype: Rect2D

        :raises ValueError:
            If the input sheet object is not initialized.
        """
        if drawsheetObject is None:
            raise ValueError(
                "DrawSheet object is needed for working area computation."
            )


        # Execute Working Area Rectangle (WAR) algorithm.
        sheetConfigAlgo = runSheetConfigAlgorithm(
            algorithmName="WAR",
            drawSheet=drawsheetObject,
            config={'displayWorkingArea': False}
        )

        workingAreaRect2D = sheetConfigAlgo.getWorkingArea()
        return workingAreaRect2D

    def stackViewsCentrally_MSIL(self, viewsIdObjectDict):
        """

        Stack OPS and Non-OPS views and position them at the center
        of the draw sheet working area.

        :param viewsIdObjectDict:
            Dictionary containing input view objects.
        :type viewsIdObjectDict: dict

        :returns:
            Dictionary containing centrally positioned view objects.
        :rtype: dict
        """
        workingAreaRect = self.getRectangleWorkingArea()
        workingAreaCTRCoords = workingAreaRect.basis_point("CTR")

        # Arrange OPS views according to orthographic projection rules.
        OPS = OrthographicProjectionSet(
            viewsIdObjectDict=viewsIdObjectDict,
            MVP_Config=self.MVP_Config
        )
        viewsIdObjectDict_ForOPS = OPS.viewsIdObjectDict

        # Extract only the first Non-OPS view.
        nonOPSViews = {}

        for viewId, viewObject in viewsIdObjectDict.items():
            if viewObject.rel_order not in ["L", "R", "T", "B", "CTR"]:
                if nonOPSViews:
                    print("Considering only one Non-OPS View")
                    break
                nonOPSViews[viewId] = viewObject

        # Create cluster for OPS views.
        viewClusterOPS = ViewCluster(
            viewsIdObjectDict=viewsIdObjectDict_ForOPS,
            setClusterLBAtOrigin=True,
            clust_pad=10
        )

        OPSClusterRBCoords = (
            viewClusterOPS.boundingRectangle().basis_point("RB")
        )
        allViewsIdObjectDict = {}
        # Merge OPS and Non-OPS views into a single cluster.

        # verify whether NOPS is present then form cluster.
        if nonOPSViews:
            # Position Non-OPS view above the OPS cluster.
            nonOPSViewCluster = ViewCluster(
                viewsIdObjectDict=nonOPSViews,
                setClusterLBAtOrigin=True
            )

            nonOPSViewCluster.repositionCluster(
                clusterAnchorPoint=OPSClusterRBCoords,
                clusterAnchorTag="RT"
            )

            if nonOPSViews:
                allViewsIdObjectDict |= nonOPSViewCluster.viewsIdObjectDict



        allViewsIdObjectDict |= viewClusterOPS.viewsIdObjectDict

        hybridViewCluster = ViewCluster(
            viewsIdObjectDict=allViewsIdObjectDict,
            setClusterLBAtOrigin=False
        )



        # Center the complete cluster inside the working area.
        hybridViewCluster.repositionCluster(
            clusterAnchorTag='CTR',
            clusterAnchorPoint=workingAreaCTRCoords
        )

        return copy.deepcopy(hybridViewCluster.viewsIdObjectDict)

    def arrangeViewsInRowStack(
            self,
            viewsIdObjectDict,
            cotnainerWidth,
            cotnainerHeight,
            interViewSpace=0,
            rowSpace=0,
    ):
        """
        Arrange views left-to-right within a container.
        When a row is full, start a new row below it.

        Rows are created from TOP to BOTTOM.
        """

        current_x = 0
        current_y = cotnainerHeight
        current_row_height = 0

        for viewId, view in viewsIdObjectDict.items():

            rect = view.boundingRectangle()

            view_width = rect.L1
            view_height = rect.L2

            # View itself cannot fit horizontally
            if view_width > cotnainerWidth:
                raise ValueError(
                    f"View '{viewId}' width ({view_width}) "
                    f"exceeds container width ({cotnainerWidth})."
                )

            # current_x is always the next insertion position
            required_width = current_x + view_width

            # Start a new row if needed
            if required_width > cotnainerWidth:
                current_y -= current_row_height + rowSpace
                current_x = 0
                current_row_height = 0

            view_lb_y = current_y - view_height

            # Check container height
            if view_lb_y < 0:
                print(
                    "\033[91m Cannot stack NOPS views within the given space.\033[0m"
                )
                return False

            # Position view
            view.repositionBRectView(
                "LB",
                Vector(current_x, view_lb_y)
            )



            # Update tallest view in current row
            current_row_height = max(
                current_row_height,
                view_height
            )

            # Advance insertion point for next view
            current_x += view_width + interViewSpace


        return viewsIdObjectDict


    def stackViewsCentrally_HCL(self, viewsIdObjectDict):
        """

        Stack OPS and Non-OPS views and position them at the center
        of the draw sheet working area.

        :param viewsIdObjectDict:
            Dictionary containing input view objects.
        :type viewsIdObjectDict: dict

        :returns:
            Dictionary containing centrally positioned view objects.
        :rtype: dict
        """
        workingAreaRect = self.getRectangleWorkingArea(drawsheetObject=self.inputDrawsheetObject)
        workingAreaCTRCoords = workingAreaRect.basis_point("CTR")
        # Extract only the first Non-OPS view.
        nonOPSViews = {}
        allViewsIdObjectDict = {}

        viewsIdObjectDict_ForOPS=None
        # if NO OPS views are found, those will be considered as rejected views
        # this rejected views will be part NOPS views.

        opsViews,rejectedViews=OrthographicProjectionSet.filterOPSViews(viewsIdObjectDict=viewsIdObjectDict)

        # Arrange OPS views according to orthographic projection rules.
        if  opsViews:
            OPS = OrthographicProjectionSet(
                viewsIdObjectDict=opsViews,
                MVP_Config=self.MVP_Config
            )
            viewsIdObjectDict_ForOPS = OPS.viewsIdObjectDict
            print("\033[92m OPS views are successfully stacked. \033[0m")
        else:
            print("\033[91m No OPS views Found \033[0m")

        if rejectedViews:
            # just add this rejected views as NOPS views
            nonOPSViews|=rejectedViews



        ### filter NOPS views
        for viewId, viewObject in viewsIdObjectDict.items():
            # print(f'{viewId=} {viewObject.rel_order=}')
            if viewObject.rel_order not in ["L", "R", "T", "B", "CTR"] or viewObject.ctr_view is None:
                nonOPSViews[viewId] = viewObject

        if nonOPSViews is None:
            print("\033[93m NOPS views Not Found \033[0m")

        workingAreaRectangle = self.getRectangleWorkingArea(drawsheetObject=self.inputDrawsheetObject)

        availableWidthForRowStack = workingAreaRectangle.L1
        availableHeightForRowStack = workingAreaRectangle.L2


        mainOPSClusterViewsLBCoords=None



        # Create cluster for OPS views.
        if viewsIdObjectDict_ForOPS:
            mainOPSClusterViews = ViewCluster(
                viewsIdObjectDict=viewsIdObjectDict_ForOPS,
                setClusterLBAtOrigin=True,
                clust_pad=CLUSTER_PAD
            )

            mainOPSClusterViewsLBCoords = (
                mainOPSClusterViews.boundingRectangle().basis_point("LB")
            )

            # append the main OPS cluster to hybrid cluster
            allViewsIdObjectDict |= mainOPSClusterViews.viewsIdObjectDict

            availableHeightForRowStack = workingAreaRectangle.L2 - mainOPSClusterViews.L2


        rowStackedViewsIdObjectDict = self.arrangeViewsInRowStack(viewsIdObjectDict=nonOPSViews,
                                                                  cotnainerWidth=availableWidthForRowStack,
                                                                  cotnainerHeight=availableHeightForRowStack,
                                                                  rowSpace=INTERVIEW_PADDING,
                                                                  interViewSpace=NOPS_VIEWS_ARRANGE_ROW_SPACE
                                                                  )


        # check if all the NOPS views are able to fit, form the cluster

        if nonOPSViews and rowStackedViewsIdObjectDict:
            # Position Non-OPS view above the OPS cluster.
            nonOPSViewCluster = ViewCluster(
                viewsIdObjectDict=rowStackedViewsIdObjectDict,
                setClusterLBAtOrigin=True
            )
            targetClusterViewsLBCoords = workingAreaRect.basis_point("LB") if mainOPSClusterViewsLBCoords is None else mainOPSClusterViewsLBCoords
            nonOPSViewCluster.repositionCluster(
                clusterAnchorPoint=targetClusterViewsLBCoords,
                clusterAnchorTag="LT"
            )
            print("\033[92m NOPS views are successfully stacked. \033[0m")
            # append that NOPS cluster to hybrid cluster

            allViewsIdObjectDict |= nonOPSViewCluster.viewsIdObjectDict




        hybridViewCluster = ViewCluster(
            viewsIdObjectDict=allViewsIdObjectDict,
            setClusterLBAtOrigin=False
        )

        # Center the complete cluster inside the working area.
        hybridViewCluster.repositionCluster(
            clusterAnchorTag='CTR',
            clusterAnchorPoint=workingAreaCTRCoords
        )


        return copy.deepcopy(hybridViewCluster.viewsIdObjectDict)

    def stackViewsCentrally(self, viewsIdObjectDict):
        return self.stackViewsCentrally_HCL(viewsIdObjectDict)


    def scaleUpViews(self, viewsIdObjectDict):
        """
        Apply the next available scale to all views.

        :param viewsIdObjectDict:
            Dictionary containing view objects.
        :type viewsIdObjectDict: dict

        :returns:
            Scaled view dictionary if all views can be scaled;
            otherwise False.
        :rtype: dict | bool
        """
        # Work on a copy to avoid modifying the input collection.
        viewsIdObjectDictCopy = copy.deepcopy(viewsIdObjectDict)

        # Scale each view to its next available scale.
        for viewId, viewObject in viewsIdObjectDictCopy.items():
            if viewObject.canNextScale():
                viewObject.applyNextScale()
            else:
                return False

        return viewsIdObjectDictCopy

    def runLogic(self):

        # Scale views.
        scaledViewsIdObject = self.scaleUpViews(
            viewsIdObjectDict=self.inputViewsIdObjectDict
        )

        # Stack the views centrally.
        updatedViewsIdObject = self.stackViewsCentrally(
            viewsIdObjectDict=scaledViewsIdObject
        )

        self.outputViewsIdObjectDict=updatedViewsIdObject





