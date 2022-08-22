from PySide6.QtCore import *
import numpy as np


class PGLearning(QThread):
    update_signal = Signal(np.ndarray)

    def __init__(self, aoi_slot):
        super().__init__()
        self.update_signal.connect(aoi_slot)

    def run(self):
        while True:
            data = np.random.randint(20, size=(100, 100))
            self.update_signal.emit(data)
            self.msleep(2000)
