from utils.float_tooltip import FloatTooltip
from collections import defaultdict
import timeit


class XPSChecker:
    def __init__(self, tooltip: FloatTooltip = None):
        self.tooltip = tooltip
        self.cache = defaultdict(float)
        self.last_head = ""

    def start(self):
        self.cache.clear()
        self.last_head = ""
        self.cache[""] = timeit.default_timer()

    def set_tooltip(self, tip: FloatTooltip):
        self.tooltip = tip

    def check(self, head: str, tail: str = "", dif_from: str = "-1", factor: int = 1, no_tooltip: bool = False):
        self.cache[head] = timeit.default_timer()
        if dif_from == "-1":
            dif_from = self.last_head
        diff = self.cache[head] - self.cache[dif_from]
        xps = int(1 / diff * factor)
        if self.tooltip is not None and not no_tooltip:
            self.tooltip.set(head, str(xps) + tail)
        else:
            print(f"{head}: {str(xps)}{tail}")
        self.last_head = head
