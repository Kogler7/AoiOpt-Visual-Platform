from PySide6.QtGui import *
from PySide6.QtCore import *
from visual_plat.shared.static.custom_2d import *
from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.shared.utility.count_down import CountDownWorker


class EventDeputy(QObject):
    dragging_signal = Signal(bool)
    zooming_signal = Signal(bool)
    cnt_finished_signal = Signal()

    def __init__(self, zoom_slot, drag_slot):
        super(EventDeputy, self).__init__()

        self.on_framing = False
        self.on_zooming = False
        self.on_dragging = False
        self.on_sliding = False
        self.on_translating = False

        self.zooming_signal.connect(zoom_slot)
        self.dragging_signal.connect(drag_slot)

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

    def add_layer(self, layer, config):
        pass

    def cnt_finished(self):
        self.counting = False
        self.cnt_worker.reset()
        self.on_zooming = False
        self.zooming_signal.emit(self.on_zooming)

    def on_mouse_press(self, event):
        self.last_mouse_pos = event.pos
        if event.button() == Qt.LeftButton:
            self.has_framed = False
            self.on_framing = True
            self.start_framing_crd = event.crd
            self.focus_point = event.crd
            self.focus_rect = None
        elif event.button() == Qt.MiddleButton:
            self.on_sliding = not self.on_sliding
            if self.on_sliding:
                self.start_sliding_pos = event.pos
        elif event.button() == Qt.RightButton:
            if not self.on_sliding:
                self.on_dragging = True
                self.dragging_signal.emit(self.on_dragging)
                self.allow_menu = True

    def on_mouse_move(self, event):
        self.last_mouse_pos = event.pos
        if not self.on_sliding:
            if self.on_framing:
                self.has_framed = True
                start = self.start_framing_crd
                end = event.crd
                self.focus_rect = area_of_points([start, end])
            elif not self.has_framed:
                self.focus_point = event.crd
            self.allow_menu = False

    def on_mouse_release(self):
        if self.on_dragging:
            self.on_dragging = False
            self.dragging_signal.emit(self.on_dragging)
        if self.on_framing:
            self.on_framing = False

    def on_mouse_wheel(self):
        self.on_zooming = True
        self.zooming_signal.emit(self.on_zooming)
        if self.counting:
            self.cnt_worker.reset()
        else:
            AsyncProxy.start(self.cnt_worker)
            self.counting = True
