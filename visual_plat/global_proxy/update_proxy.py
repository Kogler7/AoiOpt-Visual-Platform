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
    def reload(layer_tag: str, data=None, new_step=True):
        if UpdateProxy.canvas:
            if not UpdateProxy.state_deputy.suspended:
                UpdateProxy.state_deputy.reload(layer_tag=layer_tag, data=data, new_step=new_step)
                while UpdateProxy.state_deputy.blocked:
                    time.sleep(0.2)
        else:
            print("Canvas is not set.")

    @staticmethod
    def batched_reload(tags: list[str], data: list):
        new_step = True
        for i in range(len(tags)):
            UpdateProxy.reload(tags[i], data[i], new_step=new_step)
            new_step = False

    @staticmethod
    def adjust(layer_tag: str, data=None, new_step=True):
        if UpdateProxy.canvas:
            if not UpdateProxy.state_deputy.suspended:
                UpdateProxy.state_deputy.adjust(layer_tag=layer_tag, data=data, new_step=new_step)
                while UpdateProxy.state_deputy.blocked:
                    time.sleep(0.2)
        else:
            print("Canvas is not set.")

    @staticmethod
    def batched_adjust(tags: list[str], data: list):
        new_step = True
        for i in range(len(tags)):
            UpdateProxy.adjust(tags[i], data[i], new_step=new_step)
            new_step = False

    @staticmethod
    def start_record():
        UpdateProxy.state_deputy.start_record()

    @staticmethod
    def stop_record():
        UpdateProxy.state_deputy.stop_record()
