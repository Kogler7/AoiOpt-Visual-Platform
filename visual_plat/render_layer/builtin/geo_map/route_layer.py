from visual_plat.render_layer.layer_base import *


class RouteLayer(LayerBase):
    pass

    def on_stage(self, device: QPixmap):
        return True

    def start_service(self):
        self.show()
        print("Route service started.")

    def stop_service(self):
        self.hide()
        print("Route service stopped.")

    def trans_state(self):
        if self.visible:
            self.stop_service()
        else:
            self.start_service()