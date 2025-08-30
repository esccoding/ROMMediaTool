import json
import os
from pathlib import Path
import sys


from common import constants
from common.Singleton import Singleton
from utils.Formatter import Formatter
from utils.Logger import Logger

class ToolConfig(metaclass=Singleton):
    config_data = None

    try:
        # init logging
        Logger()
        Logger.log_message("info", "Logging successfully initialized")

        with open(f'.\\config\\{constants.CONFIG_FILE}') as config_file:
            config_data = json.load(config_file)
            config_file.close()

    except json.JSONDecodeError as jde:
        Logger.log_message('critical', f'JSONDecodeError during Config init, {jde}')
        Logger.log_message('info', f'Please verify that the "{constants.CONFIG_FILE}" file is formatted correctly and try again.')
        Logger.log_message('info', 'Program closing...')
        sys.exit()
        
    except Exception as e:
        Logger.log_message('critical', f'Unexpected Exception encountered during TestConfig init, {e}')
        Logger.log_message('info', f'Please verify that the "{constants.CONFIG_FILE}" file is formatted correctly and try again.')
        Logger.log_message('info', 'Program closing...')
        sys.exit()

    def get_consoles_dir() -> Path:
        return Path(ToolConfig.config_data[constants.CONFIG_TARGET_DIR_KEY]["consoles_dir"])
    
    def get_output_dir() -> Path:
        return Path(ToolConfig.config_data[constants.CONFIG_TARGET_DIR_KEY]["output_dir"])
    
    def is_scan_all_consoles_enabled() -> bool:
        return ToolConfig.config_data[constants.CONFIG_CONSOLE_SETTINGS_KEY]["scan_all_consoles"]
    
    def get_target_consoles() -> list[str]:
        return ToolConfig.config_data[constants.CONFIG_CONSOLE_SETTINGS_KEY]["target_consoles"]

    def get_suffix_action() -> str:
        return str(ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["suffix_action"])
    
    def get_media_dir_identifier() -> str:
        return str(ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["media_dir_identifier"])
    
    def get_valid_media_file_types() -> list[str]:
        return ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["valid_media_file_types"]
    
    def get_suffixes_by_media_type_dict() -> dict:
        return ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["suffixes_by_media_type"]

    # TODO - delete method? unnecessary?
    def get_target_media_suffix_pairs() -> list[list[str]]:
        target_media_suffix_pairs = []
        for media_type, suffix in ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["suffixes_by_media_type"].items():
            if suffix:
                target_media_suffix_pairs.append((media_type, suffix))
        return target_media_suffix_pairs
    
    def is_config_valid() -> bool:
        try:
            # verify target consoles directory exists in system
            __consoles_dir = ToolConfig.get_consoles_dir()
            if not os.path.exists(__consoles_dir):
                ToolConfig._invalid_config_response("Consoles directory")
            
            # verify target output directory exists in system; if not, prompt dir creation
            __output_dir = ToolConfig.get_output_dir()
            if not os.path.exists(__output_dir):
                ToolConfig._invalid_config_response("Output directory", exit=False)
                while True:
                    __create_dir_reply = input(f"Would you like to create a path to '{__output_dir}'  now? [y/n]")
                    match __create_dir_reply:
                        case "y" | "yes":
                            # Create output filepath
                            try:
                                os.makedirs(__output_dir)
                                print(f"Nested directories '{__output_dir}' created successfully.")
                                break

                            except FileExistsError:
                                print(f"One or more directories in '{__output_dir}' already exist.")
                                ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)

                            except PermissionError:
                                print(f"Permission denied: Unable to create '{__output_dir}'.")
                                ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)

                            except Exception as e:
                                print(f"An error occurred: {e}")
                                ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)
                                
                        case "n" | "no":
                            ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)

                        case _:
                            print("ERROR | Invalid reponse - enter 'y' or 'n'\n")

            # verify "remove suffix" is configured as bool
            if ToolConfig.get_suffix_action() not in ["add", "remove"]:
                ToolConfig._invalid_config_response("Suffix action")

            # verify that "media directory identifier" is present in target folders
            __media_dir_identifier = ToolConfig.get_media_dir_identifier()
            # get all subfolders of configured consoles directory
            __console_folders = [folder.name for folder in __consoles_dir.iterdir() if folder.is_dir()]

            for console_name in __console_folders:
                __current_console_folder_path = Path(str(__consoles_dir) + f"\\{console_name}")
                __console_subfolders = [folder.name for folder in __current_console_folder_path.iterdir() if folder.is_dir()]

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
                for media_subfolder in __media_subfolders:
                    
                    




        except Exception as e:
            Logger.log_message("critical", f"'{constants.CONFIG_FILE}' validation failed: {e}")

    def _invalid_config_response(invalid_config_key: str, invalid_messaging: bool=True, exit_program: bool=True) -> None:
        if invalid_messaging:
            Logger.log_message("critical", f"{invalid_config_key} configuration in {constants.CONFIG_FILE} is invalid")

        if exit_program:
            Logger.log_message("info", f"Please verify that the '{constants.CONFIG_FILE}' file is configured correctly and try again")
            Logger.log_message("info", "Program closing...")
            sys.exit()
        
    def run_unit_test() -> None:
        ToolConfig()
        Logger.log_message("info", f"{Formatter.generate_header("Testing ToolConfig methods", capitalize=False)}")
        try:
            Logger.log_message("info", f"\033[0;33mget_console_dir()\033[0m returned {type(ToolConfig.get_consoles_dir())} -> \033[0;32m{ToolConfig.get_consoles_dir()}\033[0m")
            Logger.log_message("info", f"\033[0;33mget_output_dir()\033[0m returned {type(ToolConfig.get_output_dir())} -> \033[0;32m{ToolConfig.get_output_dir()}\033[0m")
            Logger.log_message("info", f"\033[0;33mget_suffix_action()\033[0m returned {type(ToolConfig.get_suffix_action())} -> \033[0;32m{ToolConfig.get_suffix_action()}\033[0m")
            Logger.log_message("info", f"\033[0;33mget_media_dir_identifier()\033[0m returned {type(ToolConfig.get_media_dir_identifier())} -> \033[0;32m{ToolConfig.get_media_dir_identifier()}\033[0m")
            Logger.log_message("info", f"\033[0;33mget_valid_media_file_types()\033[0m returned {type(ToolConfig.get_valid_media_file_types())} -> \033[0;32m{ToolConfig.get_valid_media_file_types()}\033[0m")
            Logger.log_message("info", f"\033[0;33mget_target_suffixes()\033[0m returned {type(ToolConfig.get_target_media_suffix_pairs())} -> \033[0;32m{ToolConfig.get_target_media_suffix_pairs()}\033[0m")
        
        except Exception as e:
            Logger.log_message("critical", f"ToolConfig unit test has failed: {e}")

