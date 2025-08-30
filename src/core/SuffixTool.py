import os
from pathlib import Path

from common.Singleton import Singleton
from config_loaders.ToolConfig import ToolConfig
from utils.Logger import Logger

class SuffixTool(metaclass=Singleton):
    def run_tool(action: str="append") -> None:
        Logger.log_message("info", "Running suffix tool...")
        Logger.log_message("info", f"Tool action set to: {action} target suffix")

        try:
            _console_dir = ToolConfig.get_consoles_dir()
            for console in _console_dir.glob(""):

        except Exception as e:
            Logger.log_message("critical", f"SuffixTool.run_tool() has failed: {e}")
