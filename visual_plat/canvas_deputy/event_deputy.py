from PySide6.QtGui import *
from PySide6.QtCore import *

from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.render_layer.layer_base import LayerBase

from visual_plat.shared.static.custom_2d import *
from visual_plat.shared.utility.count_down import CountDownWorker
from visual_plat.shared.utility.notifier.key_notifier import KeyEventNotifier
from visual_plat.shared.utility.notifier.event_notifier import EventNotifier

from visual_plat.global_proxy.config_proxy import ConfigProxy

"""
事件代理
支持的事件有：
    1. 鼠标事件（mouse）
        - 鼠标按下：press
        - 鼠标释放：release
        - 鼠标移动：move
        - 鼠标滚轮：wheel
    2. 键盘事件（key）
        - 键盘按下（自定义）
    3. 视图更新事件（view）
        - 视图框选：frame_begin; frame_end; framing
        - 视图缩放：zoom_begin; zoom_end; zooming
        - 视图拖拽：drag_begin; drag_end; dragging
        - 视图滑动：slide_begin; slide_end
"""


class EventDeputy(QObject):
    cnt_finished_signal = Signal()

    def __init__(self, canvas):
        super(EventDeputy, self).__init__()
        self.canvas = canvas

        self.on_framing = False
        self.on_zooming = False
        self.on_dragging = False
        self.on_sliding = False

        self.has_framed = False  # 已经框选某个矩形
        self.allow_menu = False

        self.focus_point: QPoint = QPoint()
        self.focus_rect: QRect = QRect()

        self.last_mouse_pos: QPoint = QPoint()  # 上次记录的鼠标坐标
        self.start_framing_crd: QPoint = QPoint()
        self.start_sliding_pos: QPoint = QPoint()

        self.cnt_worker = CountDownWorker(finished=self.cnt_finished)
        self.counting = False
        self.cnt_finished_signal.connect(self.cnt_finished)

        self.key_notifier = KeyEventNotifier()
        self.mouse_notifier = EventNotifier()
        self.view_notifier = EventNotifier()
        self.drag_notifier = EventNotifier()

        self.mouse_listening = ConfigProxy.event_setting()["mouse_listening"]

    def bind_layer_event(self, layer: LayerBase, config: dict):
        if "key" in config.keys():
            self.key_notifier.parse(config["key"], layer)
        if "mouse" in config.keys():
            self.mouse_notifier.parse(config["mouse"], layer)
        if "view" in config.keys():
            self.view_notifier.parse(config["view"], layer)
        if "drop" in config.keys():
            self.drag_notifier.parse(config["drop"], layer)

    def on_key_pressed(self, event: QKeyEvent):
        self.key_notifier.invoke(event.modifiers(), event.key())

    def cnt_finished(self):
        self.counting = False
        self.cnt_worker.reset()
        self.on_zooming = False
        self.view_notifier.invoke("zoom_end")

    def on_mouse_press(self, event):
        self.last_mouse_pos = event.pos
        if event.button() == Qt.LeftButton:
            self.has_framed = False
            self.on_framing = True
            self.view_notifier.invoke("frame_begin")
            self.start_framing_crd = event.crd
            self.focus_point = event.crd
            self.focus_rect = None
        elif event.button() == Qt.MiddleButton:
            self.on_sliding = not self.on_sliding
            if self.on_sliding:
                self.start_sliding_pos = event.pos
                self.view_notifier.invoke("slide_begin")
            else:
                self.view_notifier.invoke("slide_end")
        elif event.button() == Qt.RightButton:
            if not self.on_sliding:
                self.on_dragging = True
                self.view_notifier.invoke("drag_begin")
                self.canvas.setCursor(Qt.OpenHandCursor)
                self.allow_menu = True
        # 分发事件
        self.mouse_notifier.invoke("press", event)

    def on_mouse_move(self, event):
        self.last_mouse_pos = event.pos
        if self.on_dragging:
            self.view_notifier.invoke("dragging")
        if not self.on_sliding:
            if self.on_framing:
                self.has_framed = True
                self.view_notifier.invoke("framing")
                start = self.start_framing_crd
                end = event.crd
                self.focus_rect = area_of_points([start, end])
            elif not self.has_framed:
                self.focus_point = event.crd
            self.allow_menu = False
        # 分发事件
        if self.mouse_listening:
            self.mouse_notifier.invoke("move", event)

    def on_mouse_release(self, event):
        if self.on_dragging:
            self.on_dragging = False
            self.view_notifier.invoke("drag_end")
            self.canvas.setCursor(Qt.ArrowCursor)
            self.canvas.render_deputy.mark_need_restage()
        if self.on_framing:
            self.on_framing = False
            self.view_notifier.invoke("frame_end")
        # 分发事件
        self.mouse_notifier.invoke("release", event)

    def on_mouse_wheel(self, event):
        if event.angleDelta().y():
            if not self.on_zooming:
                self.view_notifier.invoke("zoom_begin")
            self.on_zooming = True
            self.view_notifier.invoke("zooming")
            if self.counting:
                self.cnt_worker.reset()
            else:
                AsyncProxy.start(self.cnt_worker)
                self.counting = True
            # 分发事件
            self.mouse_notifier.invoke("wheel", event)
