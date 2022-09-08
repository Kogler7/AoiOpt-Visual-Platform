from visual_plat.render_layer.layer_base import *
from visual_plat.utility.static.custom_2d import *
from visual_plat.utility.static.color_set import ColorSet


class FocusLayer(LayerBase):
    def __init__(self):
        super(FocusLayer, self).__init__()
        self.level = 3
        self.focus_brush = QBrush(QColor(255, 255, 255, 100))
        self.focus_rect_pen = QPen(ColorSet.named["LightGrey"])
        self.focus_rect_pen.setWidth(3)

    def on_paint(self, device: QWidget):
        """绘制聚焦框"""
        with QPainter(device) as painter:
            if self.state.focus_rect:
                tl = self.layout.crd2pos(self.state.focus_rect.topLeft())
                br = self.layout.crd2pos(self.state.focus_rect.bottomRight() + QPoint(1, 1))
            else:
                tl = self.layout.crd2pos(self.state.focus_point)
                br = self.layout.crd2pos(self.state.focus_point + QPoint(1, 1))
            rect = QRect(tl, br)
            painter.fillRect(rect, self.focus_brush)
            painter.setPen(self.focus_rect_pen)
            painter.drawRect(rect)
        return True
