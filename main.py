import sys

from PySide6.QtWidgets import QApplication
from grid_world import GridWorld


def show_world():
    app = QApplication([])
    world = GridWorld()

    # world.data_deputy.read_aoi("./data/AOI_20_grid.npy")
    world.data_deputy.read_aoi("./data/2.jpg")
    world.data_deputy.read_traces("./data/trace/trace_1.npy")
    world.data_deputy.read_parcels("./data/parcels_n.npy")

    indexes = range(1000)
    bias = 1
    world.render_deputy.trace_indexes = indexes
    world.render_deputy.parcels_indexes = indexes

    world.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    show_world()
