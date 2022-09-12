import time

from visual_plat.canvas_deputy.state_deputy import StateDeputy


class UpdateProxy:
    canvas = None
    state_deputy: StateDeputy = None

    @staticmethod
    def set_canvas(canvas):
        """仅在第一次绑定时有效"""
        if not UpdateProxy.canvas:
            UpdateProxy.canvas = canvas
            UpdateProxy.state_deputy = canvas.state_deputy

    @staticmethod
    def reload(layer_tag: str, data=None):
        if not UpdateProxy.state_deputy.suspended:
            blocked = UpdateProxy.state_deputy.reload(layer_tag=layer_tag, data=data)
            while blocked:
                time.sleep(0.2)
                blocked = UpdateProxy.state_deputy.blocked

    @staticmethod
    def adjust(layer_tag: str, data=None):
        if not UpdateProxy.state_deputy.suspended:
            blocked = UpdateProxy.state_deputy.adjust(layer_tag=layer_tag, data=data)
            while blocked:
                time.sleep(0.2)
                blocked = UpdateProxy.state_deputy.blocked
