import json
import os.path
from glob import glob


class ConfigProxy:
    config_path = os.path.abspath(".\\visual_plat\\builtin_config\\*.json")
    config: dict[str, dict] = {}

    @staticmethod
    def load():
        path = os.path.join(ConfigProxy.config_path)
        config_paths = glob(path)
        for pth in config_paths:
            with open(pth) as f:
                tag = pth.split('\\')[-1][:-5]
                ConfigProxy.config[tag] = json.load(f)

    @staticmethod
    def get(tag):
        return ConfigProxy.config[tag]

    @staticmethod
    def path(tag):
        return ConfigProxy.config["paths"][tag]

    @staticmethod
    def canvas(tag):
        return ConfigProxy.config["canvas"][tag]

    @staticmethod
    def event(tag):
        return ConfigProxy.config["events"][tag]

    @staticmethod
    def layout(tag):
        return ConfigProxy.config["canvas"]["layout"][tag]

    @staticmethod
    def tooltip(tag):
        return ConfigProxy.config["canvas"]["tooltip"][tag]

    @staticmethod
    def record(tag):
        return ConfigProxy.config["canvas"]["record"][tag]
