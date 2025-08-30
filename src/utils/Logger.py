import logging
from pathlib import Path
import shutil
import sys

from common.Singleton import Singleton
from utils.Formatter import Formatter
from utils.TestTime import TestTime


class Logger(metaclass=Singleton):
    
    # the code block below is necessary to add custom 'result' log level to logging
    # log level priority value -- higher value = higher priority
    RESULT_LEVEL_NUM = 15       
    logging.addLevelName(RESULT_LEVEL_NUM, "RESULT")

    def __result(self, message, *args, **kwargs):               #
        if self.isEnabledFor(Logger.RESULT_LEVEL_NUM):
            self._log(Logger.RESULT_LEVEL_NUM, message, args, **kwargs)

    logging.Logger.result = __result
    
    try:        
        # init logging module to enable error logging
        __logger = logging.getLogger('eventlog')
        # TODO - consider setting "setLevel" as a global var
        __logger.setLevel(logging.DEBUG)
        
        __formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d, %(levelname)s, %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        
        __eventlog = logging.FileHandler(filename='.\\eventlog.csv', mode='w')
        __eventlog.setFormatter(__formatter)
        
        __logger.addHandler(__eventlog)
        
        __logging_enabled = True

    except Exception as e:
        print(f'CRITICAL >> Exception during Logger init, {e}')
        while True:
            user_continue = str(input('Would you like to continue with console output only? [y/n]:\n$ ')).lower()
            match user_continue:
                case 'y' | 'yes':
                    __logging_enabled = False
                    break

                case 'n' | 'no':
                    print('INFO     >> Please verify that "eventlog.csv" is not open somewhere else and try again.')
                    print('INFO     >> Program closing...')
                    sys.exit()

                case _:
                    print("ERROR    >> invalid entry - please enter 'y' or 'n'\n")

    
    
    def is_logging_enabled() -> bool:          
        return Logger.__logging_enabled
        
    def log_message(log_level: str, message: str, write_to_log: bool=True, print_to_console: bool=True) -> None:        
        if print_to_console:
            # generate a "label" formatted with padding, text alignment, and a specified symbol, representing the specified log level
            __level_label = Formatter.pad_field_label(f'{log_level.upper()}', longest_field_len=len(max(Logger.__get_log_level_list(), key=len)), symbol='>>', alignment='center')
            
            # color message based on log-level severity using ANSI color codes
            match log_level.upper():
                case 'INFO':
                    __labeled_message = f'{__level_label} {message}'                    # default 
                case 'RESULT':
                    __labeled_message = f'\033[0;32m{__level_label} {message}\033[0m'   # green
                case 'DEBUG':
                    __labeled_message = f'\033[0;36m{__level_label} {message}\033[0m'   # cyan 
                case 'WARNING':
                    __labeled_message = f'\033[0;35m{__level_label} {message}\033[0m'   # purple  
                case 'ERROR':                
                    __labeled_message = f'\033[0;33m{__level_label} {message}\033[0m'   # yellow
                case 'CRITICAL':
                    __labeled_message = f'\033[0;31m{__level_label} {message}\033[0m'   # red
            
            # console output        
            print(f'[\033[2m{TestTime.get_fnow()}\033[0m] {__labeled_message}')         # dark gray
        
        # eventlog.csv output, if logging enabled
        if write_to_log and Logger.is_logging_enabled():
            __log_level = log_level.upper()
            match __log_level:
                case 'INFO':
                    Logger.__logger.info(message)
                case 'RESULT':
                    Logger.__logger.result(message)
                case 'DEBUG':
                    Logger.__logger.debug(message)
                case 'WARNING':
                    Logger.__logger.warning(message)
                case 'ERROR':
                    Logger.__logger.error(message)
                case 'CRITICAL':
                    Logger.__logger.critical(message)
        else:
            pass
    
    def __get_log_level_list() -> list[str]:
        return [name for name in logging._nameToLevel.keys()]
    
    def export_log(log_export_path: Path) -> None:          
        try:             
            # print final message to exported log to record export event
            Logger.log_message('info', f'Attempting export of, "eventlog.csv", to {log_export_path}')

            # copy target log to export destination specified in config.json
            shutil.copy('eventlog.csv', log_export_path)
            Logger.log_message('result', f'Log export successful!')
         
        except Exception as e:
            Logger.log_message('error', 'Unexpected Exception encountered while attempting export of "eventlog.csv"')
            Logger.log_message('info', 'Export attempt failed... log will not be exported')
    
    def shutdown_logging() -> None:     
        return logging.shutdown()





### unit test ###
if __name__ == "__main__":   
    import time
    Logger()
    ##print(Logger.__get_log_level_list())      # private method -- throws AttributeError when ran as __main__
    Logger.log_message('info', 'This is a message')
    # sleep to showcase timestamp functionality
    time.sleep(3)
    # test different log levels
    Logger.log_message('result', 'result')
    Logger.log_message('debug', 'debug')
    Logger.log_message('warning', 'warning')
    Logger.log_message('error', 'error')
    Logger.log_message('critical', 'critical')
    
    
    