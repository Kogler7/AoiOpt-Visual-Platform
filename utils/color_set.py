from PySide6.QtGui import QColor
from collections import defaultdict


class ColorSet:
    global_count = 0
    normal_cnt = 0
    dark_cnt = 0
    color_dict = {
        "light": [],
        "normal": [],
        "dark": []
    }
    named = {
        "Background": QColor(240, 240, 240),
        "LightGrey": QColor(225, 225, 225),
        "LightDark": QColor(100, 100, 100),
        "Indigo": QColor(75, 0, 130),  # 靛青
        "DoderBlue": QColor(30, 144, 255),  # 道奇蓝
        "Gold": QColor(255, 215, 0),  # 金色
    }

    @classmethod
    def init(cls):
        with open("./utils/color_set.txt") as f:
            name = ""
            for line in f:
                line = line.rstrip('\n')
                if line[0] == '-':
                    name = line.lstrip('-')
                else:
                    c = cls.hex_to_rgb(line)
                    cls.color_dict[name].append(QColor(c[0], c[1], c[2]))

    @classmethod
    def new_color(cls, c_type: str = "light"):
        """按顺序返回一个颜色"""
        if c_type not in cls.color_dict.keys():
            return QColor(0, 0, 0)
        if not cls.color_dict[c_type]:
            cls.init()
        cls.global_count += 2
        return cls.color_dict[c_type][cls.global_count % len(cls.color_dict[c_type])]

    @classmethod
    def idx_color(cls, idx: int, c_type: str = "light"):
        """根据idx返回对应颜色"""
        if c_type not in cls.color_dict.keys():
            return QColor(0, 0, 0)
        if not cls.color_dict[c_type]:
            cls.init()
        return cls.color_dict[c_type][idx * 3 % len(cls.color_dict[c_type])]

    @staticmethod
    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    @staticmethod
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb
