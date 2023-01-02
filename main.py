import numpy as np
import time

from visual_plat.platform import VisualPlatform
from visual_plat.proxies.update_proxy import UpdateProxy
from visual_plat.shared.utils.xps_checker import XPSChecker


def update_task():
    index = 0
    xps = XPSChecker()
    while True:
        data = np.zeros((5, 5), dtype=np.int)
        data[int(index / 5)][index % 5] = 1
        data[index % 5][int(index / 5)] = 2
        data[index % 5][index % 5] = 3
        UpdateProxy.reload("aoi", data)
        index += 1
        if index >= 25:
            index = 0
        time.sleep(10)


def color_test():
    data = np.arange(64).reshape((8, 8))
    UpdateProxy.reload("aoi", data)


if __name__ == '__main__':
    VisualPlatform.launch(async_task=color_test)
