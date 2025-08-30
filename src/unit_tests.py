from config_loaders.ToolConfig import ToolConfig
from utils.Formatter import Formatter
from utils.Logger import Logger

def run_unit_tests():
    Logger.log_message("info", "Running unit tests...")
    # initialize classes
    ToolConfig()
    
    # ToolConfig.py
    ToolConfig.run_unit_test()
    

if __name__ == "__main__":
    run_unit_tests()