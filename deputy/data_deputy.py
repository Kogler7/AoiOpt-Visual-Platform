from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QImage
import numpy as np

from proxy.aoi_proxy import AOIProxy
from proxy.trace_proxy import TraceInfo, TraceProxy
from proxy.parcel_proxy import ParcelsInfo, ParcelProxy
from utils.txt_reader import TxtReader
from utils.color_set import ColorSet


class DataDeputy:
    def __init__(self):
        self.generation = 0
        self.aoi_proxy = AOIProxy()
        self.trace_proxy = TraceProxy()
        self.parcel_proxy = ParcelProxy()

    def read_aoi(self, path: str = None, data: np.array = None):
        """读入AOI数据"""
        if path:
            mode = path[-3:]
            if mode == "npy":
                self.aoi_proxy.read_npy(np.load(path))
            elif mode == "jpg" or mode == "png":
                img = QImage()
                if img.load(path):
                    self.aoi_proxy.read_img(img)
                else:
                    print("Data Deputy: Image Reading Failed.")
            else:
                print("Data Deputy: Unexpected Read Mode.")
        elif data is not None:
            self.aoi_proxy.read_npy(data)
        else:
            print("Data Deputy: No Data.")

    def read_parcels(self, path: str = None, data: np.array = None):
        """读入包裹数据"""
        if path:
            mode = path[-3:]
            if mode == "npy":
                data = np.load(path, allow_pickle=True)
                self.parcel_proxy.read_npy(data)
            elif mode == "txt":
                self.parcel_proxy.read_lst(TxtReader.read_grouped_points(path))
            else:
                print("Data Deputy: Unexpected Read Mode.")
        elif data:
            self.parcel_proxy.read_npy(data)
        else:
            print("Data Deputy: No Data.")

    def read_traces(self, path: str = None, data: np.array = None):
        """读入轨迹数据"""
        if path:
            mode = path[-3:]
            if mode == "npy":
                data = np.load(path, allow_pickle=True)
                self.trace_proxy.read_npy(data)
            elif mode == "txt":
                self.trace_proxy.read_lst(TxtReader.read_grouped_points(path))
            else:
                print("Data Deputy: Unexpected Read Mode.")
        elif data:
            self.trace_proxy.read_npy(data)
        else:
            print("Data Deputy: No Data.")

    def get_aoi_info(self, aoi_id: int = -1):
        return self.aoi_proxy.get_aoi_map(aoi_id)

    def get_traces_info(self, indexes: list):
        return self.trace_proxy.get_trace(indexes)

    def get_parcels_info(self, indexes: list):
        return self.parcel_proxy.get_parcels(indexes)
