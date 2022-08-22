from dataclasses import dataclass
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor
from collections import defaultdict
from utils.custom_2d import area_of_points, area_of_array
from utils.color_set import ColorSet
import numpy as np
from tqdm import trange


@dataclass
class TraceInfo:
    area: QRect
    index: int
    color: QColor
    p_lst: list[QPoint]


class TraceProxy:
    def __init__(self):
        self.trace_dict = defaultdict(TraceInfo)

    def clear(self):
        self.trace_dict.clear()

    def add_trace(self, crd_list: list[QPoint], index: int, color: QColor):
        """对轨迹数据进行编制，删去不必要的中间点"""
        if len(crd_list) < 2:
            return
        info = TraceInfo(QRect(), index, color, [])
        ldr = QPoint(0, 0)
        for i in range(1, len(crd_list)):
            ndr = crd_list[i] - crd_list[i - 1]
            if ldr != ndr:
                info.p_lst.append(crd_list[i - 1])
            ldr = ndr
        info.p_lst.append(crd_list[len(crd_list) - 1])
        info.area = area_of_points(info.p_lst)
        self.trace_dict[index] = info

    def read_npy(self, arr: np.array):
        data = []
        with trange(len(arr)) as t:
            t.set_description_str(f"Reading traces")
            for i in t:
                if len(data) < i + 1:
                    data.append([])
                for p in arr[i]:
                    data[i].append(QPoint(p[1], p[0]))
            self.read_lst(data)

    def read_lst(self, lst: list[list[QPoint]]):
        with trange(len(lst)) as t:
            t.set_description_str(f"Processing traces")
            for i in t:
                self.add_trace(lst[i], i, ColorSet.idx_color(i, "normal"))

    def get_idx_list(self):
        return self.trace_dict.keys()

    def get_trace(self, indexes: list):
        res = []
        if indexes == [-1]:
            for _, trace in self.trace_dict.items():
                res.append(trace)
        else:
            for idx in indexes:
                if idx in self.trace_dict.keys():
                    res.append(self.trace_dict[idx])
                else:
                    print(f"TraceSteward: Trace Index ({idx}) Not Found.")
        return res
