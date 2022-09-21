from PySide6.QtWidgets import QApplication
from visual_plat.canvas import VisualCanvas
from visual_plat.global_proxy.async_proxy import AsyncProxy
"""
可视化服务平台
提供一些常规的设置服务
"""


class VisualPlatform:
    @staticmethod
    def launch(async_task: callable = None):
        """
        启动可视化平台
        可附带执行一个异步任务
        请不要在重复调用此函数
        也不要在此函数后再执行其他任务
        """
        app = QApplication([])
        canvas = VisualCanvas()
        if async_task is not None:
            AsyncProxy.run(async_task)
        canvas.show()
        app.exec()
