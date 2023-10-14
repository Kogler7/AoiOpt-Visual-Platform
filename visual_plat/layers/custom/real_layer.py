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
        lng = data['lng']
        lat = data['lat']
        data_map: dict[str, list[QPoint]] = dict()
        for i in range(len(area_id)):
            if area_id[i] is None or lng[i] is None or lat[i] is None:
                print("Real Layer: Invalid data.", area_id[i], lng[i], lat[i])
                continue
            if area_id[i] not in data_map:
                data_map[area_id[i]] = []
            data_map[area_id[i]].append(QPointF(lng[i], lat[i]))
        self.data = data_map
        self.force_restage()

    def on_stage(self, device: QWidget):
        rect = self.layout.win_sample
        if self.data:
            with QPainter(device) as painter:
                painter.setPen(QPen(QColor(0, 0, 0, 100), 2))
                for area_id in self.data:
                    for point in self.data[area_id]:
                        crd = self.layout.geo2crd(point)
                        if rect.contains(crd.toPoint()):
                            painter.drawPoint(self.layout.crd2pos(crd))
