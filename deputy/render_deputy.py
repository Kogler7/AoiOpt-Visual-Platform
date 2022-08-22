from PySide6.QtCore import QPointF, QSize, QPoint
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import *
from deputy.layout_deputy import LayoutDeputy
from deputy.data_deputy import DataDeputy
from proxy.tooltip_proxy import TooltipProxy
from utils.color_set import ColorSet
from utils.xps_checker import XPSChecker
from utils.custom_2d import *
from tqdm import tqdm, trange


class RenderDeputy:
    def __init__(self, device: QWidget, layout: LayoutDeputy, data: DataDeputy):
        self.device = device
        self.painter = QPainter()

        # Deputy
        self.layout_deputy = layout
        self.data_deputy = data

        # 视图缓冲图层
        self.buff_map: QPixmap = QPixmap(self.device.size())
        # 数据图层
        self.aoi_map: QPixmap = QPixmap()
        self.parcels_maps: dict[int, QPixmap] = {}
        self.parcels_area_dict: dict[int, QRect] = {}
        self.trace_maps: dict[int, QPixmap] = {}
        self.trace_area_dict: dict[int, QRect] = {}

        # 布尔参数
        self.need_reload = True  # 是否需要重载数据
        self.aoi_need_update = True  # 是否需要更新AOI
        self.parcels_need_update = True  # 是否需要更新包裹
        self.traces_need_update = True  # 是否需要更新轨迹
        self.need_repaint = True  # 是否需要重绘图层

        # 绘制参数
        self.enable_dot_line = True  # 是否使用点线绘制轨迹
        self.enable_crd_mark = True  # 是否标记逻辑坐标
        self.enable_geo_mark = True  # 是否标记地理坐标
        self.enable_base_lines = True  # 是否绘制基础栅格

        # 常用 QPen
        self.dot_back_line_pen = QPen(ColorSet.named["LightGrey"])
        self.focus_rect_pen = QPen(ColorSet.named["LightGrey"])
        self.focus_rect_pen.setWidth(3)

        # 聚焦框位置
        self.focus_point: QPoint = QPoint()
        self.focus_rect: QRect = QRect()

        # 数据加载列表
        self.parcels_indexes = []
        self.trace_indexes = []

        # 提示工具
        self.tooltip_proxy = TooltipProxy(self.device, anchor_bias=QPointF(90, 50))
        # 性能测算工具
        self.xps = XPSChecker(self.tooltip_proxy.tooltip_tl)

    def render(self):
        """用于全部更新"""
        self.tooltip_proxy.relocate(self.layout_deputy.size)
        self.xps.set_tooltip(self.tooltip_proxy.tooltip_tl)
        self.xps.start()

        if self.need_reload:
            # 数据图层初始化
            self.need_reload = False
            self.init_aoi_areas()
            self.init_traces()
            self.init_parcels()
            self.xps.check("INI", no_tooltip=True)

        if self.need_repaint:
            # 绘制视图缓冲图层
            self.need_repaint = False
            self.buff_map = QPixmap(self.device.size())
            self.xps.check("BGET")
            self.buff_map.fill(ColorSet.named["Background"])
            self.xps.check("BINI")
            if self.aoi_need_update:
                self.updt_aoi_areas()
            self.draw_aoi_areas()  # 绘制AOI
            self.xps.check("APS")
            self.draw_grid_lines()  # 绘制栅格
            self.xps.check("GPS")
            if self.traces_need_update:
                self.updt_traces()
            self.draw_traces()  # 绘制轨迹
            self.xps.check("TPS")
            if self.parcels_need_update:
                self.updt_parcels()
            self.draw_parcels()  # 绘制包裹
            self.xps.check("PPS")
            self.draw_scale_marks()  # 绘制刻度
            self.xps.check("SPS")

        # 将视图图层绘制到屏幕
        self.xps.set_tooltip(self.tooltip_proxy.tooltip_tr)
        self.painter.begin(self.device)
        self.painter.drawPixmap(QPoint(0, 0), self.buff_map)
        self.painter.end()
        self.xps.check("DPS")
        self.draw_focus_frame()  # 绘制聚焦框
        self.xps.check("MPS")
        self.tooltip_proxy.draw()  # 绘制提示
        self.xps.check("FPS", dif_from="")

    def mark_need_reload(self):
        """标记需要重载"""
        self.need_reload = True
        self.need_repaint = True

    def mark_need_repaint(self):
        """标记需要重绘"""
        self.need_repaint = True

    def mark_need_update(self, aoi: bool = True, parcels: bool = False, trace: bool = False):
        """标记需要更新"""
        self.aoi_need_update = aoi
        self.parcels_need_update = parcels
        self.traces_need_update = trace
        self.need_repaint = True

    def set_focus_point(self, crd: QPoint):
        """设置聚焦点"""
        self.focus_rect = None
        self.focus_point = crd

    def set_focus_rect(self, rect: QRect):
        """设置聚焦框"""
        self.focus_rect = rect

    def draw_focus_frame(self):
        """绘制聚焦框"""
        self.painter.begin(self.device)
        if self.focus_rect:
            tl = self.layout_deputy.crd2pos(self.focus_rect.topLeft())
            br = self.layout_deputy.crd2pos(self.focus_rect.bottomRight() + QPoint(1, 1))
        else:
            tl = self.layout_deputy.crd2pos(self.focus_point)
            br = self.layout_deputy.crd2pos(self.focus_point + QPoint(1, 1))
        rect = QRect(tl, br)
        self.painter.fillRect(rect, QBrush(QColor(255, 255, 255, 100)))
        self.painter.setPen(self.focus_rect_pen)
        self.painter.drawRect(rect)
        self.painter.end()

    def draw_grid_lines(self):
        """绘制栅格"""
        layout = self.layout_deputy
        size = int(layout.viewport_size)
        step = layout.grid_gap

        pen = QPen(ColorSet.named["LightGrey"])
        self.painter.begin(self.buff_map)
        self.painter.setPen(pen)

        # 绘制基础栅格
        if self.enable_base_lines:  # 优化性能
            bias = -mod_2d(layout.window_bias, layout.grid_lvl_fac) * layout.win2view_factor
            loc = bias
            while loc.x() < layout.viewport_size or loc.y() < layout.viewport_size:
                self.painter.drawLine(QPoint(0, loc.y()), QPoint(size, loc.y()))
                self.painter.drawLine(QPoint(loc.x(), 0), QPoint(loc.x(), size))
                loc += QPointF(step, step)

        # 绘制定位栅格
        pen.setWidth(2)
        self.painter.setPen(pen)
        step *= layout.grid_cov_fac
        win_bias = -mod_2d(layout.window_bias, layout.grid_lvl_fac * layout.grid_cov_fac)
        bias = win_bias * layout.win2view_factor
        loc = bias
        while loc.x() < layout.viewport_size or loc.y() < layout.viewport_size:
            self.painter.drawLine(QPoint(0, loc.y()), QPoint(size, loc.y()))
            self.painter.drawLine(QPoint(loc.x(), 0), QPoint(loc.x(), size))
            loc += QPointF(step, step)
        self.painter.end()

    def draw_scale_marks(self):
        """标记坐标"""
        layout = self.layout_deputy
        size = layout.size
        pen = QPen(ColorSet.named["LightDark"])
        pen.setWidth(3)
        self.painter.begin(self.buff_map)
        self.painter.setPen(pen)
        self.painter.setFont(QFont("等线", 12, 1))
        win_step = layout.grid_lvl_fac * layout.grid_cov_fac
        win_bias = int_2d(layout.window_bias / win_step) * win_step
        for i in range(0, int(layout.window_size), win_step):
            crd = win_bias + QPoint(i, i)
            pos = layout.crd2pos(crd) + QPoint(3, -5)  # 避免坐标标注在网格边线上
            geo = layout.crd2geo(crd)
            if self.enable_crd_mark:
                self.painter.drawText(QPoint(pos.x(), 22), f"{crd.x()}")
                self.painter.drawText(QPoint(16, pos.y()), f"{crd.y()}")
            if self.enable_geo_mark:
                self.painter.drawText(QPoint(pos.x(), size.height() - 20), "%.3f°E" % geo.x())
                self.painter.drawText(QPoint(size.width() - 80, pos.y()), "%.3f°N" % geo.y())
        self.painter.end()

    def init_aoi_areas(self):
        """初始化AOI图层"""
        aoi_img = self.data_deputy.get_aoi_info()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)

    def updt_aoi_areas(self):
        """更新AOI图层"""
        aoi_img = self.data_deputy.get_aoi_info()
        self.aoi_map: QPixmap = QPixmap.fromImage(aoi_img)

    def draw_aoi_areas(self):
        """在缓冲图层绘制AOI"""
        layout = self.layout_deputy
        self.painter.begin(self.buff_map)
        self.painter.setWindow(layout.window)
        self.painter.setViewport(layout.viewport)
        self.painter.drawPixmap(-layout.win_bias_dec, self.aoi_map, layout.sample)
        self.painter.end()

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

    def draw_arrow(self, painter: QPainter, fst: QPoint, sec: QPoint):
        """绘制带箭头的线"""
        self.draw_dot_line(painter, fst, sec)
        dt1 = QPoint(1, 1)
        dt2 = QPoint(1, 1)
        dif = sec - fst
        if dif.x() == 0:
            dt2.setX(-1)
            if dif.y() > 0:
                dt1.setY(-1)
                dt2.setY(-1)
        elif dif.y() == 0:
            dt2.setY(-1)
            if dif.x() > 0:
                dt1.setX(-1)
                dt2.setX(-1)
        painter.drawLine(sec, sec + dt1 * 7)
        painter.drawLine(sec, sec + dt2 * 7)

    def init_traces(self):
        """初始化轨迹图层"""
        if self.trace_indexes:
            lst = self.data_deputy.get_traces_info(self.trace_indexes)
            with tqdm(total=len(lst)) as t:
                for trace in lst:
                    t.update()
                    t.set_description_str("Painting traces")
                    bias = rect_bias(trace.area)
                    self.trace_area_dict[trace.index] = trace.area
                    pixmap = QPixmap(trace.area.size() * 15)
                    pixmap.fill(QColor(0, 0, 0, 0))
                    pen = QPen(trace.color)
                    self.painter.begin(pixmap)
                    self.painter.setPen(pen)
                    nt = []
                    for p in trace.p_lst:
                        _p = (p - bias) * 15
                        nt.append(_p + QPoint(7, 7))
                    for i in range(1, len(nt)):
                        self.draw_dot_line(self.painter, nt[i - 1], nt[i])
                    self.painter.end()
                    self.trace_maps[trace.index] = pixmap

    def updt_traces(self):
        """更新轨迹图层"""
        pass

    def draw_traces(self):
        """在缓冲图层绘制轨迹"""

        def draw_trace_at(idx: int):
            area = self.trace_area_dict[idx]
            if rect_overlap(area, layout.sample):
                _map = self.trace_maps[idx]
                _loc = - layout.window_bias + area.topLeft()
                self.painter.drawPixmap(_loc * 15, _map)

        layout = self.layout_deputy
        self.painter.begin(self.buff_map)
        self.painter.setWindow(mul_rect(layout.window, 15))
        self.painter.setViewport(layout.viewport)
        if self.trace_indexes != [-1]:
            for i in self.trace_indexes:
                if i in self.trace_maps.keys():
                    draw_trace_at(i)
        else:
            for i in self.trace_maps.keys():
                draw_trace_at(i)
        self.painter.end()

    def init_parcels(self):
        """初始化包裹图层"""
        if self.parcels_indexes:
            lst = self.data_deputy.get_parcels_info(self.parcels_indexes)
            brush_bk = QBrush(ColorSet.named["LightGrey"])
            step_p = QPoint(1, 1)
            step_s = QSize(-2, -2)
            with tqdm(total=len(lst)) as t:
                for parcels in lst:
                    t.update()
                    t.set_description_str("Painting parcels")
                    bias = rect_bias(parcels.area)
                    self.parcels_area_dict[parcels.index] = parcels.area
                    pixmap = QPixmap(parcels.area.size() * 10)
                    pixmap.fill(QColor(0, 0, 0, 0))
                    color = parcels.color
                    brush_id = QBrush(color)
                    self.painter.begin(pixmap)
                    for p in parcels.p_lst:
                        _p = (p - bias) * 10
                        rect = QRect(_p + step_p, QSize(8, 8))
                        self.painter.fillRect(rect, brush_id)
                        rect = trans_rect(rect, step_p, step_s)
                        self.painter.fillRect(rect, brush_bk)
                        rect = trans_rect(rect, step_p, step_s)
                        self.painter.fillRect(rect, brush_id)
                    self.painter.end()
                    self.parcels_maps[parcels.index] = pixmap

    def updt_parcels(self):
        """更新包裹图层"""
        pass

    def draw_parcels(self):
        """在缓冲图层绘制包裹"""

        def draw_parcels_at(idx: int):
            area = self.parcels_area_dict[idx]
            if rect_overlap(area, layout.sample):
                _map = self.parcels_maps[idx]
                _loc = - layout.window_bias + area.topLeft()
                self.painter.drawPixmap(_loc * 10, _map)

        layout = self.layout_deputy
        self.painter.begin(self.buff_map)
        self.painter.setWindow(mul_rect(layout.window, 10))
        self.painter.setViewport(layout.viewport)
        if self.parcels_indexes != [-1]:
            for i in self.parcels_indexes:
                if i in self.parcels_maps.keys():
                    draw_parcels_at(i)
        else:
            for i in self.parcels_maps.keys():
                draw_parcels_at(i)
        self.painter.end()
