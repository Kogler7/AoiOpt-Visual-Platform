from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QPixmap, QImage

from utils.color_set import ColorSet
from tqdm import trange
import time


@dataclass
class AOIInfo:
    crd_set: set
    index: int = 0
    label: str = ""
    color: QColor = QColor()


class AOIInfoSet:
    def __init__(self):
        pass

    def __hash__(self):
        return hash(time.time())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__hash__() == other.__hash__()
        else:
            return False


class AOIProxy:
    def __init__(self):
        self.crd_count = 0
        self.aoi_dict = defaultdict(lambda: AOIInfo(crd_set=set()))
        self.crd_dict = {}
        self.index_map: QImage = QImage()
        self.color_map: QImage = QImage()

    def clear(self):
        self.crd_count = 0
        self.aoi_dict.clear()
        self.crd_dict.clear()

    def get_crd_num(self):
        return self.crd_count

    def get_idx_list(self):
        return self.aoi_dict.keys()

    def get_aoi_area(self, idx: int = -1):
        res = []
        if idx == -1:
            for _, aoi in self.aoi_dict.items():
                res.append(aoi)
        else:
            if idx in self.aoi_dict.keys():
                res.append(self.aoi_dict[idx])
            else:
                print(f"AOISteward: AOI Index ({idx}) Not Found.")
        return res

    def add_aoi(self, index: int, label: str = "", color: QColor = QColor()):
        if index not in self.aoi_dict.keys():
            info = self.aoi_dict[index]
            info.index = index
            info.label = label
            info.color = color

    def del_aoi(self, index: int):
        if index in self.aoi_dict.keys():
            info = self.aoi_dict.pop(index)
            for crd in info.crd_set:
                self.crd_dict.pop(crd)

    def append(self, crd: QPoint, aoi: int):
        if crd not in self.crd_dict.keys():
            if aoi not in self.aoi_dict.keys():
                self.add_aoi(index=aoi, color=ColorSet.new_color())
            self.aoi_dict[aoi].crd_set.add(crd)
            self.crd_dict[crd] = aoi
            self.crd_count += 1
        else:
            print("请改用 change/n")

    def remove(self, crd: QPoint):
        if crd in self.crd_dict.keys():
            aoi = self.crd_dict.pop(crd)
            self.aoi_dict[aoi].crd_set.remove(crd)
            self.crd_count -= 1

    def change(self, crd: QPoint, tgt: int):
        self.remove(crd)
        self.append(crd, tgt)

    def crd2aoi(self, crd: QPoint):
        if crd in self.crd_dict.keys():
            return self.crd_dict.get(crd)
        return None

    def read_img(self, img: QImage):
        self.color_map = img

    def read_npy(self, arr: np.array):
        shape = arr.shape
        self.color_map = QImage(shape[1], shape[0], QImage.Format_BGR888)
        with trange(shape[0]) as line:
            for y in line:
                line.set_description_str(f"Reading AOI")
                for x in range(shape[1]):
                    self.color_map.setPixelColor(QPoint(x, y), ColorSet.idx_color(arr[y][x]))

    def get_aoi_map(self, idx: int = -1):
        return self.color_map
