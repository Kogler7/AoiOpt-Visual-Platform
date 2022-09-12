from PySide6.QtCore import QPointF, QSize
from PySide6.QtWidgets import QWidget
from visual_plat.shared.utility.anchor_tip import AnchorTip, AnchorLocate
from visual_plat.global_proxy.config_proxy import ConfigProxy


class TooltipDeputy:
    def __init__(self, canvas: QWidget):
        self.canvas = canvas
        self.size = canvas.size()
        anchor_bias = ConfigProxy.tooltip("anchor_bias")
        self.anchor_bias = QPointF(anchor_bias[0], anchor_bias[1])
        self.tooltip_ft = AnchorTip(AnchorLocate.btm_lft)
        self.tooltip_tl = AnchorTip(
            anchor=AnchorLocate.top_lft,
            locate=self.anchor_bias
        )
        self.tooltip_tr = AnchorTip(
            anchor=AnchorLocate.top_rgt,
            locate=QPointF(self.size.width() - self.anchor_bias.x(), self.anchor_bias.y())
        )
        self.tooltip_bl = AnchorTip(
            anchor=AnchorLocate.btm_lft,
            locate=QPointF(self.anchor_bias.x(), self.size.height() - self.anchor_bias.y())
        )
        self.tooltip_br = AnchorTip(
            anchor=AnchorLocate.btm_rgt,
            locate=QPointF(self.size.width() - self.anchor_bias.x(), self.size.height() - self.anchor_bias.y())
        )

    def relocate(self, size=QSize):
        self.size = size
        self.tooltip_tr.move(QPointF(self.size.width() - self.anchor_bias.x(), self.anchor_bias.y()))
        self.tooltip_bl.move(QPointF(self.anchor_bias.x(), self.size.height() - self.anchor_bias.y()))
        self.tooltip_br.move(
            QPointF(self.size.width() - self.anchor_bias.x(), self.size.height() - self.anchor_bias.y()))

    def draw(self):
        self.tooltip_tl.draw(self.canvas)
        self.tooltip_tr.draw(self.canvas)
        self.tooltip_bl.draw(self.canvas)
        self.tooltip_br.draw(self.canvas)
        self.tooltip_ft.draw(self.canvas)
