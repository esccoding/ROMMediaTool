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
        ToolConfig.is_config_valid()
            


    else:
        main()