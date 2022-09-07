from visual_plat.layers.auto.async_layer import *
from visual_plat.utils.anchor_tip import AnchorTip, AnchorLocate


class InfoLayer(LayerProxy):
    def __init__(self):
        super(InfoLayer, self).__init__()
        self.tooltip = AnchorTip(anchor=AnchorLocate.top_lft, locate=QPoint(90, 100))
        self.action = (0, 0, 0)
        self.reward = (0, 0, 0)
        self.time = (0, 0)
        self.dir_lst = ['↑', '↓', '←', '→', '*']

    def reload(self, data):
        self.action = data[1]
        self.reward = data[2]
        self.time = data[3]  # epoch, step

    def on_paint(self, device: QWidget):
        with QPainter(device) as painter:
            crd = QPoint(self.action[0], self.action[1])
            pos = self.layout.crd2pos(crd)
            act = self.action[2]
            fac = self.layout.win2view_factor
            rect = QRect(pos, square_size(fac))
            painter.fillRect(rect, QBrush(QColor(255, 255, 255, 200)))
            painter.setFont(QFont("等线", fac / 2, 10))
            painter.drawText(pos + QPoint(fac / 4, fac / 4 * 3), self.dir_lst[act])
        self.tooltip.set("Time", str(self.time))
        self.tooltip.set("Reward", str(self.reward))
        self.tooltip.draw(device)
