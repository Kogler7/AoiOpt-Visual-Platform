from visual_plat.layers.auto.async_layer import *


class WeightLayer(LayerBase):
    def __init__(self, canvas):
        super(WeightLayer, self).__init__(canvas)
        self.data = None

    def on_reload(self, data):
        self.data = data
        self.force_restage()

    def on_stage(self, device: QPixmap):
        if self.layout.win2view_factor < 30:
            # 太小了看不清不要了
            return False
        with QPainter(device) as painter:
            factor = self.layout.win2view_factor
            if self.data is not None:
                for y in range(self.data.shape[0]):
                    for x in range(self.data.shape[1]):
                        loc = self.layout.crd2pos(QPoint(x, y))
                        rt_loc = loc + QPoint(factor, factor / 2)
                        bt_loc = loc + QPoint(factor / 2 - 5, factor)
                        painter.drawText(rt_loc, str(self.data[y][x][1]))
                        painter.drawText(bt_loc, str(self.data[y][x][0]))
        return True
