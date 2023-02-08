from scipy.spatial import ConvexHull
from scipy.spatial import Delaunay
import numpy as np
import matplotlib.pyplot as plt
import os


def cal_hull(points):
    # 先画底层，画一次即可
    y_min, y_max = x_min, x_max = 0, 6
    grid_x, grid_y = np.meshgrid(np.arange(x_min, x_max), np.arange(y_min, y_max))
    grid = np.c_[grid_x.ravel(), grid_y.ravel()]  # ravel 是 numpy 库中的一个方法，意思是将多维数组降为一维。

    plt.scatter(grid[:, 0], grid[:, 1], color='gray', alpha=0.5)

    for i in range(len(points)):
        # 对每个aoi每个路径进行计算
        point = np.delete(np.unique(np.array(points[i]), axis=0), -1, axis=0)  # 去除重复点和6,6点
        x, y = point[:, 0], point[:, 1]
        if len(np.unique(x)) == 1 or len(np.unique(y)) == 1:  # 如果x或者y坐标都相同，说明是一条直线，不存在凸包，没有可能有任何内部点
            hull_points=inner_points = point
        else:
            hull = ConvexHull(np.array(point))  # 计算凸包
            tri = Delaunay(point)# 计算凸包内部点的索引
            inner_points_idx = [i for i, point in enumerate(grid) if tri.find_simplex(point) >= 0]  # 计算凸包内部点的索引
            inner_points = grid[inner_points_idx]
            hull_points = point[hull.vertices]
        visual(point, hull_points, grid, inner_points, i)
    plt.gca().invert_yaxis()  # 左上角为原点


def visual(point, hull, grid, inner_points, id):
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    plt.scatter(inner_points[:, 1], inner_points[:, 0], color=colors[id], alpha=0.5)
    plt.plot(hull[:, 1], hull[:, 0], 'k--', lw=2, color=colors[id])

def inputpath():
    from util import ws
    path = os.path.join(ws, 'data', 'manu_data', '6_6')
    points = np.load(os.path.join(path, 'traj.npy'), allow_pickle=True)
    return points,path


if __name__ == '__main__':
    points,path= inputpath()
    for point,i in zip(points,range(len(points))):
        cal_hull(point)
        plt.savefig(os.path.join(path, 'aoi2_{}.png'.format(i)))
        plt.clf()