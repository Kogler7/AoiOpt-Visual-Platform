from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import warnings

from grid_world.deputy.layout_deputy import LayoutDeputy, GeographyInfo
from grid_world.deputy.menu_deputy import MenuDeputy
from grid_world.deputy.data_deputy import DataDeputy
from grid_world.deputy.render_deputy import RenderDeputy
from grid_world.deputy.state_deputy import StateDeputy
from grid_world.utils.custom_2d import *
from grid_world.proxy.layer_proxy import LayerBase
from grid_world.layers.built_in.aoi_layer import AOILayer
from grid_world.layers.built_in.trace_layer import TraceLayer
from grid_world.layers.built_in.parcel_layer import ParcelLayer
from grid_world.layers.built_in.grid_layer import GridLayer
from grid_world.layers.built_in.scale_layer import ScaleLayer
from grid_world.layers.built_in.focus_layer import FocusLayer

warnings.filterwarnings("ignore", category=DeprecationWarning)


class GridWorld(QWidget):
    def __init__(self):
        super(GridWorld, self).__init__()
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
        self.state_deputy = StateDeputy()
        self.render_deputy = RenderDeputy(self)
        self.menu_deputy = MenuDeputy(self, tooltip=self.render_deputy.tooltip_proxy.tooltip_ft)

        self.state_deputy.dragging_signal.connect(self.dragging_slot)
        self.state_deputy.zooming_signal.connect(self.zooming_slot)

        # Layers
        LayerBase.bind(self)
        self.aoi_layer = AOILayer()
        self.trace_layer = TraceLayer()
        self.parcel_layer = ParcelLayer()
        self.gird_layer = GridLayer()
        self.scale_layer = ScaleLayer()
        self.focus_layer = FocusLayer()

        # TooltipProxy
        self.tooltip_proxy = self.render_deputy.tooltip_proxy
        self.tooltip_proxy.tooltip_br.set("LEVEL", "0")

        # Other
        self.setMouseTracking(True)  # 开启鼠标追踪

    def paintEvent(self, event):
        """窗口刷新时被调用，完全交由 Render Deputy 代理"""
        self.render_deputy.render()

    def mousePressEvent(self, event):
        """鼠标按下时调用"""
        event = self.layout_deputy.wrap_event(event)
        self.state_deputy.on_mouse_press(event)

        self.tooltip_proxy.tooltip_ft.show()
        self.tooltip_proxy.tooltip_ft.move(event.pos + QPoint(10, -20))
        self.tooltip_proxy.tooltip_ft.set("At", f"({event.crd.x()}, {event.crd.y()})")

        self.update()

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
        if on_drag:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.render_deputy.mark_need_restage()

    def zooming_slot(self, on_zoom: bool):
        if not on_zoom:
            self.render_deputy.mark_need_restage()
            # self.update()
