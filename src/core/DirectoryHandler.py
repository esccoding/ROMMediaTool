from pathlib import Path

from common.Singleton import Singleton
from utils.Logger import Logger

class DirectoryHandler(metaclass=Singleton):
    def get_subdirectories(directory: Path) -> list[str]:
        try:
            __target_subdirectories = [folder.name for folder in Path(directory).iterdir() if folder.is_dir()]
            return __target_subdirectories
        
        except FileNotFoundError:
            Logger.log_message("error", f"Unable to collect subdirectories from '{directory}' -- path does not exist")
            raise FileNotFoundError
        
        except Exception as e:
            Logger.log_message("critical", f"Unexpected exception encountered in DirectoryHandler.get_subdirectories(): {e}")
    
    def add_to_path(directory: Path, subdirectory: str) -> Path:
        return Path(str(directory) + f"\\{subdirectory}")