import time

from PySide6.QtCore import QPoint, QPointF

from visual_plat.layers.layer_base import *
import pandas as pd


class RealLayer(LayerBase):
    def __init__(self, canvas):
        super(RealLayer, self).__init__(canvas)
        self.data = None

    def load_rpkg(self, path):
        data = pd.read_csv(path).head(50000)
        area_id = data['area_id']
        courier_id = data['courier_id']
        timestamp = data['time']
        lng = data['lng']
        lat = data['lat']
        data_map: dict[str, list[QPoint]] = dict()
        for i in range(len(courier_id)):
            if courier_id[i] is None or lng[i] is None or lat[i] is None:
                print("Real Layer: Invalid data.", area_id[i], lng[i], lat[i])
                continue
            if courier_id[i] not in data_map:
                data_map[courier_id[i]] = []
            data_map[courier_id[i]].append(QPointF(lng[i], lat[i]))
        self.data = data_map
        self.force_restage()

    def on_stage(self, device: QWidget):
        rect = self.layout.win_sample
        if self.data:
            with QPainter(device) as painter:
                painter.setPen(QPen(QColor(0, 0, 0, 100), 3))
                for courier_id in self.data:
                    last_p = None
                    for point in self.data[courier_id]:
                        crd = self.layout.geo2crd(point)
                        pos = self.layout.crd2pos(crd)
                        painter.drawPoint(pos)
                        if last_p is not None:
                            painter.drawLine(last_p, pos)
                        last_p = pos
