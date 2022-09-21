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
from visual_plat.shared.utility.status_bar import StatusBar
from visual_plat.shared.utility.notifier.key_notifier import KeyEventNotifier

from visual_plat.global_proxy.config_proxy import ConfigProxy
from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.global_proxy.update_proxy import UpdateProxy

from visual_plat.render_layer.layer_base import LayerBase
from visual_plat.render_layer.builtin.aoi_layer import AoiLayer

warnings.filterwarnings("ignore", category=DeprecationWarning)


class VisualCanvas(QWidget):
    instance_list: list = []

    def __new__(cls, *args, **kwargs):
        if not ConfigProxy.loaded:
            ConfigProxy.load()
        instance = super(VisualCanvas, cls).__new__(cls)
        cls.instance_list.append(instance)
        return instance

    @staticmethod
    def instance(idx: int = 0):
        return VisualCanvas.instance_list[idx]

    def __init__(self, pre_processor=None):
        super(VisualCanvas, self).__init__()
        # 载入配置信息
        version = str(ConfigProxy.canvas('version')) \
                  + ("-pre" if not ConfigProxy.canvas("release") else "")
        self.setWindowTitle(f"AoiOpt Visual Platform {version}")

        # status 在设置窗口标题之后
        self.status_bar = StatusBar(self, self.set_window_title)

        init_size = ConfigProxy.canvas("init_size")
        self.resize(init_size[0], init_size[1])

        # Layers
        self.layer_dict: dict[str] = {}
        self.layer_list: list[LayerBase] = []

        # Deputies
        self.tooltip_deputy = TooltipDeputy(self)
        self.state_deputy = StateDeputy(layers=self.layer_dict, status_bar=self.status_bar)
        self.event_deputy = EventDeputy(self)
        self.render_deputy = RenderDeputy(self, layers=self.layer_list, tooltip=self.tooltip_deputy)
        self.layout_deputy = LayoutDeputy(size=self.size())
        self.menu_deputy = MenuDeputy(self, self.render_deputy.tooltip_deputy.anchor_tips["cursor"])

        # Layers 载入，需要在 Deputy 声明后完成
        layers_config = ConfigProxy.get("layers")
        self.load_layers(layers_config)
        self.aoi_layer: AoiLayer = self.layer_dict["aoi"]

        # TooltipProxy
        self.tooltip_proxy = self.render_deputy.tooltip_deputy
        self.tooltip_proxy.anchor_tips["btm_rgt"].set("LEVEL", "0")

        # Other
        self.setMouseTracking(True)  # 开启鼠标追踪
        self.setAcceptDrops(True)  # 接受拖拽
        self.show_tooltips = ConfigProxy.tooltip("visible")

        # 预处理
        if pre_processor:
            pre_processor(self)

        # Teleport
        self.animate2center()

        # 在StateDeputy之后
        UpdateProxy.set_canvas(self)

        # 新窗口
        self.new_canvas = None

        # 事件监听
        self.key_notifier = KeyEventNotifier()
        self.last_load()

    def set_window_title(self, title: str):
        self.setWindowTitle(title)

    def load_layers(self, layers_cfg: dict):
        pth_base = "visual_plat.render_layer."
        mod_back = "_layer"
        nme_back = "Layer"
        for cls, layers in layers_cfg.items():
            mod_base = pth_base + cls + '.'
            for tag, layer_info in layers.items():
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
                if "event" in layer_info.keys():
                    self.event_deputy.bind_layer_event(layer_obj, layer_info["event"])
                self.layer_dict[tag] = layer_obj
                self.layer_list.append(layer_obj)
        # 根据层级排序
        self.layer_list.sort(key=lambda layer: layer.level, reverse=False)

    def paintEvent(self, event):
        """窗口刷新时被调用，完全交由 Render Deputy 代理"""
        self.render_deputy.render()
        if self.show_tooltips:
            self.tooltip_deputy.draw()

    def mousePressEvent(self, event):
        """鼠标按下时调用"""
        event = self.layout_deputy.wrap_event(event)
        self.event_deputy.on_mouse_press(event)

        if self.event_deputy.on_sliding:
            self.setCursor(Qt.SizeAllCursor)
            AsyncProxy.run(self.on_sliding)
        elif not self.event_deputy.on_dragging:
            self.setCursor(Qt.ArrowCursor)

        self.tooltip_proxy.anchor_tips["cursor"].show()
        self.tooltip_proxy.anchor_tips["cursor"].move(event.pos + QPoint(10, -20))
        self.tooltip_proxy.anchor_tips["cursor"].set("At", f"({event.crd.x()}, {event.crd.y()})")

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

        self.render_deputy.tooltip_deputy.anchor_tips["cursor"].hide()
        self.render_deputy.tooltip_deputy.anchor_tips["btm_lft"].set("CRD", f"({event.crd.x()}, {event.crd.y()})")
        self.render_deputy.tooltip_deputy.anchor_tips["btm_lft"].set("POS", f"({event.pos.x()}, {event.pos.y()})")

        self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放时调用"""
        self.event_deputy.on_mouse_release(event)

        self.tooltip_proxy.anchor_tips["btm_lft"].set("POS")
        self.tooltip_proxy.anchor_tips["top_lft"].set("FPS")

        self.update()

    def wheelEvent(self, event):
        """滚动鼠标滚轮时调用"""
        self.event_deputy.on_mouse_wheel(event)
        self.layout_deputy.zoom_at(event.angleDelta().y(), self.event_deputy.last_mouse_pos)

        self.tooltip_proxy.anchor_tips["btm_rgt"].set("LEVEL", str(self.layout_deputy.grid_level))

        self.render_deputy.mark_need_restage()
        self.update()

    def create_new_canvas(self):
        """创建新画布"""
        self.new_canvas = VisualCanvas()
        self.new_canvas.setWindowTitle("New Canvas")
        self.new_canvas.status_bar.set_default("New Canvas")
        self.new_canvas.show()

    def snapshot_and_create_new_canvas(self):
        """截图并创建新画布"""
        path, _ = self.state_deputy.snapshot()

        def pre_setter(canvas: VisualCanvas):
            rcd = canvas.state_deputy.load_record(path)
            canvas.state_deputy.apply_snapshot(rcd)
            canvas.status_bar.set_default("New Canvas")

        self.new_canvas = VisualCanvas(pre_processor=pre_setter)
        self.new_canvas.setWindowTitle("New Canvas")
        self.new_canvas.show()

    def record(self):
        """记录"""
        if self.state_deputy.recording:
            self.state_deputy.stop_record()
        else:
            self.state_deputy.start_record()

    def keyPressEvent(self, event: QKeyEvent):
        self.key_notifier.invoke(event.modifiers(), event.key())
        self.event_deputy.on_key_pressed(event)

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
        rcd_name = rcd_path.split("/")[-1][:-4]
        rcd = self.state_deputy.load_record(rcd_path)
        if not hasattr(rcd, 'comp_idx'):
            print("RECORD has no COMPATIBLE INDEX. [It may be derived from ANCIENT versions]")
        elif rcd.comp_idx != ConfigProxy.record("compatible_index"):
            print(f"The RECORD is not COMPATIBLE with this VERSION of canvas. "
                  f"[{rcd.comp_idx} != {ConfigProxy.record('compatible_index')}]")
        else:
            self.state_deputy.start_replay(rcd, rcd_name)
            self.animate2center()

    def resizeEvent(self, event):
        """改变窗口大小时调用"""
        self.layout_deputy.resize(event.size())
        self.render_deputy.mark_need_restage()
        self.update()

    def last_load(self):
        """在最后执行，以等待类的所有属性方法载入完毕"""
        self.key_notifier.parse(ConfigProxy.event(), self)
