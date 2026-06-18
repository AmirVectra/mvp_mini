import json
import yaml
import os
import pandas as pd
from pathlib import Path
from mvp_lite.path_manager import logger_config as lg


class FileHandler:
    @staticmethod
    def _full_path(base_dir: Path, filename: str = "") -> Path:
        """
        Resolve the final file path.
        - If filename is given: joins base_dir / filename.
        - If filename is empty: treats base_dir as the full path already.
        """
        base_dir = Path(base_dir)
        return base_dir / filename if filename else base_dir

    @staticmethod
    def ensure_dir(path: Path) -> None:
        """Create parent directories for a path if they don't exist."""
        os.makedirs(Path(path).parent, exist_ok=True)

    # ─── Text / binary ─────────────────────────────────────────────────

    @staticmethod
    def read(base_dir: Path, filename: str = "", mode: str = "r", encoding: str = "utf-8") -> str:
        """
        Read file contents as string.

        Usage:
            FileHandler.read(Path("data/"), "config.txt")
            FileHandler.read(Path("data/config.txt"))
        """
        path = FileHandler._full_path(base_dir, filename)
        if not path.is_file():
            lg.logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, mode, encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write(
            base_dir: Path,
            filename: str = "",
            data: str = "",
            mode: str = "w",
            encoding: str = "utf-8",
    ) -> None:
        """
        Write string data to file, creating parent dirs as needed.

        Usage:
            FileHandler.write(Path("data/"), "output.txt", "hello")
            FileHandler.write(Path("data/output.txt"), data="hello")
        """
        path = FileHandler._full_path(base_dir, filename)
        FileHandler.ensure_dir(path)

        with open(path, mode, encoding=encoding) as f:
            f.write(data or "")

    # ─── CSV / Parquet ─────────────────────────────────────────────────

    @staticmethod
    def read_csv(
            base_dir: Path,
            filename: str = "",
            encoding: str = "utf-8",
    ) -> pd.DataFrame:
        """
        Read CSV into a DataFrame.

        Usage:
            FileHandler.read_csv(Path("data/"), "parts.csv")
            FileHandler.read_csv(Path("data/parts.csv"))
        """
        path = FileHandler._full_path(base_dir, filename)
        if not path.is_file():
            lg.logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        return pd.read_csv(path, encoding=encoding)

    @staticmethod
    def load_parquet(
            base_dir: Path,
            filename: str = "",
            columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Read a Parquet file into a DataFrame.

        Args:
            columns: Optional list of columns to load (projection pushdown).

        Usage:
            FileHandler.load_parquet(Path("data/"), "features.parquet")
            FileHandler.load_parquet(Path("data/features.parquet"))
            FileHandler.load_parquet(Path("data/features.parquet"), columns=["face_id", "area"])
        """
        path = FileHandler._full_path(base_dir, filename)
        if not path.is_file():
            raise FileNotFoundError(f"Parquet file not found: {path}")

        return pd.read_parquet(path, columns=columns)

    # ─── JSON ──────────────────────────────────────────────────────────

    @staticmethod
    def load_json(
            base_dir: Path,
            filename: str = "",
            encoding: str = "utf-8",
    ) -> dict:
        """
        Load JSON file and return as dict.

        Usage:
            FileHandler.load_json(Path("config/"), "rules.json")
            FileHandler.load_json(Path("config/rules.json"))
        """
        path = FileHandler._full_path(base_dir, filename)
        if not path.is_file():
            raise FileNotFoundError(f"JSON file not found: {path}")

        with open(path, "r", encoding=encoding) as f:
            return json.load(f)

    @staticmethod
    def save_json(
            base_dir: Path,
            filename: str = "",
            data: dict = None,
            indent: int = 4,
            encoding: str = "utf-8",
    ) -> None:
        """
        Save dict as JSON file, creating parent dirs as needed.

        Usage:
            FileHandler.save_json(Path("output/"), "result.json", data=my_dict)
            FileHandler.save_json(Path("output/result.json"), data=my_dict)
        """
        path = FileHandler._full_path(base_dir, filename)
        FileHandler.ensure_dir(path)

        with open(path, "w", encoding=encoding) as f:
            json.dump(data or {}, f, indent=indent)

    # ─── YAML ──────────────────────────────────────────────────────────

    @staticmethod
    def load_yml(
            base_dir: Path,
            filename: str = "",
            encoding: str = "utf-8",
    ) -> dict:
        """
        Load YAML file and return as dict.

        Usage:
            FileHandler.load_yml(Path("config/"), "settings.yml")
            FileHandler.load_yml(Path("config/settings.yml"))
        """
        path = FileHandler._full_path(base_dir, filename)
        if not path.is_file():
            raise FileNotFoundError(f"YAML file not found: {path}")

        with open(path, "r", encoding=encoding) as f:
            return yaml.safe_load(f)

    @staticmethod
    def save_yml(
            base_dir: Path,
            filename: str = "",
            data: dict = None,
            encoding: str = "utf-8",
    ) -> None:
        """
        Save dict as YAML file, creating parent dirs as needed.

        Usage:
            FileHandler.save_yml(Path("config/"), "settings.yml", data=my_dict)
            FileHandler.save_yml(Path("config/settings.yml"), data=my_dict)
        """
        path = FileHandler._full_path(base_dir, filename)
        FileHandler.ensure_dir(path)

        with open(path, "w", encoding=encoding) as f:
            yaml.dump(data or {}, f, allow_unicode=True, default_flow_style=False)

    @staticmethod
    def checkStatusFile(base_dir: Path, program_prefix: str) -> None:
        SUFFIXES = ["_complete.txt", "_failure.txt"]

        for suffix in SUFFIXES:
            file_path = base_dir / f"{program_prefix}{suffix}"
            if file_path.exists():
                file_path.unlink()
