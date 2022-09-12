import time
from importlib import import_module

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import warnings

from visual_plat.canvas_deputy.layout_deputy import LayoutDeputy
from visual_plat.canvas_deputy.menu_deputy import MenuDeputy
from visual_plat.canvas_deputy.state_deputy import StateDeputy
from visual_plat.canvas_deputy.render_deputy import RenderDeputy
from visual_plat.canvas_deputy.event_deputy import EventDeputy
from visual_plat.canvas_deputy.tooltip_deputy import TooltipDeputy

from visual_plat.shared.static.custom_2d import *
from visual_plat.shared.static.bezier_curves import *

from visual_plat.global_proxy.config_proxy import ConfigProxy
from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.global_proxy.update_proxy import UpdateProxy

from visual_plat.render_layer.layer_base import LayerBase
from visual_plat.render_layer.builtin.aoi_layer import AoiLayer

warnings.filterwarnings("ignore", category=DeprecationWarning)


class VisualCanvas(QWidget):
    def __init__(self, pre_processor=None):
        super(VisualCanvas, self).__init__()
        # 载入配置信息
        ConfigProxy.load()
        version = str(ConfigProxy.canvas('version')) + "-pre" \
            if not ConfigProxy.canvas("release") else ""
        self.setWindowTitle(f"AoiOpt Visual Platform {version}")

        init_size = ConfigProxy.canvas("init_size")
        self.resize(init_size[0], init_size[1])

        # Layers
        self.layer_dict: dict[str] = {}
        self.layer_list: list[LayerBase] = []

        # Deputies
        self.tooltip_deputy = TooltipDeputy(self)
        self.state_deputy = StateDeputy(layers=self.layer_dict)
        self.event_deputy = EventDeputy(self.zooming_slot, self.dragging_slot)
        self.render_deputy = RenderDeputy(self, layers=self.layer_list, tooltip=self.tooltip_deputy)
        self.layout_deputy = LayoutDeputy(size=self.size())
        self.menu_deputy = MenuDeputy(self, tooltip=self.render_deputy.tooltip_deputy.tooltip_ft)

        self.event_deputy.dragging_signal.connect(self.dragging_slot)
        self.event_deputy.zooming_signal.connect(self.zooming_slot)

        # Layers 载入，需要在 Deputy 声明后完成
        layers_config = ConfigProxy.get("layers")
        self.load_layers(layers_config)
        self.aoi_layer: AoiLayer = self.layer_dict["aoi"]

        # TooltipProxy
        self.tooltip_proxy = self.render_deputy.tooltip_deputy
        self.tooltip_proxy.tooltip_br.set("LEVEL", "0")

        # Other
        self.setMouseTracking(True)  # 开启鼠标追踪
        self.setAcceptDrops(True)  # 接受拖拽

        # 预处理
        if pre_processor:
            pre_processor(self)

        # Teleport
        self.animate2center()

        # 在StateDeputy之后
        UpdateProxy.set_canvas(self)

        # 新窗口
        self.new_canvas = None

    def load_layers(self, layers_cfg: dict):
        pth_base = "visual_plat.render_layer."
        mod_back = "_layer"
        nme_back = "Layer"
        for cls, layers in layers_cfg.items():
            mod_base = pth_base + cls + '.'
            for layer_info in layers:
                tag: str = layer_info["tag"]
                module = mod_base + tag + mod_back
                mod = import_module(module)
                name = tag.capitalize() + nme_back
                layer_cls = getattr(mod, name)
                layer_obj = layer_cls(self)
                if "level" in layer_info.keys():
                    layer_obj.level = layer_info["level"]
                if "xps_tag" in layer_info.keys():
                    layer_obj.xps_tag = layer_info["xps_tag"]
                if "visible" in layer_info.keys():
                    layer_obj.visible = layer_info["visible"]
                self.layer_dict[tag] = layer_obj
                self.layer_list.append(layer_obj)
        # 根据层级排序
        self.layer_list.sort(key=lambda layer: layer.level, reverse=False)

    def paintEvent(self, event):
        """窗口刷新时被调用，完全交由 Render Deputy 代理"""
        self.render_deputy.render()

    def mousePressEvent(self, event):
        """鼠标按下时调用"""
        event = self.layout_deputy.wrap_event(event)
        self.event_deputy.on_mouse_press(event)

        if self.event_deputy.on_sliding:
            self.setCursor(Qt.SizeAllCursor)
            AsyncProxy.run(self.on_sliding)
        elif not self.event_deputy.on_dragging:
            self.setCursor(Qt.ArrowCursor)

        self.tooltip_proxy.tooltip_ft.show()
        self.tooltip_proxy.tooltip_ft.move(event.pos + QPoint(10, -20))
        self.tooltip_proxy.tooltip_ft.set("At", f"({event.crd.x()}, {event.crd.y()})")

        self.update()

    def on_sliding(self):
        """中键滑动"""
        while self.event_deputy.on_sliding:
            delt = -(self.event_deputy.start_sliding_pos - self.event_deputy.last_mouse_pos) / 20
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
            self.event_deputy.on_sliding = False
            self.animate2center()

    def mouseMoveEvent(self, event):
        """鼠标移动时调用"""
        if self.event_deputy.on_dragging:
            self.layout_deputy.translate(self.event_deputy.last_mouse_pos - event.pos())
            self.render_deputy.mark_need_restage()

        event = self.layout_deputy.wrap_event(event)
        self.event_deputy.on_mouse_move(event)

        self.render_deputy.tooltip_deputy.tooltip_ft.hide()
        self.render_deputy.tooltip_deputy.tooltip_bl.set("CRD", f"({event.crd.x()}, {event.crd.y()})")
        self.render_deputy.tooltip_deputy.tooltip_bl.set("POS", f"({event.pos.x()}, {event.pos.y()})")

        self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放时调用"""
        self.event_deputy.on_mouse_release()

        self.tooltip_proxy.tooltip_bl.set("POS")
        self.tooltip_proxy.tooltip_tl.set("FPS")

        self.update()

    def wheelEvent(self, event):
        """滚动鼠标滚轮时调用"""
        self.event_deputy.on_mouse_wheel()
        self.layout_deputy.zoom_at(event.angleDelta().y(), self.event_deputy.last_mouse_pos)

        self.tooltip_proxy.tooltip_br.set("LEVEL", str(self.layout_deputy.grid_level))

        self.render_deputy.mark_need_restage()
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            if event.modifiers() == Qt.ControlModifier:
                self.state_deputy.block()  # Ctrl+Space 阻塞
            else:
                self.state_deputy.pause()  # Space 暂停
        # Ctrl+N 创建新窗口
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_N:
            self.new_canvas = VisualCanvas()
            self.new_canvas.setWindowTitle("New Canvas")
            self.new_canvas.show()
        # Ctrl+Shift+N 截图并创建新窗口
        elif event.modifiers() == Qt.ControlModifier | Qt.ShiftModifier and event.key() == Qt.Key_N:
            path = self.state_deputy.snapshot()

            def pre_setter(canvas: VisualCanvas):
                rcd = canvas.state_deputy.load_record(path)
                canvas.state_deputy.start_replay(rcd)

            self.new_canvas = VisualCanvas(pre_processor=pre_setter)
            self.new_canvas.setWindowTitle("New Canvas")
            self.new_canvas.show()
        # Ctrl+S 截图
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.state_deputy.snapshot()
        # Ctrl+R 录制
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_R:
            self.state_deputy.start_record()
        # Escape 终止
        elif event.key() == Qt.Key_Escape:
            self.state_deputy.terminate()
        # Left 快退
        elif event.key() == Qt.Key_Left:
            self.state_deputy.back_forward()
        # Right 快进
        elif event.key() == Qt.Key_Right:
            self.state_deputy.fast_forward()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """检测是否拖拽rcd文件进入窗口"""
        if event.mimeData().hasUrls():
            tp = event.mimeData().urls().pop().toLocalFile()[-4:]
            if tp == ".rcd":
                event.accept()

    def dropEvent(self, event: QDropEvent):
        """放下rcd文件时触发"""
        url = event.mimeData().urls()
        rcd_path = url.pop().toLocalFile()
        rcd = self.state_deputy.load_record(rcd_path)
        self.state_deputy.start_replay(rcd)
        self.animate2center()

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
