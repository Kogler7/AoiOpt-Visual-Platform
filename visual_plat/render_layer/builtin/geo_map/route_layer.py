from visual_plat.render_layer.layer_base import *


class RouteLayer(LayerBase):
    pass

    def on_stage(self, device: QPixmap):
        return True

    def move_up(self):
        print("move_up")

    def move_down(self):
        print("move_down")

    def move_left(self):
        print("move_left")

    def move_right(self):
        print("move_right")
