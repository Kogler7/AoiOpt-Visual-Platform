from PySide6.QtGui import QImage
import numpy as np

from visual_plat.data_agent.aoi_agent import AoiAgent
from visual_plat.data_agent.traj_agent import TrajAgent
from visual_plat.data_agent.parcel_agent import ParcelAgent


class DataDeputy:
    def __init__(self):
        self.generation = 0
        self.aoi_proxy = AoiAgent()
        self.trace_proxy = TrajAgent()
        self.parcel_proxy = ParcelAgent()
