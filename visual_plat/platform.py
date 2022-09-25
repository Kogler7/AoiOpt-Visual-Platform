from PySide6.QtWidgets import QApplication
from visual_plat.canvas import VisualCanvas
from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.global_proxy.config_proxy import ConfigProxy
from visual_plat.global_proxy.update_proxy import UpdateProxy

"""
可视化服务平台
提供全局代理的初始设置服务
"""


class VisualPlatform:
    canvas_list: list[VisualCanvas] = []

    @staticmethod
    def launch(async_task: callable = None, init_finished: callable = None):
        """
        启动可视化平台
        可附带执行一个异步任务
        请不要在重复调用此函数
        也不要在此函数后再执行其他任务
        此函数全局仅允许被调用一次
        """
        if not ConfigProxy.loaded:
            ConfigProxy.load()
            app = QApplication([])
            version = str(ConfigProxy.canvas('version')) \
                      + ("-pre" if not ConfigProxy.canvas("release") else "")
            app_name = f"AoiOpt Visual Platform {version}"
            app.setApplicationName(app_name)
            canvas = VisualPlatform.new_canvas(app_name, init_finished)
            UpdateProxy.set_canvas(canvas)
            if async_task is not None:
                AsyncProxy.run(async_task)
            app.exec()
        else:
            raise RuntimeError("VisualPlatform has been launched.")

    @staticmethod
    def new_canvas(title: str = "New Canvas", on_init_finished: callable = None):
        canvas = VisualCanvas(on_init_finished=on_init_finished)
        VisualPlatform.canvas_list.append(canvas)
        canvas.setWindowTitle(title)
        canvas.status_bar.set_default(title)
        canvas.key_notifier.parse(ConfigProxy.event(), canvas)
        canvas.show()
        return canvas

    @staticmethod
    def get_canvas(index: int = 0):
        return VisualPlatform.canvas_list[index]
