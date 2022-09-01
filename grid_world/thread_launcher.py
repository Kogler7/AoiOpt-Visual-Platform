from PySide6.QtCore import *
import numpy as np
import time
from grid_world.proxy.async_proxy import AsyncProxy, AsyncWorker


class Learner(AsyncWorker):
    update_signal = Signal(np.ndarray)

    def __init__(self, aoi_slot):
        super().__init__()
        self.update_signal.connect(aoi_slot)

    def runner(self):
        while True:
            data = np.random.randint(20, size=(100, 100))
            self.update_signal.emit(data)
            time.sleep(0.5)