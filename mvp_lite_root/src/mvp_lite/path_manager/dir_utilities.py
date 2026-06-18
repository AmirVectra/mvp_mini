import os
import shutil
from pathlib import Path
from mvp_lite.path_manager import logger_config as lg


class DirectoryOPS:

    @staticmethod
    def create(dir_paths):
        """Create directories if they do not exist."""
        # Normalize to list
        if isinstance(dir_paths, (str, Path)):
            dir_paths = [dir_paths]

        for path in dir_paths:
            p = Path(path)
            try:
                p.mkdir(parents=True, exist_ok=True)
                # lg.info(f"Directory ensured: {p}")
            except Exception as e:
                lg.logger.error(f"Failed to create directory '{p}': {e}")
                raise
            # for dir_path in dir_paths:
            # if not os.path.exists(dir_path):
            #     # lg.logger.info(f"{dir_path} does not exist, creating it...")
            #     os.makedirs(dir_path)
            # else:
            #     pass
            #     # lg.logger.info(f"Dir already exists: {dir_path}")

    @staticmethod
    def delete(dir_path):
        p = Path(dir_path)

        if not p.exists():
            return  # Nothing to delete

        if not p.is_dir():
            raise ValueError(f"Cannot delete: Not a directory -> {p}")

        try:
            shutil.rmtree(p)
            # lg.info(f"Deleted directory: {p}")
        except Exception as e:
            lg.logger.error(f"Failed to delete directory '{p}': {e}")
            raise

    @staticmethod
    def validate(args, validate_contents=False):
        """
        Validate directories. Creates them if they don't exist.

        Args:
            args: Either a single path, or a dict with "output_paths" (when validate_contents=True).
            validate_contents (bool): If True, validate all paths in args["output_paths"].
        """

        # Case 1: Single path validation
        if not validate_contents:
            if not isinstance(args, (str, Path)):
                raise TypeError(
                    "Expected 'args' to be a single path (str | Path) when validate_contents=False"
                )
            lg.logger.info(f"Creating/validating directory: {args}")
            DirectoryOPS.create(args)
            return

        # Case 2: Validate all output paths inside the dict
        if not isinstance(args, dict):
            raise TypeError("args must be a dict when validate_contents=True")

        output_paths = args.get("output_paths")
        if output_paths is None:
            raise KeyError("'output_paths' key missing in args when validate_contents=True")

        if not isinstance(output_paths, dict):
            raise TypeError("'output_paths' must be a dict containing paths")

        paths = list(output_paths.values())
        DirectoryOPS.create(paths)


        # if not validate_contents:
        #     lg.logger.info(f"Creating the directory: {args}")
        #     DirectoryOPS.create(args)
        # else:
        #     output_paths = list(args["output_paths"].values())
        #     DirectoryOPS.create(output_paths)

    @staticmethod
    def getPathUpToWord(basePath: str, searchWord: str) -> str:
        """
        Returns the path up to and including the directory that contains `searchWord`.
        Example:
            basePath = "C:/Users/vct/my_project_root/src/module/file.py"
            searchWord = "_project_root"
            -> "C:/Users/vct/my_project_root"
        """
        # Normalize the path
        basePath = os.path.normpath(basePath)

        # Split into components
        dirList = basePath.split(os.sep)

        # Look for searchWord as substring inside components
        idxSearchWord = None
        for i, d in enumerate(dirList):
            if searchWord in d:
                idxSearchWord = i
                break

        if idxSearchWord is None:
            raise ValueError(f"word '{searchWord}' not found in path '{basePath}'")

        # Slice up to and including that part
        finalDirList = dirList[:idxSearchWord + 1]

        # Join back
        return os.sep.join(finalDirList)

    @staticmethod
    def list_items(
        folder: Path,
        include_files: bool = True,
        include_folders: bool = True,
    ) -> list[str]:
        """
        Return sorted names of items inside `folder`.

        Args:
            folder:          Path to the target directory.
            include_files:   If True, include file names.
            include_folders: If True, include subdirectory names.

        Raises:
            NotADirectoryError: if `folder` is not an existing directory.
        """
        folder = Path(folder)
        if not folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder}")

        results = []
        for item in folder.iterdir():
            if item.is_file() and include_files:
                results.append(item.name)
            elif item.is_dir() and include_folders:
                results.append(item.name)

        return sorted(results)
