from visual_plat.render_layer.layer_base import *
from visual_plat.layer_agent.aoi_agent import AoiAgent


class AoiLayer(LayerBase):
    def __init__(self, canvas):
        super(AoiLayer, self).__init__(canvas)
        """初始化AOI图层"""
        self.agent = AoiAgent()
        aoi_img = self.agent.get_aoi_map()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        self.size = self.aoi_map.size()

    def reload(self, data=None):
        """更新AOI图层"""
        if data is not None:
            self.data = data
            self.agent.auto_read(data)
        aoi_img = self.agent.get_aoi_map()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)
        self.size = self.aoi_map.size()
        self.force_restage()
        return True

    def adjust(self, data):
        pass

    def on_stage(self, device: QPixmap):
        """在缓冲图层绘制AOI"""
        with QPainter(device) as painter:
            painter.setWindow(self.layout.window)
            painter.setViewport(self.layout.viewport)
            painter.drawPixmap(-self.layout.win_bias_dec, self.aoi_map, self.layout.sample)
        return True
