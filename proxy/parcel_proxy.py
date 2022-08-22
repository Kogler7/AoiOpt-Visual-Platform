from dataclasses import dataclass
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor
from collections import defaultdict
from utils.custom_2d import area_of_points, area_of_array
from utils.color_set import ColorSet
import numpy as np
from tqdm import trange


@dataclass
class ParcelsInfo:
    area: QRect
    index: int
    color: QColor
    p_lst: list[QPoint]


class ParcelProxy:
    def __init__(self):
        self.parcels_dict: dict[int, ParcelsInfo] = {}

    def clear(self):
        self.parcels_dict.clear()

    def add_parcels(self, crd_list: list[QPoint], index: int, color: QColor):
        area = area_of_points(crd_list)
        info = ParcelsInfo(area, index, color, [])
        info.p_lst = crd_list
        self.parcels_dict[index] = info

    def read_npy(self, arr: np.array):
        with trange(len(arr)) as t:
            t.set_description_str(f"Reading parcels")
            for i in t:
                area = area_of_array(arr[i])
                info = ParcelsInfo(area, i, ColorSet.idx_color(i), [])
                for p in arr[i]:
                    info.p_lst.append(QPoint(p[1], p[0]))
                self.parcels_dict[i] = info

    def read_lst(self, lst: list[list[QPoint]]):
        for i in range(len(lst)):
            self.add_parcels(lst[i], i, ColorSet.idx_color(i, "dark"))

    def get_idx_list(self):
        return self.parcels_dict.keys()

    def get_parcels(self, indexes: list):
        res = []
        if indexes == [-1]:
            for _, parcels in self.parcels_dict.items():
                res.append(parcels)
        else:
            for idx in indexes:
                if idx in self.parcels_dict.keys():
                    res.append(self.parcels_dict[idx])
                else:
                    print(f"ParcelSteward: Parcels Index ({idx}) Not Found.")
        return res
