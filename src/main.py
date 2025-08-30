import unit_tests
from common import constants
from utils.Logger import Logger
from utils.TestTime import TestTime
from utils.Formatter import Formatter

from config_loaders.ToolConfig import ToolConfig
from pathlib import Path

def main():
    print("running Main...")



### main ###
if (__name__ == "__main__"):
    if constants.UNIT_TESTS:
        #unit_tests.run_unit_tests()

        ToolConfig()
        __consoles_dir = ToolConfig.get_consoles_dir()
        __media_dir_identifier = ToolConfig.get_media_dir_identifier()
        __console_folders = [folder.name for folder in __consoles_dir.iterdir() if folder.is_dir()]
        print(__console_folders)

        for console_name in __console_folders:
            print(console_name)
            __current_console_folder_path = Path(str(__consoles_dir) + f"\\{console_name}")
            __console_subfolders = [folder.name for folder in __current_console_folder_path.iterdir() if folder.is_dir()]
            print(__console_subfolders)

            for subfolder in __console_subfolders:
                # if a folder named with the "media_dir_identifier" not found, skip to next console folder
                if __media_dir_identifier not in __console_subfolders:
                    Logger.log_message("warning", f"Skipped '{console_name}' folder -- does not contain a '\\{__media_dir_identifier}' folder")
                    break
                else:
                    if subfolder == __media_dir_identifier:
                        # build media folder path
                        __media_folder_path = Path(str(__current_console_folder_path) + f"\\{subfolder}")
                        break
            
            __media_subfolders = [folder.name for folder in __media_folder_path.iterdir() if folder.is_dir()]
            print(__media_subfolders)

    else:
        main()