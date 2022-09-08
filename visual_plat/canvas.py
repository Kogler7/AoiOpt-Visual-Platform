import time

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import warnings

from visual_plat.canvas_deputy.layout_deputy import LayoutDeputy, GeographyInfo
from visual_plat.canvas_deputy.menu_deputy import MenuDeputy
from visual_plat.canvas_deputy.data_deputy import DataDeputy
from visual_plat.canvas_deputy.render_deputy import RenderDeputy
from visual_plat.canvas_deputy.state_deputy import StateDeputy

from visual_plat.utility.static.custom_2d import *
from visual_plat.utility.static.bezier_curves import *

from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.render_layer.layer_base import LayerBase

from visual_plat.render_layer.builtin.aoi_layer import AoiLayer
from visual_plat.render_layer.builtin.traj_layer import TrajLayer
from visual_plat.render_layer.builtin.parcel_layer import ParcelLayer
from visual_plat.render_layer.builtin.grids_layer import GridsLayer
from visual_plat.render_layer.builtin.scale_layer import ScaleLayer
from visual_plat.render_layer.builtin.focus_layer import FocusLayer

warnings.filterwarnings("ignore", category=DeprecationWarning)


class VisualCanvas(QWidget):
    def __init__(self):
        super(VisualCanvas, self).__init__()
        self.resize(1000, 800)

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
        self.state_deputy = StateDeputy(self.zooming_slot, self.dragging_slot)
        self.render_deputy = RenderDeputy(self)
        self.menu_deputy = MenuDeputy(self, tooltip=self.render_deputy.tooltip_proxy.tooltip_ft)

        self.state_deputy.dragging_signal.connect(self.dragging_slot)
        self.state_deputy.zooming_signal.connect(self.zooming_slot)

        # Layers
        LayerBase.bind(self)
        self.aoi_layer = AoiLayer()
        self.trace_layer = TrajLayer()
        self.parcel_layer = ParcelLayer()
        self.gird_layer = GridsLayer()
        self.scale_layer = ScaleLayer()
        self.focus_layer = FocusLayer()

        # TooltipProxy
        self.tooltip_proxy = self.render_deputy.tooltip_proxy
        self.tooltip_proxy.tooltip_br.set("LEVEL", "0")

        # Other
        self.setMouseTracking(True)  # 开启鼠标追踪

        # Teleport
        self.animate2center()

    def paintEvent(self, event):
        """窗口刷新时被调用，完全交由 Render Deputy 代理"""
        self.render_deputy.render()

    def mousePressEvent(self, event):
        """鼠标按下时调用"""
        event = self.layout_deputy.wrap_event(event)
        self.state_deputy.on_mouse_press(event)

        if self.state_deputy.on_sliding:
            self.setCursor(Qt.SizeAllCursor)
            AsyncProxy.run(self.on_sliding)
        elif not self.state_deputy.on_dragging:
            self.setCursor(Qt.ArrowCursor)

        self.tooltip_proxy.tooltip_ft.show()
        self.tooltip_proxy.tooltip_ft.move(event.pos + QPoint(10, -20))
        self.tooltip_proxy.tooltip_ft.set("At", f"({event.crd.x()}, {event.crd.y()})")

        self.update()

    def on_sliding(self):
        """中键滑动"""
        while self.state_deputy.on_sliding:
            delt = -(self.state_deputy.start_sliding_pos - self.state_deputy.last_mouse_pos) / 20
            self.layout_deputy.translate(delt)
            self.render_deputy.mark_need_restage()
            self.update()
            time.sleep(0.01)

    def animate_to(self, target: QPointF = QPointF(0, 0)):
        """滑动至（另起线程调用）"""

        def step():
            curve = BezierCurves.ease_in_out()
            init_bias = self.layout_deputy.window_bias
            distance = target - init_bias
            p = 0.0
            while p < 1.0:
                p += 0.05
                self.layout_deputy.teleport(init_bias + distance * curve.transform(p))
                self.render_deputy.mark_need_restage()
                self.update()
                time.sleep(0.01)

        AsyncProxy.run(step)

    def animate2center(self):
        """滑动至中心"""
        target = self.layout_deputy.get_central_bias(self.aoi_layer.size)
        self.animate_to(-target)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            """滑动回原点"""
            self.setCursor(Qt.ArrowCursor)
            self.state_deputy.on_sliding = False
            self.animate2center()

    def mouseMoveEvent(self, event):
        """鼠标移动时调用"""
        if self.state_deputy.on_dragging:
            self.layout_deputy.translate(self.state_deputy.last_mouse_pos - event.pos())
            self.render_deputy.mark_need_restage()

        event = self.layout_deputy.wrap_event(event)
        self.state_deputy.on_mouse_move(event)

        self.render_deputy.tooltip_proxy.tooltip_ft.hide()
        self.render_deputy.tooltip_proxy.tooltip_bl.set("CRD", f"({event.crd.x()}, {event.crd.y()})")
        self.render_deputy.tooltip_proxy.tooltip_bl.set("POS", f"({event.pos.x()}, {event.pos.y()})")

        self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放时调用"""
        self.state_deputy.on_mouse_release()

        self.tooltip_proxy.tooltip_bl.set("POS")
        self.tooltip_proxy.tooltip_tl.set("FPS")

        self.update()

    def wheelEvent(self, event):
        """滚动鼠标滚轮时调用"""
        self.state_deputy.on_mouse_wheel()
        self.layout_deputy.zoom_at(event.angleDelta().y(), self.state_deputy.last_mouse_pos)

        self.tooltip_proxy.tooltip_br.set("LEVEL", str(self.layout_deputy.grid_level))

        self.render_deputy.mark_need_restage()
        self.update()

    def resizeEvent(self, event):
        """改变窗口大小时调用"""
        self.layout_deputy.resize(event.size())
        self.render_deputy.mark_need_restage()
        self.update()

    def dragging_slot(self, on_drag: bool):
        """Drag回调函数"""
        if on_drag:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.render_deputy.mark_need_restage()

    def zooming_slot(self, on_zoom: bool):
        """Zoom回调函数"""
        if not on_zoom:
            self.render_deputy.mark_need_restage()
            self.update()
