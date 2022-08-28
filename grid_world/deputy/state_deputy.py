from PySide6.QtGui import *
from PySide6.QtCore import *
from grid_world.utils.custom_2d import *
import time


class StateDeputy(QObject):
    dragging_signal = Signal(bool)
    zooming_signal = Signal(bool)

    def __init__(self):
        super(StateDeputy, self).__init__()

        self.on_framing = False
        self.on_zooming = False
        self.on_dragging = False
        self.on_translating = False

        self.has_framed = False  # 已经框选某个矩形
        self.allow_menu = False

        self.focus_point: QPoint = QPoint()
        self.focus_rect: QRect = QRect()

        self.last_mouse_pos: QPoint = QPoint()  # 上次记录的鼠标坐标
        self.start_framing_crd: QPoint = QPoint()

        self.cnt_thread = CountDownThread(self.zooming_signal, self)

    def on_mouse_press(self, event):
        self.last_mouse_pos = event.pos
        if event.button() == Qt.LeftButton:
            self.has_framed = False
            self.on_framing = True
            self.start_framing_crd = event.crd
            self.focus_point = event.crd
            self.focus_rect = None
        elif event.button() == Qt.RightButton:
            self.on_dragging = True
            self.dragging_signal.emit(self.on_dragging)
            self.allow_menu = True

    def on_mouse_move(self, event):
        self.last_mouse_pos = event.pos
        if self.on_framing:
            self.has_framed = True
            start = self.start_framing_crd
            end = event.crd
            self.focus_rect = area_of_points([start, end])
        elif not self.has_framed:
            self.focus_point = event.crd
        self.allow_menu = False

    def on_mouse_release(self):
        self.on_dragging = False
        self.dragging_signal.emit(self.on_dragging)
        self.on_framing = False

    def on_mouse_wheel(self):
        self.on_zooming = True
        self.zooming_signal.emit(self.on_zooming)
        if self.cnt_thread.isRunning():
            self.cnt_thread.reset()
        else:
            self.cnt_thread = CountDownThread(self.zooming_signal, self)
            self.cnt_thread.start()


class CountDownThread(QThread):
    def __init__(self, signal, target: StateDeputy):
        super(CountDownThread, self).__init__()
        self.remaining_time = 8
        self.signal = signal
        self.target = target

    def reset(self, total: int = 8):
        self.remaining_time = total

    def run(self):
        while self.remaining_time > 0:
            self.remaining_time -= 1
            time.sleep(0.01)
        self.target.on_zooming = False
        self.target.zooming_signal.emit(False)
        self.quit()