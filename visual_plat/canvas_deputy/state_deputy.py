import os
import pickle
import time
from enum import Enum
from dataclasses import dataclass

from visual_plat.render_layer.layer_base import LayerBase
from visual_plat.global_proxy.config_proxy import ConfigProxy
from visual_plat.global_proxy.async_proxy import AsyncProxy
from visual_plat.shared.utility.status_bar import StatusBar


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
    updates: list[list[RecordUnit]]


class StateDeputy:
    record_path = ""

    def __init__(self, layers: dict[str, LayerBase], status_bar: StatusBar):
        super().__init__()
        self.layers = layers
        self.status_bar = status_bar
        self.record: Record = Record([], [])
        self.pausing = False  # 播放暂停
        self.blocked = False  # 异步线程阻塞
        self.suspended = False  # 拒绝接受更新
        self.recording = False
        self.replaying = False
        self.play_index = 0
        self.play_range = None
        self.play_record = None
        StateDeputy.record_path = ConfigProxy.path("record")
        if not os.path.exists(StateDeputy.record_path):
            os.mkdir(StateDeputy.record_path)

    def block(self):
        """切换阻塞状态"""
        self.blocked = not self.blocked
        if self.blocked:
            self.status_bar.set("Blocked")
        else:
            self.status_bar.reset("Blocked")

    def reload(self, layer_tag: str, data=None, new_step=True):
        """重载某个图层"""
        if layer_tag in self.layers.keys():
            self.layers[layer_tag].reload(data)
            record = RecordUnit(layer_tag, RecordType.reload, data)
            if self.recording:
                if new_step:
                    self.record.updates.append([])
                self.record.updates[-1].append(record)

    def adjust(self, layer_tag: str, data=None, new_step=True):
        """调整某个图层"""
        if layer_tag in self.layers.keys():
            self.layers[layer_tag].adjust(data)
            record = RecordUnit(layer_tag, RecordType.adjust, data)
            if self.recording:
                if new_step:
                    self.record.updates.append([])
                self.record.updates[-1].append(record)

    @staticmethod
    def load_record(path):
        """解析记录"""
        with open(path, 'rb') as rcd:
            res = pickle.load(rcd)
        return res

    @staticmethod
    def save_record(record: Record):
        """保存记录"""
        rcd_name = time.strftime(
            '%y%m%d-%H%M%S',
            time.localtime(time.time())
        ) + f"-{len(record.updates) + 1}"
        path = StateDeputy.record_path + rcd_name + ".rcd"
        with open(path, 'wb') as rcd:
            pickle.dump(record, rcd)
        print(f"Record saved as {rcd_name}.rcd")
        return path

    def snapshot(self):
        """截图并保存"""
        record = Record([], [])
        for tag, layer in self.layers.items():
            record.initial.append(RecordUnit(tag, RecordType.reload, layer.data))
        return self.save_record(record)

    def start_record(self):
        """开始录制"""
        if not self.recording:
            self.status_bar.set("Recording")
            self.record = Record([], [])
            for tag, layer in self.layers.items():
                self.record.initial.append(RecordUnit(tag, RecordType.reload, layer.data))
            self.recording = True
            self.status_bar.set("Recording")

    def start_replay(self, record: Record):
        """开始播放"""
        initial = record.initial
        for r in initial:
            self.reload(r.layer_tag, r.record_data)
        self.play_record = record
        self.play_index = 0
        self.play_range = range(len(record.updates))
        if record.updates:
            # 避免在刷新snapshot时设置为悬置状态
            self.replaying = True
            self.suspended = True  # 不再接受外部更新
            self.status_bar.set("Replaying")
            self.status_bar.set("Suspended")
            AsyncProxy.run(self.async_replay)

    def replay_by_index(self):
        """播放某一帧"""
        updates = self.play_record.updates
        if self.play_index in self.play_range:
            self.status_bar.set("Replaying", f"{self.play_index + 1}/{len(updates)}")
            for upd in updates[self.play_index]:
                if upd.record_type == RecordType.reload:
                    self.reload(upd.layer_tag, upd.record_data)
                elif upd.record_type == RecordType.adjust:
                    self.adjust(upd.layer_tag, upd.record_data)
                    print("Warning: Adjustment not yet well supported.")

    def async_replay(self):
        """异步播放控制"""
        while self.replaying:
            while self.pausing:
                time.sleep(0.5)
            self.replay_by_index()
            self.play_index += 1
            if self.play_index > self.play_range[-1]:
                self.play_index = 0
            time.sleep(1)

    def fast_forward(self):
        """快进"""
        if self.replaying and self.pausing:
            if self.play_index + 1 in self.play_range:
                self.play_index += 1
                self.replay_by_index()

    def back_forward(self):
        """倒退"""
        if self.replaying and self.pausing:
            if self.play_index - 1 in self.play_range:
                self.play_index -= 1
                self.replay_by_index()

    def pause(self):
        """暂停"""
        if self.replaying:
            self.pausing = not self.pausing
            if self.pausing:
                self.status_bar.set("Paused")
            else:
                self.status_bar.reset("Paused")
        else:
            self.suspended = not self.suspended
            if self.suspended:
                self.status_bar.set("Suspended")
            else:
                self.status_bar.reset("Suspended")

    def terminate(self):
        """终止（优先终止播放，再次触发会终止录制）"""
        if self.replaying:
            self.replaying = False
            self.suspended = False
            self.status_bar.reset("Replaying")
            self.status_bar.reset("Suspended")
            self.play_index = self.play_range[-1]
            print("Replaying terminated.")
        elif self.recording:
            self.recording = False
            self.status_bar.reset("Recording")
            self.save_record(self.record)
            print("Recording terminated.")
