from PySide6.QtWidgets import *
from PySide6.QtGui import *


# from grid_world.deputy.data_deputy import DataDeputy
# from grid_world.deputy.state_deputy import StateDeputy
# from grid_world.deputy.render_deputy import RenderDeputy
# from grid_world.deputy.layout_deputy import LayoutDeputy


class LayerBase:
    # data: DataDeputy
    # state: StateDeputy
    # render: RenderDeputy
    # layout: LayoutDeputy

    @classmethod
    def bind(cls, base):
        """与GridWorld绑定，请在实例化GridWorld时调用"""
        cls.base = base
        cls.data = base.data_deputy
        cls.state = base.state_deputy
        cls.render = base.render_deputy
        cls.layout = base.layout_deputy

    def __new__(cls, *args, **kwargs):
        self = super(LayerBase, cls).__new__(cls)
        self.render.layers.append(self)
        return self

    def __init__(self):
        self.xps_tag = ""
        self.visible = True

    def __del__(self):
        pass

    def reload(self, data):
        """全局更新时调用"""
        return False

    def force_restage(self):
        """用于主动更新"""
        self.render.mark_need_restage()
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

    def mark_need_restage(self):
        """强制更新buff图层"""
        self.render.mark_need_restage()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
