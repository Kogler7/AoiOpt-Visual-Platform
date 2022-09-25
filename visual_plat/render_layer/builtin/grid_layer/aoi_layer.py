import os
from PySide6.QtCore import QSize, QPoint, QRect

from visual_plat.render_layer.layer_base import *
from visual_plat.data_service.grid_agent.aoi_agent import AoiAgent
from visual_plat.global_proxy.config_proxy import ConfigProxy


class AoiLayer(LayerBase):
    def __init__(self, canvas):
        super(AoiLayer, self).__init__(canvas)
        """初始化AOI图层"""
        self.agent = AoiAgent()
        aoi_img = self.agent.get_aoi_map()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        self.size = self.aoi_map.size()
        self.should_save = ConfigProxy.layer("builtin")["grid_layer"]["aoi"]["save_image"]
        self.save_path = ConfigProxy.layer("builtin")["grid_layer"]["aoi"]["save_path"]
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        self.index = 0

    def save_img(self, img: QPixmap):
        """放大并保存图片"""
        new_img = QPixmap(QSize(100, 100))
        new_img.fill(Qt.white)
        with QPainter(new_img) as painter:
            aoi_rect = QRect(QPoint(0, 0), self.size)
            painter.setWindow(aoi_rect)
            painter.drawPixmap(QPoint(0, 0), img, aoi_rect)
        new_img.save(f"{self.save_path}/test[{self.index}].png")
        self.index += 1

    def on_reload(self, data=None):
        """更新AOI图层"""
        if data is not None:
            self.data = data
            self.agent.auto_read(data)
        aoi_img = self.agent.get_aoi_map()
        self.size = self.aoi_map.size()
        self.force_restage()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        if self.should_save:
            self.save_img(self.aoi_map)
        return True

    def on_adjust(self, data):
        pass

    def on_stage(self, device: QPixmap):
        """在缓冲图层绘制AOI"""
        with QPainter(device) as painter:
            painter.setWindow(self.layout.window)
            painter.setViewport(self.layout.viewport)
            painter.drawPixmap(-self.layout.win_bias_dec, self.aoi_map, self.layout.sample)
        return True
