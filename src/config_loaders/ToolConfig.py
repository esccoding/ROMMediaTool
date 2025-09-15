import json
import os
from pathlib import Path
import sys

from common import constants
from common.Singleton import Singleton
from core.DirectoryHandler import DirectoryHandler
from utils.Formatter import Formatter
from utils.Logger import Logger
from utils.TestTime import TestTime
from utils.TextColor import TextColor as tc

class ToolConfig(metaclass=Singleton):
    config_data = None
    target_media_dirs = []
    output_dir = ""

    try:
        # init logging
        Logger()
        Logger.log_message("info", "Logging successfully initialized")
        Logger.log_message("info", f"ROMMediaTool initialized at {TestTime.get_fstart()}")

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

    def is_config_validation_enabled() -> bool:
        return ToolConfig.config_data["validate_config"]

    def get_consoles_dir() -> Path:
        return Path(ToolConfig.config_data[constants.CONFIG_TARGET_DIR_KEY]["consoles_dir"])
    
    def get_output_dir() -> Path:
        __output_path = ToolConfig.config_data[constants.CONFIG_TARGET_DIR_KEY]["output_dir"]
        # if no configured output path
        if not __output_path:
            return ""
        
        else:
            return Path(__output_path)
    
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
            # identify target consoles directory
            __consoles_dir = ToolConfig.__identify_console_dir_path()
            Logger.log_message("info", f"Console directory path identified as '{__consoles_dir}'", print_to_console=False)
            Logger.log_message("info", f"Console directory path identified as {tc.CYAN}'{__consoles_dir}'{tc.END}", write_to_log=False)

            # identify output consoles directory
            ToolConfig.output_dir = ToolConfig.__identify_output_dir_path()
            Logger.log_message("info", f"Output directory path identified as '{ToolConfig.output_dir}'", print_to_console=False)
            Logger.log_message("info", f"Output directory path identified as {tc.CYAN}'{ToolConfig.output_dir}'{tc.END}", write_to_log=False)

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
                ToolConfig.__invalid_config_response('Console settings')

            # check that each console dir contains subdir named with the "media_dir_identifier"
            for console in __target_consoles:
                __current_console_dir_path = DirectoryHandler.add_to_path(__consoles_dir, console)

                try:
                    __current_console_subdirs_list = DirectoryHandler.get_subdirectories(__current_console_dir_path)

                except FileNotFoundError:
                    Logger.log_message("error", f"Configured target console '{console}' has no corresponding folder in consoles directory")
                    ToolConfig.__invalid_config_response("Target consoles")

                # if "media_dir_identifier" subdir not found, skip to next console dir
                if __media_dir_identifier not in __current_console_subdirs_list:
                    Logger.log_message("warning", f"Skipped '\\{console}' directory -- does not contain a '\\{__media_dir_identifier}' subdirectory")
                else:
                    # append `media_dir_identifier` to current console path and append new path to class-global list of target directory paths
                    ToolConfig.target_media_dirs.append(DirectoryHandler.add_to_path(__current_console_dir_path, __media_dir_identifier))
                    Logger.log_message("info", f"Media subdirectory identified in '\\{console}' directory ", print_to_console=False)
                    Logger.log_message("info", f"Media subdirectory identified in {tc.YELLOW}'\\{console}'{tc.END} directory ", write_to_log=False)

            # verify "suffix_action" has valid configuration
            if ToolConfig.get_suffix_action() not in ["add", "remove"]:
                ToolConfig.__invalid_config_response("Suffix action")    

            # verify at least one valid file type specified in configuration
            __target_media_file_types = ToolConfig.get_target_media_file_types()
            if not __target_media_file_types:
                Logger.log_message("error", f"At least one media file type must be specified as a target in '{constants.CONFIG_FILE}'")
                ToolConfig.__invalid_config_response("Target media file types")
            else:
                for file_type in __target_media_file_types:
                    if file_type[:1] == ".":
                        Logger.log_message("info", f"'{file_type}' files identified as target for name modification", print_to_console=False)
                        Logger.log_message("info", f"{tc.YELLOW}'{file_type}'{tc.END} files identified as target for name modification", write_to_log=False)
                    else:
                        Logger.log_message("info", f"'.{file_type}' files identified as target for name modification", print_to_console=False)
                        Logger.log_message("info", f"{tc.YELLOW}'.{file_type}'{tc.END} files identified as target for name modification", write_to_log=False)

            # verify at least one suffix has been specified in configuration
            __suffix_dict = ToolConfig.get_suffixes_by_media_type_dict()
            __media_type_suffix_pairs = []

            for media_type, suffix in __suffix_dict.items():
                if suffix:
                    __media_type_suffix_pairs.append((media_type, suffix))
            
            # if no suffixes configured
            if not __media_type_suffix_pairs:
                Logger.log_message("error", f"At least one (media type : suffix) pair must be specified in '{constants.CONFIG_FILE}'")
                ToolConfig.__invalid_config_response("Suffixes by media types")
            else:
                for pair in __media_type_suffix_pairs:
                    # unpack pair tuples
                    media_type, suffix = pair
                    Logger.log_message("info", f"'{suffix}' will be added to filenames in '{media_type}' folders", print_to_console=False)
                    Logger.log_message("info", f"{tc.YELLOW}'{suffix}'{tc.END} will be added to filenames in {tc.CYAN}'{media_type}'{tc.END} folders", write_to_log=False)

            # all fields validated in config file
            Logger.log_message("result", f"All configurations in '{constants.CONFIG_FILE}' are valid")
            return True


        except Exception as e:
            Logger.log_message("critical", f"'{constants.CONFIG_FILE}' validation failed: {e}")

    def __identify_console_dir_path() -> Path:
        __consoles_dir = ToolConfig.get_consoles_dir()

        # verify target consoles directory exists in system
        if not os.path.exists(__consoles_dir):
            Logger.log_message("critical", f"The configured consoles directory filepath '{__consoles_dir}' does not exist")
            ToolConfig.__invalid_config_response("Consoles directory")     

        return Path(__consoles_dir)
    
    def __identify_output_dir_path() -> Path:
        # verify target output directory exists in system; if not, prompt dir creation
        __output_dir = ToolConfig.get_output_dir()

        # if no output dir configured, use default output folder (local "output")
        if not __output_dir:
            __output_dir = ".\\output"

            # if default local "output" folder not yet created
            if not os.path.exists(__output_dir):
                try:
                    ToolConfig.__create_path(__output_dir)

                except Exception:
                    ToolConfig.__invalid_config_response("Output directory", invalid_messaging=False)

        # if output dir configured, verify path exists in system
        if not os.path.exists(__output_dir):
            Logger.log_message("warning", f"The configured output directory filepath '{__output_dir}' does not exist")
            ToolConfig.__invalid_config_response("Output directory", log_level="error", exit_program=False)
            
            while True:
                __create_dir_reply = input(f"Would you like to create a path to {tc.CYAN}'{__output_dir}'{tc.END} now? [y/n]\n>> ")
                match __create_dir_reply:
                    case "y" | "yes":
                        try:
                            ToolConfig.__create_path(__output_dir)
                            break

                        except Exception:
                            ToolConfig.__invalid_config_response("Output directory")
                    
                    case "n" | "no":
                        ToolConfig.__invalid_config_response("Output directory")

                    case _:
                        print("ERROR | Invalid reponse - enter 'y' or 'n'\n")
                    
        return Path(__output_dir)

    def __create_path(desired_path: str) -> None:
        # Create desired filepath
        try:
            os.makedirs(desired_path)
            Logger.log_message("result", f"Path to '{desired_path}' created successfully.")
            return

        except FileExistsError as fee:
            Logger.log_message("warning", f"One or more directories in '{desired_path}' already exist: {fee}")
            Logger.log_message("error", f"Cannot create path to '{desired_path}'")
            raise Exception

        except PermissionError as pe:
            Logger.log_message("warning", f"Permission denied: {pe}")
            Logger.log_message("error", f"Cannot create path to '{desired_path}'")
            raise Exception

        except Exception as e:
            Logger.log_message("warning", f"An error occurred: {e}")
            Logger.log_message("error", f"Cannot create path to '{desired_path}'")
            raise Exception

    def __invalid_config_response(config_key: str, log_level: str="critical", invalid_messaging: bool=True, exit_program: bool=True) -> None:
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
            Logger.log_message("info", f"get_console_dir() returned {type(ToolConfig.get_consoles_dir())}, {ToolConfig.get_consoles_dir()}")
            Logger.log_message("info", f"get_output_dir() returned {type(ToolConfig.get_output_dir())}, {ToolConfig.get_output_dir()}")
            Logger.log_message("info", f"get_suffix_action() returned {type(ToolConfig.get_suffix_action())}, {ToolConfig.get_suffix_action()}")
            Logger.log_message("info", f"get_media_dir_identifier() returned {type(ToolConfig.get_media_dir_identifier())}, {ToolConfig.get_media_dir_identifier()}")
            Logger.log_message("info", f"get_target_media_file_types() returned {type(ToolConfig.get_target_media_file_types())}, {ToolConfig.get_target_media_file_types()}")
            Logger.log_message("info", f"get_target_suffixes() returned {type(ToolConfig.get_target_media_suffix_pairs())}, {ToolConfig.get_target_media_suffix_pairs()}")
        
        except Exception as e:
            Logger.log_message("critical", f"ToolConfig unit test has failed: {e}")

