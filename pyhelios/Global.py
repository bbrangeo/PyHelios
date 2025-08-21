import os

from .wrappers import UGlobalWrapper as global_wrapper

class Global:

    @staticmethod
    def set_build_plugin_root_directory(directory:str) -> None:
        global_wrapper.setBuildPluginRootDirectory(directory)

    @staticmethod
    def get_build_plugin_root_directory() -> str:
        return global_wrapper.getBuildPluginRootDirectory()
    
