import sys
from grid_world.thread_launcher import Learner
from PySide6.QtWidgets import QApplication
from grid_world.grid_world import GridWorld
from grid_world.proxy.async_proxy import AsyncProxy
from custom_layers.weight_layer import WeightAsyncLayer


def world_config(world: GridWorld):
    world.data_deputy.read_aoi("./data/aoi/AOI_20_grid.npy")
    world.aoi_layer.reload()
    # world.data_deputy.read_aoi("./data/images/2.jpg")
    # world.data_deputy.read_traces("./data/trace/trace_1.npy")
    # world.data_deputy.read_parcels("./data/parcels/parcels_n.npy")

    indexes = range(10)
    bias = 1
    # world.trace_layer.set_indexes(indexes)
    # world.parcel_layer.set_indexes(indexes)

    weight_layer = WeightAsyncLayer()


def async_config(world: GridWorld):
    learner = Learner(world.aoi_layer.reload)
    AsyncProxy.start(learner)


if __name__ == '__main__':
    app = QApplication([])
    grid_world = GridWorld()

    world_config(grid_world)
    # async_config(grid_world)

    grid_world.show()
    sys.exit(app.exec())
