import os
from PySide6.QtCore import QSize, QPoint, QRect

from visual_plat.render_layer.layer_base import *
from visual_plat.shared.static.custom_2d import rects_intersection, size2rect, max_2d
from visual_plat.data_service.grid_agent.aoi_agent import AoiAgent
from visual_plat.global_proxy.config_proxy import ConfigProxy


class AoiLayer(LayerBase):
    def __init__(self, canvas):
        super(AoiLayer, self).__init__(canvas)
        """初始化AOI图层"""
        self.agent = AoiAgent()
        self.aoi_sample = QRect()
        aoi_img = self.agent.get_aoi_map()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        self.aoi_size = self.aoi_map.size()
        self.aoi_rect = size2rect(self.aoi_size)
        self.config = ConfigProxy.layer("aoi")
        self.should_save = self.config["save_image"]
        self.save_path = self.config["save_path"]
        self.should_auto_back = self.config["auto_back"]
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        self.index = 0

    def save_img(self, img: QPixmap):
        """放大并保存图片"""
        new_img = QPixmap(QSize(100, 100))
        new_img.fill(Qt.white)
        with QPainter(new_img) as painter:
            painter.setWindow(self.aoi_rect)
            painter.drawPixmap(QPoint(0, 0), img, self.aoi_rect)
        new_img.save(f"{self.save_path}/test[{self.index}].png")
        self.index += 1

    def auto_back(self):
        if self.should_auto_back and self.aoi_sample == QRect():
            self.canvas.animate2center()

    def on_reload(self, data=None):
        """更新AOI图层"""
        if data is not None:
            self.data = data
            self.agent.auto_read(data)
        aoi_img = self.agent.get_aoi_map()
        self.aoi_size = self.aoi_map.size()
        self.aoi_rect = size2rect(self.aoi_size)
        self.force_restage()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        if self.should_save:
            self.save_img(self.aoi_map)
        return True

    def on_stage(self, device: QPixmap):
        """在缓冲图层绘制AOI"""
        with QPainter(device) as painter:
            painter.setWindow(self.layout.window)
            painter.setViewport(self.layout.viewport)
            # 此处不采用win_sample，因为希望得到真正的取样大小
            self.aoi_sample = rects_intersection(self.layout.win_sample, self.aoi_rect)
            # 相应的，需要新的算法来调整绘制位置，尤其注重处理负绘制问题
            draw_bias = max_2d(-self.layout.window_bias, -self.layout.win_bias_dec)
            if self.aoi_sample != QRect():
                # aoi_sample 为0时，Qt默认绘制全部，因而需要避开
                painter.drawPixmap(draw_bias, self.aoi_map, self.aoi_sample)
        return True
