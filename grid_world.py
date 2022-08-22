import time

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import warnings

from deputy.layout_deputy import LayoutDeputy, GeographyInfo
from deputy.menu_deputy import MenuDeputy
from deputy.data_deputy import DataDeputy
from deputy.render_deputy import RenderDeputy
from utils.custom_2d import *

warnings.filterwarnings("ignore", category=DeprecationWarning)


class GridWorld(QWidget):
    def __init__(self):
        super(GridWorld, self).__init__()
        self.resize(1000, 800)

        self.on_drag = False  # 正在拖动
        self.on_frame = False  # 正在框选
        self.framed = False  # 已经框选某个矩形

        self.last_mouse_pos: QPoint = QPoint()  # 上次记录的鼠标坐标
        self.press_start_pos: QPoint = QPoint()  # 上次鼠标按下的坐标

        # Deputies
        self.data_deputy = DataDeputy()
        self.layout_deputy = LayoutDeputy(
            size=self.size(),
            pos_bias=QPoint(-50, -50),
            geo_info=GeographyInfo(
                locate=QPointF(116.400, 39.910),
                eastern=True,
                southern=False
            )
        )
        self.render_deputy = RenderDeputy(self, self.layout_deputy, self.data_deputy)
        self.menu_deputy = MenuDeputy(self, tooltip=self.render_deputy.tooltip_proxy.tooltip_ft)

        # Tooltip
        self.tooltip_tl = self.render_deputy.tooltip_proxy.tooltip_tl
        self.tooltip_tr = self.render_deputy.tooltip_proxy.tooltip_tr
        self.tooltip_bl = self.render_deputy.tooltip_proxy.tooltip_bl
        self.tooltip_br = self.render_deputy.tooltip_proxy.tooltip_br
        self.tooltip_ft = self.render_deputy.tooltip_proxy.tooltip_ft

        # Other
        self.tooltip_br.set("LEVEL", "0")
        self.setMouseTracking(True)  # 开启鼠标追踪

    def aoi_update(self, aoi_data: np.ndarray):
        self.data_deputy.read_aoi(data=aoi_data)
        self.render_deputy.mark_need_update(aoi=True)
        self.update()

    def paintEvent(self, event):
        """窗口刷新时被调用，完全交由 Render Deputy 代理"""
        self.render_deputy.render()

    def mousePressEvent(self, event):
        """鼠标按下时调用"""
        pos = QPoint(event.pos())
        crd = self.layout_deputy.pos2crd(pos)

        self.press_start_pos = pos
        self.tooltip_ft.show()
        self.tooltip_ft.move(pos + QPoint(10, -20))
        self.tooltip_ft.set("At", f"({crd.x()}, {crd.y()})")

        if event.button() == Qt.LeftButton:
            self.framed = False
            self.on_frame = True
            self.render_deputy.set_focus_point(crd)
        elif event.button() == Qt.RightButton:
            self.on_drag = True
            self.last_mouse_pos = pos
            self.setCursor(Qt.OpenHandCursor)
            self.menu_deputy.menu_allow = True

        self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动时调用"""
        crd = self.layout_deputy.pos2crd(event.pos())
        self.menu_deputy.menu_allow = False

        if not self.render_deputy.enable_base_lines:
            self.render_deputy.enable_base_lines = True
            self.render_deputy.mark_need_repaint()

        self.render_deputy.tooltip_proxy.tooltip_ft.hide()
        self.render_deputy.tooltip_proxy.tooltip_bl.set("CRD", f"({crd.x()}, {crd.y()})")
        self.render_deputy.tooltip_proxy.tooltip_bl.set("POS", f"({event.x()}, {event.y()})")

        if self.on_drag:
            pos = event.pos()
            self.layout_deputy.translate(self.last_mouse_pos - pos)
            self.last_mouse_pos = pos
            self.render_deputy.enable_base_lines = False
            self.render_deputy.mark_need_repaint()
        elif self.on_frame:
            self.framed = True
            start = self.layout_deputy.pos2crd(self.press_start_pos)
            end = crd
            area = area_of_points([start, end])
            self.render_deputy.set_focus_rect(area)
        else:
            self.last_mouse_pos = event.pos()
            if not self.framed:
                self.render_deputy.set_focus_point(crd)

        self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放时调用"""
        self.setCursor(Qt.ArrowCursor)

        self.on_drag = False
        self.on_frame = False

        self.render_deputy.enable_base_lines = True
        self.render_deputy.mark_need_repaint()

        self.tooltip_bl.set("POS")
        self.tooltip_tl.set("FPS")

        self.update()

    def wheelEvent(self, event):
        """滚动鼠标滚轮时调用"""
        self.layout_deputy.zoom_at(event.angleDelta().y(), self.last_mouse_pos)

        self.render_deputy.enable_base_lines = False  # 优化性能
        self.render_deputy.mark_need_repaint()

        self.tooltip_br.set("LEVEL", str(self.layout_deputy.grid_level))

        self.update()

    def resizeEvent(self, event):
        """改变窗口大小时调用"""
        self.layout_deputy.resize(event.size())
        self.render_deputy.mark_need_repaint()

        self.update()
