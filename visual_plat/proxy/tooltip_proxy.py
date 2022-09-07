from PySide6.QtCore import QPointF, QPoint, QSize
from PySide6.QtWidgets import QWidget
from visual_plat.utils.anchor_tip import AnchorTip, AnchorLocate


class TooltipProxy:
    def __init__(self, device: QWidget, anchor_bias: QPoint = QPoint(100, 50)):
        self.device = device
        self.size = device.size()
        self.bias = anchor_bias
        self.tooltip_ft = AnchorTip(AnchorLocate.btm_lft)
        self.tooltip_tl = AnchorTip(
            anchor=AnchorLocate.top_lft,
            locate=self.bias
        )
        self.tooltip_tr = AnchorTip(
            anchor=AnchorLocate.top_rgt,
            locate=QPointF(self.size.width() - self.bias.x(), self.bias.y())
        )
        self.tooltip_bl = AnchorTip(
            anchor=AnchorLocate.btm_lft,
            locate=QPointF(self.bias.x(), self.size.height() - self.bias.y())
        )
        self.tooltip_br = AnchorTip(
            anchor=AnchorLocate.btm_rgt,
            locate=QPointF(self.size.width() - self.bias.x(), self.size.height() - self.bias.y())
        )

    def relocate(self, size=QSize):
        self.size = size
        self.tooltip_tr.move(QPointF(self.size.width() - self.bias.x(), self.bias.y()))
        self.tooltip_bl.move(QPointF(self.bias.x(), self.size.height() - self.bias.y()))
        self.tooltip_br.move(QPointF(self.size.width() - self.bias.x(), self.size.height() - self.bias.y()))

    def draw(self):
        self.tooltip_tl.draw(self.device)
        self.tooltip_tr.draw(self.device)
        self.tooltip_bl.draw(self.device)
        self.tooltip_br.draw(self.device)
        self.tooltip_ft.draw(self.device)
