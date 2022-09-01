import time

from grid_world.layers.auto_base.async_layer import *


class WeightAsyncLayer(AutoAsyncLayer):
    def __init__(self):
        super(WeightAsyncLayer, self).__init__()
        self.data_size = QSize(100, 100)

    def draw_each(self, device: QImage, coord: QPoint, scale: int):
        offset = coord * scale
        with QPainter(device) as painter:
            painter.fillRect(QRect(offset, QSize(scale, scale)), QBrush(QColor(0, 0, 0)))
        time.sleep(0.05)
