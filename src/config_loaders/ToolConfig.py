import json
import os
from pathlib import Path
import sys


from common import constants
from common.Singleton import Singleton
from core.DirectoryHandler import DirectoryHandler
from utils.Formatter import Formatter
from utils.Logger import Logger
from utils.TextColor import TextColor

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
    
    def get_media_dir_identifier() -> str:
        return str(ToolConfig.config_data[constants.CONFIG_CONSOLE_SETTINGS_KEY]["media_dir_identifier"])

    def get_suffix_action() -> str:
        return str(ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["suffix_action"])
    
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
                Logger.log_message("critical", f"The configured consoles directory filepath '{__consoles_dir}' does not exist")
                ToolConfig._invalid_config_response("Consoles directory")
            
            # verify target output directory exists in system; if not, prompt dir creation
            __output_dir = ToolConfig.get_output_dir()
            if not os.path.exists(__output_dir):
                Logger.log_message("warning", f"The configured output directory filepath '{__output_dir}' does not exist")
                ToolConfig._invalid_config_response("Output directory", exit_program=False)
                while True:
                    __create_dir_reply = input(f"Would you like to create a path to '{__output_dir}' now? [y/n]")
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

            # verify directories for configured "target_consoles" exist in "consoles_dir" and contain subdirectory named with "media_dir_identifier"
            __target_consoles = []
            __media_dir_identifier = ToolConfig.get_media_dir_identifier()

            # if "scan_all_consoles" disabled, get specific target consoles as list
            if not ToolConfig.is_scan_all_consoles_enabled():
                __target_consoles = ToolConfig.get_target_consoles()
            
            # get all subdirectories of configured consoles directory
            __consoles_dir_subdirs_list = DirectoryHandler.get_subdirectories(__consoles_dir)
            ##__consoles_dir_subfolders = [folder.name for folder in __consoles_dir.iterdir() if folder.is_dir()]

            for consoles_dir_subdir in __consoles_dir_subdirs_list:
                # if scan all consoles is enabled, or console is configured as target
                if not __target_consoles or consoles_dir_subdir in __target_consoles:
                    __current_console_dir_path = DirectoryHandler.add_subdirectory_to_path(__consoles_dir, consoles_dir_subdir)
                    ##__current_console_folder_path = Path(str(__consoles_dir) + f"\\{consoles_dir_subfolder}")
                    __current_console_subdirs_list = DirectoryHandler.get_subdirectories(__current_console_dir_path)
                    ##__console_subfolders = [folder.name for folder in __current_console_folder_path.iterdir() if folder.is_dir()]

                for console_subdir in __current_console_subdirs_list:
                    # if a directory named with the "media_dir_identifier" not found, skip to next console directory
                    if __media_dir_identifier not in __current_console_subdirs_list:
                        Logger.log_message("warning", f"Skipped '\\{consoles_dir_subdir}' directory -- does not contain a '\\{__media_dir_identifier}' subdirectory")
                        break
                    else:
                        if console_subdir == __media_dir_identifier:
                            Logger.log_message("info", f"'\\{__media_dir_identifier}' subdirectory identified in '\\{consoles_dir_subdir}' directory ")


            # verify "suffix_action" has valid configuration
            if ToolConfig.get_suffix_action() not in ["add", "remove"]:
                ToolConfig._invalid_config_response("Suffix action")    

            # verify at least one valid file type specified in configuration
            if not ToolConfig.get_valid_media_file_types():
                Logger.log_message("error", f"At least one valid media file type must be specified in '{constants.CONFIG_FILE}'")
                ToolConfig._invalid_config_response("Valid media file types")

            # verify at least one suffix has been specified in configuration
            __suffix_dict = ToolConfig.get_suffixes_by_media_type_dict()
            __media_type_suffix_pairs = []

            for media_type, suffix in __suffix_dict.items():
                if suffix:
                    __media_type_suffix_pairs.append((media_type, suffix))
            
            # if no suffixes configured
            if not __media_type_suffix_pairs:
                Logger.log_message("error", f"At least one (media type : suffix) pair must be specified in '{constants.CONFIG_FILE}'")
                ToolConfig._invalid_config_response("Suffixes by media types")
            else:
                for pair in __media_type_suffix_pairs:
                    # unpack pair tuples
                    media_type, suffix = pair
                    Logger.log_message("info", f"'{suffix}' will be added to files in '{media_type}' folders")

            # all fields validated in config file
            Logger.log_message("result", f"All configurations in '{constants.CONFIG_FILE}' are valid")


        except Exception as e:
            Logger.log_message("critical", f"'{constants.CONFIG_FILE}' validation failed: {e}")

    def _invalid_config_response(config_key: str, invalid_messaging: bool=True, exit_program: bool=True) -> None:
        if invalid_messaging:
            Logger.log_message("critical", f"{config_key} configuration in '{constants.CONFIG_FILE}' is invalid")

        if exit_program:
            Logger.log_message("info", f"Please verify that the '{constants.CONFIG_FILE}' file is configured correctly and try again")
            Logger.log_message("info", "Program closing...")
            sys.exit()
        
    def run_unit_test() -> None:
        ToolConfig()
        Logger.log_message("info", f"{Formatter.generate_header("Testing ToolConfig methods", capitalize=False)}")
        try:
            Logger.log_message("info", f"{TextColor.YELLOW}get_console_dir(){TextColor.END} returned {type(ToolConfig.get_consoles_dir())} -> {TextColor.GREEN}{ToolConfig.get_consoles_dir()}{TextColor.END}")
            Logger.log_message("info", f"{TextColor.YELLOW}get_output_dir(){TextColor.END} returned {type(ToolConfig.get_output_dir())} -> {TextColor.GREEN}{ToolConfig.get_output_dir()}{TextColor.END}")
            Logger.log_message("info", f"{TextColor.YELLOW}get_suffix_action(){TextColor.END} returned {type(ToolConfig.get_suffix_action())} -> {TextColor.GREEN}{ToolConfig.get_suffix_action()}{TextColor.END}")
            Logger.log_message("info", f"{TextColor.YELLOW}get_media_dir_identifier(){TextColor.END} returned {type(ToolConfig.get_media_dir_identifier())} -> {TextColor.GREEN}{ToolConfig.get_media_dir_identifier()}{TextColor.END}")
            Logger.log_message("info", f"{TextColor.YELLOW}get_valid_media_file_types(){TextColor.END} returned {type(ToolConfig.get_valid_media_file_types())} -> {TextColor.GREEN}{ToolConfig.get_valid_media_file_types()}{TextColor.END}")
            Logger.log_message("info", f"{TextColor.YELLOW}get_target_suffixes(){TextColor.END} returned {type(ToolConfig.get_target_media_suffix_pairs())} -> {TextColor.GREEN}{ToolConfig.get_target_media_suffix_pairs()}{TextColor.END}")
        
        except Exception as e:
            Logger.log_message("critical", f"ToolConfig unit test has failed: {e}")

