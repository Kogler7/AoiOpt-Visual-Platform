import sys
from grid_world.thread_launcher import ThreadLauncher
from PySide6.QtWidgets import QApplication
from grid_world.grid_world import GridWorld


def show_world():
    app = QApplication([])
    world = GridWorld()

    # world.data_deputy.read_aoi("./data/aoi/AOI_20_grid.npy")
    world.data_deputy.read_aoi("./data/images/2.jpg")
    # world.data_deputy.read_traces("./data/trace/trace_1.npy")
    # world.data_deputy.read_parcels("./data/parcels/parcels_n.npy")

    indexes = range(10)
    bias = 1
    # world.trace_layer.set_indexes(indexes)
    # world.parcel_layer.set_indexes(indexes)

    world.show()

    learn_thread = ThreadLauncher(world.aoi_layer.reload)
    learn_thread.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    show_world()
