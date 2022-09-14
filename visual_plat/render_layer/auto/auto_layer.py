from PySide6.QtCore import *
from abc import abstractmethod
from visual_plat.render_layer.layer_base import *


class AutoListLayer(LayerBase):
    pass


class AutoRectLayer(LayerBase):
    def __init__(self):
        super(AutoRectLayer, self).__init__()

    @abstractmethod
    def draw_each(self, device: QPixmap, coord: QPoint, scale: int):
        pass
