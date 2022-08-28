from grid_world.proxy.layer_proxy import *


class AOILayer(LayerBase):
    def __init__(self):
        super(AOILayer, self).__init__()
        """初始化AOI图层"""
        self.xps_tag = "AOI"
        aoi_img = self.data.get_aoi_info()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)

    def reload(self, data):
        """更新AOI图层"""
        self.data.read_aoi(data=data)
        aoi_img = self.data.get_aoi_info()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
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
