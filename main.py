import datetime
import sys
import numpy as np
import time

from PySide6.QtCore import *
from PySide6.QtWidgets import QApplication
from visual_plat.canvas import VisualCanvas
from visual_plat.global_proxy.async_proxy import AsyncProxy, AsyncWorker
from visual_plat.global_proxy.update_proxy import UpdateProxy


class LearnWorker(AsyncWorker):

    def __init__(self, aoi_slot):
        super().__init__()
        self.index = 1

    def runner(self):
        while True:
            data = np.random.randint(self.index, size=(100, 100))
            UpdateProxy.reload("aoi", data)
            self.index += 1
            if self.index > 2:
                self.index = 1
            time.sleep(1)


def world_config(world: VisualCanvas):
    # world.aoi_layer.reload("./output/aoi/AOI_20_grid.npy")
    # world.trace_layer.agent.auto_read("./data/trace/trace_1.npy")
    # world.parcel_layer.agent.auto_read("./data/parcels/parcels_n.npy")

    indexes = range(10)
    bias = 1
    # world.trace_layer.set_indexes(indexes)
    # world.parcel_layer.set_indexes(indexes)

    # weight_layer = WeightAsyncLayer()
    learner = LearnWorker(world.aoi_layer.reload)
    AsyncProxy.start(learner)


if __name__ == '__main__':
    app = QApplication([])
    canvas = VisualCanvas()

    world_config(canvas)

    canvas.show()
    sys.exit(app.exec())
