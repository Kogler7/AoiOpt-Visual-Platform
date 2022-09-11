import json
import os.path
from glob import glob


class ConfigProxy:
    config_path = ".\\visual_plat\\builtin_config\\*.json"
    config: dict[str, dict] = {}

    @staticmethod
    def load():
        path = os.path.join(ConfigProxy.config_path)
        config_paths = glob(path)
        for pth in config_paths:
            with open(pth) as f:
                name = pth.split('\\')[-1][:-5]
                ConfigProxy.config[name] = json.load(f)

    @staticmethod
    def get(name):
        return ConfigProxy.config[name]

    @staticmethod
    def path(name):
        if "paths" in ConfigProxy.config.keys():
            return ConfigProxy.config["paths"][name]

    @staticmethod
    def canvas(name):
        return ConfigProxy.config["canvas"][name]

    @staticmethod
    def layout(name):
        return ConfigProxy.config["canvas"]["layout"][name]

    @staticmethod
    def render(name):
        return ConfigProxy.config["canvas"]["render"][name]
