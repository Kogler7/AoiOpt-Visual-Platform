import json


class GridWorldConfig:
    def __init__(self, f_path: str):
        self.root: str = "./"
        self.aoi_data_path: str = "data/aoi.npy"
        self.trace_data_path: str = "data/trace.npy"
        self.parcel_data_path: str = "data/parcel.npy"
        self.abc = {"haha": "baba"}

        self.parse(f_path)

    def parse(self, path):
        with open(path, 'r') as f:
            print(json.load(f))

    def save(self):
        print(json.dumps(self.__dict__))


if __name__ == "__main__":
    cfg = GridWorldConfig("../data/config.json")
    # cfg.save()
