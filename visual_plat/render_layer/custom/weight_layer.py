from visual_plat.render_layer.auto.async_layer import *
from utils.pre_cauculate import PreCalculate


class WeightLayer(LayerBase):
    def __init__(self):
        super(WeightLayer, self).__init__()
        self.data_map = PreCalculate().create_map()

    def on_stage(self, device: QPixmap):
        if self.layout.win2view_factor < 30:
            # 太小了看不清不要了
            return False
        with QPainter(device) as painter:
            factor = self.layout.win2view_factor
            for y in range(self.data_map.shape[0]):
                for x in range(self.data_map.shape[1]):
                    loc = self.layout.crd2pos(QPoint(x, y))
                    rt_loc = loc + QPoint(factor, factor / 2)
                    bt_loc = loc + QPoint(factor / 2 - 5, factor)
                    painter.drawText(rt_loc, str(self.data_map[y][x][1]))
                    painter.drawText(bt_loc, str(self.data_map[y][x][0]))
        return True
