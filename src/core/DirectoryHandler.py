from pathlib import Path

from common.Singleton import Singleton

class DirectoryHandler(metaclass=Singleton):
    def get_subdirectories(directory: Path) -> list[str]:
        return [folder.name for folder in Path(directory).iterdir() if folder.is_dir()]
    
    def add_subdirectory_to_path(directory: Path, subdirectory: str) -> Path:
        return Path(str(directory) + f"\\{subdirectory}")