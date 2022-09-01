from PySide6.QtWidgets import QWidget
from PySide6.QtGui import *

from grid_world.utils.color_set import ColorSet
from grid_world.utils.custom_2d import *
from grid_world.utils.xps_checker import XPSChecker
from grid_world.proxy.layer_proxy import LayerProxy
from grid_world.proxy.tooltip_proxy import TooltipProxy


class RenderDeputy:
    def __init__(self, device: QWidget):
        self.device = device

        # Layers
        self.layers: list[LayerProxy] = []

        # 视图缓冲图层
        self.buff_map: QPixmap = QPixmap(self.device.size())

        # 是否需要重绘缓冲图层
        self.need_restage = True

        # 提示工具
        self.tooltip_proxy = TooltipProxy(self.device, anchor_bias=QPointF(90, 50))

        # 性能测算工具
        self.xps = XPSChecker(self.tooltip_proxy.tooltip_tl)

    def render(self):
        """用于全部更新"""
        self.tooltip_proxy.relocate(self.device.size())
        self.xps.set_tooltip(self.tooltip_proxy.tooltip_tl)
        self.xps.start()

        if self.need_restage:
            # 绘制视图缓冲图层
            self.need_restage = False
            self.buff_map = QPixmap(self.device.size())
            self.buff_map.fill(ColorSet.named["Background"])
            self.xps.check("BINI")
            for layer in self.layers:
                if layer.visible:
                    res = layer.on_stage(device=self.buff_map)
                    if res and layer.xps_tag != "":
                        self.xps.check(layer.xps_tag)

        self.xps.set_tooltip(self.tooltip_proxy.tooltip_tr)

        # 将缓冲图层绘制到屏幕
        with QPainter(self.device) as painter:
            painter.drawPixmap(QPoint(0, 0), self.buff_map)

        # 将视图图层绘制到屏幕
        self.xps.check("DPS")
        for layer in self.layers:
            if layer.visible:
                res = layer.on_paint(device=self.device)
                if res and layer.xps_tag != "":
                    self.xps.check(layer.xps_tag)

        self.tooltip_proxy.draw()  # 绘制提示
        self.xps.check("FPS", dif_from="")

    def mark_need_restage(self):
        """标记需要重绘"""
        self.need_restage = True
