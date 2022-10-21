import json
import os.path
from glob import glob


class ConfigProxy:
    loaded = False
    plat_path = "."
    config: dict[str, dict] = {}
    layer_config: dict[str, dict] = {}

    @staticmethod
    def load():
        config_path = os.path.abspath(f"{ConfigProxy.plat_path}\\visual_plat\\builtin_config\\*.json")
        path = os.path.join(config_path)
        config_paths = glob(path)
        for pth in config_paths:
            with open(pth) as f:
                tag = pth.split('\\')[-1][:-5]
                ConfigProxy.config[tag] = json.load(f)
        ConfigProxy.loaded = True

    @staticmethod
    def load_layer(tag: str, config: dict):
        """载入图层配置（方便图层访问）"""
        ConfigProxy.layer_config[tag] = config

    @staticmethod
    def layer(tag):
        return ConfigProxy.layer_config[tag]

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
    def event():
        return ConfigProxy.config["events"]["key"]

    @staticmethod
    def event_setting():
        return ConfigProxy.config["events"]["setting"]

    @staticmethod
    def layout(tag):
        return ConfigProxy.config["canvas"]["layout"][tag]

    @staticmethod
    def tooltip(tag):
        return ConfigProxy.config["canvas"]["tooltip"][tag]

    @staticmethod
    def record(tag):
        return ConfigProxy.config["canvas"]["record"][tag]
