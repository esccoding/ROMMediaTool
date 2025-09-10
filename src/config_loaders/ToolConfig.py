import json
import os
from pathlib import Path
import sys


from common import constants
from common.Singleton import Singleton
from core.DirectoryHandler import DirectoryHandler
from utils.Formatter import Formatter
from utils.Logger import Logger
from utils.TextColor import TextColor as tc

class ToolConfig(metaclass=Singleton):
    config_data = None

    try:
        # init logging
        Logger()
        Logger.log_message("info", "Logging successfully initialized")

        # load in JSON dict from config file
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
    
    def get_target_media_file_types() -> list[str]:
        return ToolConfig.config_data[constants.CONFIG_TOOL_SETTINGS_KEY]["target_media_file_types"]
    
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
        Logger.log_message("info", f"Validating '{constants.CONFIG_FILE}' configuration...")
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
                ToolConfig._invalid_config_response("Output directory", log_level="error", exit_program=False)
                while True:
                    __create_dir_reply = input(f"Would you like to create a path to {tc.CYAN}'{__output_dir}'{tc.END} now? [y/n]\n>> ")
                    match __create_dir_reply:
                        case "y" | "yes":
                            # Create output filepath
                            try:
                                os.makedirs(__output_dir)
                                Logger.log_message("result", f"Path to '{__output_dir}' created successfully.")
                                break

                            except FileExistsError:
                                Logger.log_message("warning", f"One or more directories in '{__output_dir}' already exist.")
                                ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)

                            except PermissionError:
                                Logger.log_message("critical", f"Permission denied: Unable to create '{__output_dir}'.")
                                ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)

                            except Exception as e:
                                Logger.log_message("error", "An error occurred: {e}")
                                ToolConfig._invalid_config_response("Output directory", invalid_messaging=False)
                                
                        case "n" | "no":
                            ToolConfig._invalid_config_response("Output directory")

                        case _:
                            print("ERROR | Invalid reponse - enter 'y' or 'n'\n")

            # verify directories for configured "target_consoles" exist in "consoles_dir" and contain subdirectory named with "media_dir_identifier"
            __target_consoles = []
            __media_dir_identifier = ToolConfig.get_media_dir_identifier()

            # if 'scan_all_consoles' disabled, get configured 'target_consoles' as list
            __scan_all_consoles = ToolConfig.is_scan_all_consoles_enabled()
            if not __scan_all_consoles:
                __target_consoles = ToolConfig.get_target_consoles()
            else:
                # get all subdirectories of configured consoles directory
                __target_consoles = DirectoryHandler.get_subdirectories(__consoles_dir)
            
            # if 'scan_all_consoles' disabled and no other target consoles configured
            if not __scan_all_consoles and not __target_consoles:
                Logger.log_message("error", f"'scan_all_consoles' setting is disabled in '{constants.CONFIG_FILE}'")
                Logger.log_message("error", f"No target consoles specified in '{constants.CONFIG_FILE}'")
                ToolConfig._invalid_config_response('Console settings')

            # check that each console dir contains subdir named with the "media_dir_identifier"
            for console in __target_consoles:
                __current_console_dir_path = DirectoryHandler.add_to_path(__consoles_dir, console)

                try:
                    __current_console_subdirs_list = DirectoryHandler.get_subdirectories(__current_console_dir_path)

                except FileNotFoundError:
                    Logger.log_message("error", f"Configured target console '{console}' has no corresponding folder in consoles directory")
                    ToolConfig._invalid_config_response("Target consoles")

                # if "media_dir_identifier" subdir not found, skip to next console dir
                if __media_dir_identifier not in __current_console_subdirs_list:
                    Logger.log_message("warning", f"Skipped '\\{console}' directory -- does not contain a '\\{__media_dir_identifier}' subdirectory")
                else:
                    Logger.log_message("info", f"Media subdirectory identified in {tc.YELLOW}'\\{console}'{tc.END} directory ")

            # verify "suffix_action" has valid configuration
            if ToolConfig.get_suffix_action() not in ["add", "remove"]:
                ToolConfig._invalid_config_response("Suffix action")    

            # verify at least one valid file type specified in configuration
            __target_media_file_types = ToolConfig.get_target_media_file_types()
            if not __target_media_file_types:
                Logger.log_message("error", f"At least one media file type must be specified as a target in '{constants.CONFIG_FILE}'")
                ToolConfig._invalid_config_response("Target media file types")
            else:
                for file_type in __target_media_file_types:
                    if file_type[:1] == ".":
                        Logger.log_message("info", f"{tc.YELLOW}'{file_type}'{tc.END} files identified as target for name modification")
                    else:
                        Logger.log_message("info", f"{tc.YELLOW}'.{file_type}'{tc.END} files identified as target for name modification")

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
                    Logger.log_message("info", f"{tc.YELLOW}'{suffix}'{tc.END} will be added to filenames in {tc.CYAN}'{media_type}'{tc.END} folders")

            # all fields validated in config file
            Logger.log_message("result", f"All configurations in '{constants.CONFIG_FILE}' are valid")


        except Exception as e:
            Logger.log_message("critical", f"'{constants.CONFIG_FILE}' validation failed: {e}")

    def _invalid_config_response(config_key: str, log_level: str="critical", invalid_messaging: bool=True, exit_program: bool=True) -> None:
        if invalid_messaging:
            Logger.log_message(f"{log_level}", f"Invalid {config_key.lower()} configuration in '{constants.CONFIG_FILE}'")

        if exit_program:
            Logger.log_message("info", f"Please verify that the '{constants.CONFIG_FILE}' file is configured correctly and try again")
            Logger.log_message("info", "Program closing...")
            sys.exit()
        
    def run_unit_test() -> None:
        ToolConfig()
        Logger.log_message("info", f"{Formatter.generate_header("Testing ToolConfig methods", capitalize=False)}")
        try:
            Logger.log_message("info", f"{tc.YELLOW}get_console_dir(){tc.END} returned {type(ToolConfig.get_consoles_dir())} -> {tc.GREEN}{ToolConfig.get_consoles_dir()}{tc.END}")
            Logger.log_message("info", f"{tc.YELLOW}get_output_dir(){tc.END} returned {type(ToolConfig.get_output_dir())} -> {tc.GREEN}{ToolConfig.get_output_dir()}{tc.END}")
            Logger.log_message("info", f"{tc.YELLOW}get_suffix_action(){tc.END} returned {type(ToolConfig.get_suffix_action())} -> {tc.GREEN}{ToolConfig.get_suffix_action()}{tc.END}")
            Logger.log_message("info", f"{tc.YELLOW}get_media_dir_identifier(){tc.END} returned {type(ToolConfig.get_media_dir_identifier())} -> {tc.GREEN}{ToolConfig.get_media_dir_identifier()}{tc.END}")
            Logger.log_message("info", f"{tc.YELLOW}get_target_media_file_types(){tc.END} returned {type(ToolConfig.get_target_media_file_types())} -> {tc.GREEN}{ToolConfig.get_target_media_file_types()}{tc.END}")
            Logger.log_message("info", f"{tc.YELLOW}get_target_suffixes(){tc.END} returned {type(ToolConfig.get_target_media_suffix_pairs())} -> {tc.GREEN}{ToolConfig.get_target_media_suffix_pairs()}{tc.END}")
        
        except Exception as e:
            Logger.log_message("critical", f"ToolConfig unit test has failed: {e}")

