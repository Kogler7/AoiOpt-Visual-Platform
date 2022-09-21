from PySide6.QtWidgets import QApplication
from visual_plat.canvas import VisualCanvas
from visual_plat.global_proxy.async_proxy import AsyncProxy


class VisualPlatform:
    @staticmethod
    def launch(async_task: callable = None):
        app = QApplication([])
        canvas = VisualCanvas()
        if async_task is not None:
            AsyncProxy.run(async_task)
        canvas.show()
        app.exec()
