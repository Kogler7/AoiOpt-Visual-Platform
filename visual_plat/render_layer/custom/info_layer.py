from visual_plat.render_layer.auto.async_layer import *
from visual_plat.shared.utility.anchor_tip import AnchorTip, AnchorLocate


class InfoLayer(LayerBase):
    def __init__(self, canvas):
        super(InfoLayer, self).__init__(canvas)
        self.tooltip = AnchorTip(anchor=AnchorLocate.top_lft, anchor_bias=QPoint(90, 100))
        canvas.tooltip_deputy.add_anchor_tip("info", self.tooltip)
        self.action = (0, 0, 0)
        self.reward = (0, 0, 0)
        self.time = (0, 0)
        self.data = (self.action, self.reward, self.time)
        self.dir_lst = ['↑', '↓', '←', '→', '*']

    def reload(self, data):
        self.data = data
        if data:
            self.action, self.reward, self.time = data

    def on_paint(self, device: QWidget):
        if self.data and self.layout.win2view_factor > 10:
            with QPainter(device) as painter:
                crd = QPoint(self.action[0], self.action[1])
                pos = self.layout.crd2pos(crd)
                act = self.action[2]
                fac = self.layout.win2view_factor + 1
                rect = QRect(pos, square_size(fac))
                painter.fillRect(rect, QBrush(QColor(255, 255, 255, 200)))
                painter.setFont(QFont("等线", fac / 2, 10))
                painter.drawText(pos + QPoint(fac / 4, fac / 4 * 3), self.dir_lst[act])
            self.tooltip.set("Time", str(self.time))
            self.tooltip.set("Reward", str(self.reward))
