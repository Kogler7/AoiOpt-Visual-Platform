from visual_plat.render_layer.layer_base import *
from visual_plat.utility.static.custom_2d import *
from visual_plat.utility.static.color_set import ColorSet
from visual_plat.data_agent.traj_agent import TrajAgent
from tqdm import tqdm


class TrajLayer(LayerBase):
    def __init__(self):
        super(TrajLayer, self).__init__()
        self.level = -2
        self.xps_tag = "TPS"
        self.agent = TrajAgent()
        self.traj_indexes = []
        self.trace_maps: dict[int, QPixmap] = {}
        self.trace_area_dict: dict[int, QRect] = {}
        self.enable_dot_line = True  # 是否使用点线绘制轨迹
        self.dot_back_line_pen = QPen(ColorSet.named["LightGrey"])
        """初始化轨迹图层"""
        self.reload()

    def set_indexes(self, indexes):
        self.traj_indexes = indexes
        self.reload()

    def draw_dot_line(self, painter: QPainter, fst: QPoint, sec: QPoint):
        """绘制点线"""
        if self.enable_dot_line:
            pen = painter.pen()
            self.dot_back_line_pen.setWidth(pen.width() + 2)
            painter.setPen(self.dot_back_line_pen)
            painter.drawLine(fst, sec)
            pen.setStyle(Qt.CustomDashLine)
            pen.setDashPattern([5, 1, 1, 5])
            painter.setPen(pen)
        painter.drawLine(fst, sec)

    def reload(self, data=None):
        if data:
            self.traj_indexes: list[int] = data
        if self.traj_indexes:
            lst = self.agent.get_trace(self.traj_indexes)
            with tqdm(total=len(lst)) as t:
                for trace in lst:
                    t.update()
                    t.set_description_str("Painting traces")
                    bias = rect_bias(trace.area)
                    self.trace_area_dict[trace.index] = trace.area
                    pixmap = QPixmap(trace.area.size() * 15)
                    pixmap.fill(QColor(0, 0, 0, 0))
                    pen = QPen(trace.color)
                    with QPainter(pixmap) as painter:
                        painter.setPen(pen)
                        nt = []
                        for p in trace.p_lst:
                            _p = (p - bias) * 15
                            nt.append(_p + QPoint(7, 7))
                        for i in range(1, len(nt)):
                            self.draw_dot_line(painter, nt[i - 1], nt[i])
                    self.trace_maps[trace.index] = pixmap
        self.force_restage()
        return True

    def on_stage(self, device: QPixmap):
        """在缓冲图层绘制轨迹"""
        with QPainter(device) as painter:
            def draw_trace_at(idx: int):
                area = self.trace_area_dict[idx]
                if rect_overlap(area, layout.sample):
                    _map = self.trace_maps[idx]
                    _loc = - layout.window_bias + area.topLeft()
                    painter.drawPixmap(_loc * 15, _map)

            layout = self.layout
            painter.setWindow(mul_rect(layout.window, 15))
            painter.setViewport(layout.viewport)
            if self.traj_indexes != [-1]:
                for i in self.traj_indexes:
                    if i in self.trace_maps.keys():
                        draw_trace_at(i)
            else:
                for i in self.trace_maps.keys():
                    draw_trace_at(i)
        return True
