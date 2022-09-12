import pickle
import time
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QMutex

from visual_plat.render_layer.layer_base import LayerBase
from visual_plat.global_proxy.config_proxy import ConfigProxy
from visual_plat.global_proxy.async_proxy import AsyncProxy


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
    record_path = ""

    def __init__(self, layers: dict[str, LayerBase]):
        self.layers = layers
        self.record: Record = Record([], [])
        self.pausing = False  # 播放暂停
        self.blocked = False  # 异步线程阻塞
        self.suspended = False  # 拒绝接受更新
        self.recording = False
        self.replaying = False
        self.play_index = 0
        self.play_range = None
        self.play_record = None
        self.play_mutex = QMutex()
        StateDeputy.record_path = ConfigProxy.path("record")

    def block(self):
        self.blocked = not self.blocked

    def reload(self, layer_tag: str, data=None):
        self.layers[layer_tag].reload(data)
        if self.recording:
            self.record.updates.append(RecordUnit(layer_tag, RecordType.reload, data))
        return self.blocked

    def adjust(self, layer_tag: str, data=None):
        self.layers[layer_tag].adjust(data)
        if self.recording:
            self.record.updates.append(RecordUnit(layer_tag, RecordType.adjust, data))
        return self.blocked

    @staticmethod
    def load_record(path):
        with open(path, 'rb') as rcd:
            res = pickle.load(rcd)
        return res

    @staticmethod
    def save_record(record: Record):
        rcd_name = time.strftime(
            '%Y%m%d-%H%M%S',
            time.localtime(time.time())
        )
        path = StateDeputy.record_path + rcd_name + ".rcd"
        with open(path, 'wb') as rcd:
            pickle.dump(record, rcd)
        print(f"Record saved as {rcd_name}.rcd")
        return path

    def snapshot(self):
        record = Record([], [])
        for tag, layer in self.layers.items():
            record.initial.append(RecordUnit(tag, RecordType.reload, layer.data))
        return self.save_record(record)

    def start_record(self):
        if not self.recording:
            print("Recording")
            self.record = Record([], [])
            for tag, layer in self.layers.items():
                self.record.initial.append(RecordUnit(tag, RecordType.reload, layer.data))
            self.recording = True

    def start_replay(self, record: Record):
        print("start")
        self.replaying = True
        self.suspended = True  # 不再接受外部更新
        initial = record.initial
        for r in initial:
            self.reload(r.layer_tag, r.record_data)
        self.play_record = record
        self.play_index = 0
        self.play_range = range(len(record.updates))
        AsyncProxy.run(self.async_replay)

    def replay_by_index(self):
        self.play_mutex.lock()
        updates = self.play_record.updates
        if self.play_index in self.play_range:
            print(f"playing {self.play_index}/{len(updates) - 1}")
            upd = updates[self.play_index]
            if upd.record_type == RecordType.reload:
                self.reload(upd.layer_tag, upd.record_data)
            elif upd.record_type == RecordType.adjust:
                self.adjust(upd.layer_tag, upd.record_data)
                print("Warning: Adjustment not yet well supported.")
            else:
                raise
        self.play_mutex.unlock()

    def async_replay(self):
        while self.play_index in self.play_range:
            while self.pausing:
                time.sleep(0.5)
            self.replay_by_index()
            self.play_index += 1
            time.sleep(1)
        self.replaying = False
        self.suspended = False

    def fast_forward(self):
        if self.replaying:
            if self.play_index + 1 in self.play_range:
                self.play_index += 1
                self.replay_by_index()
                print(self.play_index)

    def back_forward(self):
        if self.replaying:
            if self.play_index - 1 in self.play_range:
                self.play_index -= 1
                self.replay_by_index()
                print(self.play_index)

    def pause(self):
        if self.replaying:
            self.pausing = not self.pausing
        else:
            self.suspended = not self.suspended

    def terminate(self):
        if self.recording:
            self.recording = False
            self.save_record(self.record)
        if self.replaying:
            self.replaying = False
            self.suspended = False
            self.play_index = self.play_range[-1]
