import datetime
import pickle
from dataclasses import dataclass
from enum import Enum

from visual_plat.render_layer.layer_base import LayerBase
from visual_plat.global_proxy.config_proxy import ConfigProxy


class RecordType(Enum):
    reload = 0
    adjust = 1


@dataclass
class RecordUnit:
    layer_tag: str
    record_type: RecordType
    record_data: any


@dataclass
class Record:
    initial: list[RecordUnit]
    updates: list[RecordUnit]


class StateDeputy:
    record_path = ConfigProxy.path("record")

    def __init__(self, layers: dict[str, LayerBase]):
        self.layers = layers
        self.record: Record = Record([], [])
        self.blocked = False
        self.suspended = False
        self.recording = False
        self.replaying = False

    def block_up(self):
        self.blocked = not self.blocked

    def reload(self, layer_tag: str, data=None):
        if not self.suspended:
            self.layers[layer_tag].reload(data)
            if self.recording:
                self.record.updates.append(RecordUnit(layer_tag, RecordType.reload, data))
            while self.blocked:
                pass  # 尚未完成

    def adjust(self, layer_tag: str, data=None):
        if not self.suspended:
            self.layers[layer_tag].adjust(data)
            if self.recording:
                self.record.updates.append(RecordUnit(layer_tag, RecordType.adjust, data))

    @staticmethod
    def load_record(path):
        with open(path, 'rb') as rcd:
            res = pickle.load(rcd)
        return res

    @staticmethod
    def save_record(record: Record):
        rcd_name = str(datetime.datetime.now())
        with open(StateDeputy.record_path + rcd_name + ".rcd", 'wb') as rcd:
            pickle.dump(record, rcd)

    def snapshot(self):
        record = Record([], [])
        for tag, layer in self.layers:
            record.initial.append(RecordUnit(tag, RecordType.reload, layer.data))
        self.save_record(record)

    def start_record(self):
        self.record = Record([], [])
        for tag, layer in self.layers:
            self.record.initial.append(RecordUnit(tag, RecordType.reload, layer.data))
        self.recording = True

    def start_replay(self):
        pass

    def pause(self):
        self.suspended = not self.suspended

    def terminate(self):
        if self.recording:
            self.recording = False
            self.save_record(self.record)
