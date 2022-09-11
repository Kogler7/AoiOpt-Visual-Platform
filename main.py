import sys
import numpy as np
import time

from PySide6.QtCore import *
from PySide6.QtWidgets import QApplication
from visual_plat.canvas import VisualCanvas
from visual_plat.global_proxy.async_proxy import AsyncProxy, AsyncWorker


class LearnWorker(AsyncWorker):
    update_signal = Signal(np.ndarray)

    def __init__(self, aoi_slot):
        super().__init__()
        self.update_signal.connect(aoi_slot)

    def runner(self):
        while True:
            data = np.random.randint(20, size=(100, 100))
            self.update_signal.emit(data)
            time.sleep(0.5)


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
