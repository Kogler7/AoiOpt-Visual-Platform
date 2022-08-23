from collections import defaultdict
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from enum import Enum


class TipAnchor(Enum):
    top_lft = 0
    top_rgt = 1
    btm_lft = 2
    btm_rgt = 3


class FloatTooltip:
    def __init__(self, anchor=TipAnchor.top_lft, locate=QPoint(0, 0)):
        self.visible = True
        self.anchor = anchor
        self.locate = locate
        self.tips = defaultdict(str)
        self.text = ""
        self.back_height = 30
        self.text_pen = QPen(QColor(50, 50, 50))
        self.text_pen.setWidth(3)

    def get_rect(self, txt_len=0):
        if txt_len == 0:
            return QRect()
        width = int(txt_len * 6.5) + 10
        height = self.back_height
        if self.anchor is TipAnchor.top_lft:
            return QRect(int(self.locate.x()), int(self.locate.y()), width, height)
        elif self.anchor is TipAnchor.top_rgt:
            return QRect(int(self.locate.x()) - width, int(self.locate.y()), width, height)
        elif self.anchor is TipAnchor.btm_lft:
            return QRect(int(self.locate.x()), int(self.locate.y()) - height, width, height)
        elif self.anchor is TipAnchor.btm_rgt:
            return QRect(int(self.locate.x()) - width, int(self.locate.y()) - height, width, height)
        else:
            raise

    def draw(self, canvas: QWidget):
        if self.visible:
            painter = QPainter(canvas)
            rect = self.get_rect(len(self.text))
            painter.fillRect(rect, QColor(240, 240, 240))
            painter.setPen(self.text_pen)
            painter.setFont(QFont("等线", 12, 3))
            painter.drawText(QPointF(rect.x() + 5, rect.y() + 20), self.text)

    def move(self, tgt=QPoint(0, 0)):
        self.locate = tgt

    def set(self, key="", words=""):
        self.tips[key] = words
        self.text = ""
        for key, val in self.tips.items():
            if val != "":
                self.text += f"{str(key)}: {val} | "
        self.text = self.text[:-2]

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
