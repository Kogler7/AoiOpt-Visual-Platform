from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from abc import ABC, abstractmethod
from grid_world.utils.custom_2d import *
from grid_world.proxy.async_proxy import *


class LayerProxy:

    @classmethod
    def bind(cls, base):
        """与GridWorld绑定，请在实例化GridWorld时调用"""
        cls.base = base
        cls.data = base.data_deputy
        cls.state = base.state_deputy
        cls.render = base.render_deputy
        cls.layout = base.layout_deputy
        cls.layers: list[LayerProxy] = base.render_deputy.layers

    def __new__(cls, *args, **kwargs):
        self = super(LayerProxy, cls).__new__(cls)
        self.level = 0
        self.layers.append(self)
        self.layers.sort(key=lambda layer: layer.level, reverse=False)
        return self

    def __init__(self):
        self.level = 0
        self.xps_tag = ""
        self.visible = True

    def __del__(self):
        self.render.layers.remove(self)

    def set_level(self, level: int):
        """调整层级关系"""
        self.level = level
        self.layers.sort(key=lambda layer: layer.level, reverse=False)

    def reload(self, data):
        """全局更新时调用"""
        return False

    def force_restage(self):
        """用于主动更新"""
        self.render.mark_need_restage()
        self.base.update()

    def force_repaint(self):
        """用于主动刷新"""
        self.base.update()

    def update(self, data):
        """局部更新时调用"""
        return False

    def on_stage(self, device: QPixmap):
        """重绘buff图层时自动调用"""
        return False

    def on_paint(self, device: QWidget):
        """重绘时自动调用"""
        return False

    def show(self):
        self.visible = True
        self.force_restage()

    def hide(self):
        self.visible = False
        self.force_restage()


