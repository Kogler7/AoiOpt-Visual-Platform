from PySide6.QtWidgets import *
from PySide6.QtGui import *


class LayerBase:
    def __init__(self, canvas):
        self.aoi_map = None
        self.canvas = canvas
        self.state = canvas.event_deputy
        self.render = canvas.render_deputy
        self.layout = canvas.layout_deputy
        self.layers: list[LayerBase] = canvas.layer_list
        self.level = 0
        self.xps_tag = ""
        self.visible = True
        self.data = None

    def set_level(self, level: int):
        """调整层级关系"""
        self.level = level
        self.layers.sort(key=lambda layer: layer.level, reverse=False)

    def reload(self, data):
        """全局更新时调用"""
        return False

    def adjust(self, data):
        """局部更新时调用"""
        return False

    def on_stage(self, device: QPixmap):
        """重绘buff图层时自动调用"""
        return False

    def on_paint(self, device: QWidget):
        """重绘时自动调用"""
        return False

    def force_restage(self):
        """用于主动更新"""
        self.render.mark_need_restage()
        self.canvas.update()

    def force_repaint(self):
        """用于主动刷新"""
        self.canvas.update()

    def show(self):
        self.visible = True
        self.force_restage()

    def hide(self):
        self.visible = False
        self.force_restage()
