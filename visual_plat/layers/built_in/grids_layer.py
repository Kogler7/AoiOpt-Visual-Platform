from visual_plat.proxy.layer_proxy import *
from visual_plat.utils.custom_2d import *
from visual_plat.utils.color_set import ColorSet


class GridsLayer(LayerProxy):
    def __init__(self):
        super(GridsLayer, self).__init__()
        self.level = 1
        self.xps_tag = "GPS"
        self.enable_base_lines = True  # 是否绘制基础栅格

    def on_stage(self, device: QWidget):
        """绘制栅格"""
        state = self.state
        layout = self.layout
        self.enable_base_lines = not (state.on_dragging or state.on_zooming)

        size = int(layout.viewport_size)
        step = layout.grid_gap

        pen = QPen(ColorSet.named["LightGrey"])

        with QPainter(device) as painter:
            painter.setPen(pen)

            # 绘制基础栅格
            if self.enable_base_lines:  # 优化性能
                bias = -mod_2d(layout.window_bias, layout.grid_lvl_fac) * layout.win2view_factor
                loc = bias
                while loc.x() < layout.viewport_size or loc.y() < layout.viewport_size:
                    painter.drawLine(QPoint(0, loc.y()), QPoint(size, loc.y()))
                    painter.drawLine(QPoint(loc.x(), 0), QPoint(loc.x(), size))
                    loc += QPointF(step, step)

            # 绘制定位栅格
            pen.setWidth(2)
            painter.setPen(pen)
            step *= layout.grid_cov_fac
            win_bias = -mod_2d(layout.window_bias, layout.grid_lvl_fac * layout.grid_cov_fac)
            bias = win_bias * layout.win2view_factor
            loc = bias
            while loc.x() < layout.viewport_size or loc.y() < layout.viewport_size:
                painter.drawLine(QPoint(0, loc.y()), QPoint(size, loc.y()))
                painter.drawLine(QPoint(loc.x(), 0), QPoint(loc.x(), size))
                loc += QPointF(step, step)

        return True
