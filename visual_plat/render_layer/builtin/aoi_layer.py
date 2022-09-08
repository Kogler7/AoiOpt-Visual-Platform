from visual_plat.render_layer.layer_base import *


class AoiLayer(LayerBase):
    def __init__(self):
        super(AoiLayer, self).__init__()
        """初始化AOI图层"""
        self.level = -3
        self.xps_tag = "AOI"
        aoi_img = self.data.get_aoi_info()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        self.size = self.aoi_map.size()

    def reload(self, data=None):
        """更新AOI图层"""
        if data is not None:
            self.data.read_aoi(data=data)
        aoi_img = self.data.get_aoi_info()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        self.size = self.aoi_map.size()
        self.force_restage()
        return True

    def update(self, data):
        pass

    def on_stage(self, device: QPixmap):
        """在缓冲图层绘制AOI"""
        with QPainter(device) as painter:
            painter.setWindow(self.layout.window)
            painter.setViewport(self.layout.viewport)
            painter.drawPixmap(-self.layout.win_bias_dec, self.aoi_map, self.layout.sample)
        return True
