from visual_plat.proxy.layer_proxy import *
from visual_plat.utils.custom_2d import *
from visual_plat.utils.color_set import ColorSet


class ScaleLayer(LayerProxy):
    def __init__(self):
        super(ScaleLayer, self).__init__()
        self.level = 2
        self.enable_crd_mark = True  # 是否标记逻辑坐标
        self.enable_geo_mark = True  # 是否标记地理坐标

    def on_paint(self, device: QWidget):
        """标记坐标"""
        layout = self.layout
        size = layout.size
        pen = QPen(ColorSet.named["LightDark"])
        pen.setWidth(3)
        with QPainter(device) as painter:
            painter.setPen(pen)
            painter.setFont(QFont("等线", 12, 1))
            win_step = layout.grid_lvl_fac * layout.grid_cov_fac
            win_bias = int_2d(layout.window_bias / win_step) * win_step
            for i in range(0, int(layout.window_size), win_step):
                crd = win_bias + QPoint(i, i)
                pos = layout.crd2pos(crd) + QPoint(3, -5)  # 避免坐标标注在网格边线上
                geo = layout.crd2geo(crd)
                if self.enable_crd_mark:
                    painter.drawText(QPoint(pos.x(), 22), f"{crd.x()}")
                    painter.drawText(QPoint(16, pos.y()), f"{crd.y()}")
                if self.enable_geo_mark:
                    painter.drawText(QPoint(pos.x(), size.height() - 20), "%.3f°E" % geo.x())
                    painter.drawText(QPoint(size.width() - 80, pos.y()), "%.3f°N" % geo.y())

        return True
