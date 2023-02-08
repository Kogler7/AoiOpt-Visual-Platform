'''
根据包裹位置先用vrp算法规划路径，再将内部划分成1个aoi
这里的vrp数量要求必须固定
'''
import os
import numpy as np
import pandas as pd
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import warnings

warnings.filterwarnings("ignore")


# import utils.data_loader as dl


class GetGrid:
    def __init__(self, file):
        # file should be .csv or .npy(already have aoi)
        assert file[-3:] == "csv", "wrong input format, aoi file shoud be .csv"
        file_already=file.replace('csv', 'npy')
        #load aoi file as grid
        if ~os.path.exists(file):
            if os.path.exists(file_already):
                self.grid = np.load(file_already)
            else:
                raise FileNotFoundError("no such file {}".format(file))
        else:
            self.grid = pd.read_csv(file, names=None, header=None).to_numpy()
            np.save(file_already, self.grid)
        #load matrix file
        self.matrix = np.load(
            os.path.splitext(str.replace(file, 'aoi', 'matrix'))[0] + '.npy')
        self.h, self.w = self.grid.shape[-2], self.grid.shape[-1]
        self.file = file


    def get_dir(self):  # dir (h*w)*(h*w)
        try:
            return self.dir
        except:
            self.dijkstra()
            return self.dir

    def get_dis(self,path):  # dis (h*w)*(h*w)
        if os.path.exists(path):
            return np.load(path)
        else:
            self.dijkstra()
            np.save(os.path.splitext(str.replace(os.path.abspath(
                self.file), 'aoi', 'dis'))[0] + '.npy', self.dis)
            return self.dis

    def distance(self, h1, w1, h2, w2):
        return 1 / (self.matrix[h1 * self.w + w1][h2 * self.w + w2] + 1)#laplace平滑,倒数法计算权重，牛的一批

    def dijkstra(self):
        from queue import PriorityQueue as queue
        dis = np.zeros([self.h, self.w, self.h, self.w], dtype='int8') + np.inf
        dhs, dws = [0, -1, 1, 0, 0], [0, 0, 0, -1, 1]  # 中上下左右
        # dir_change = [0, 2, 1, 4, 3]
        for ih in range(self.h):
            for iw in range(self.w):
                dis[ih, iw, ih, iw] = 0
                vis = np.zeros([self.h, self.w], dtype='int8')
                q = queue()
                q.put((0, ih, iw))
                num = 1
                while num < self.h * self.w and not q.empty():
                    _, last_h, last_w = q.get()
                    if vis[last_h, last_w]:
                        continue
                    num += 1
                    for k in range(1, 5):
                        dh, dw = dhs[k], dws[k]
                        now_h = last_h + dh
                        now_w = last_w + dw
                        if now_h >= 0 and now_h < self.h and now_w >= 0 and now_w < self.w:
                            l = self.distance(last_h, last_w, now_h, now_w)
                            if not vis[now_h, now_w] and dis[ih, iw, now_h, now_w] > dis[ih, iw, last_h, last_w] + l:
                                dis[ih, iw, now_h, now_w] = dis[ih,
                                                                iw, last_h, last_w] + l
                                # dir[ih, iw, now_h, now_w] = dir_change[k]
                                q.put(
                                    (dis[ih, iw, now_h, now_w], now_h, now_w))
                    vis[last_h, last_w] = 1
        self.dis = dis
        # self.dir = dir


class GetTrajectory():
    # 读取包裹位置,并将其划分为div组
    def __init__(self, parcels, div):
        parcels = parcels.parcel_lst
        self.parcels = np.reshape(parcels, (div, parcels.shape[0] * parcels.shape[1] // div, parcels.shape[2]))

    def generate(self, h, w, dis, aoi, time_limit=1000):
        parcels = self.parcels
        self.h, self.w = h, w
        self.distance = dis
        self.aoi_num = aoi
        ans = []
        # 150*6*2->10*90*2
        parcels = np.insert(parcels, 0, values=(
            self.h, self.w), axis=1)  # 插入(h,w)使得随机开始
        # 准备就绪，开始循环读取所有包裹
        for j in range(len(parcels)):
            print("正在处理第%d组包裹" % j)
            self.location = parcels[j, :, :]  # 91*2
            # print(location)
            self.num_pcr = len(self.location)
            # RoutingIndexManager 的参数为 位置的数目，车辆数量，起始位置
            manager = pywrapcp.RoutingIndexManager(
                self.num_pcr, self.aoi_num, 0)
            self.manager = manager
            routing = pywrapcp.RoutingModel(manager)  # 创建路由模型

            transit_callback_index = routing.RegisterTransitCallback(
                self.distance_callback)  # 创建距离回调函数
            routing.SetArcCostEvaluatorOfAllVehicles(
                transit_callback_index)  # 设置两点之间的运输成本计算方法
            # 设置默认的搜索参数和用于寻找第一个解决方案的启发式方法:
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)  # 重复优化法
            search_parameters.time_limit.FromMilliseconds(int(time_limit))  # 100ms一个轨迹
            search_parameters.log_search = False

            solution = routing.SolveWithParameters(
                search_parameters)  # 核心——计算并获取最短距离

            self.route = {}
            for vehicle_id in range(self.aoi_num):
                index = routing.Start(vehicle_id)
                self.route[vehicle_id] = []
                self.route[vehicle_id].append(self.location[0].tolist())
                while not routing.IsEnd(index):
                    index = solution.Value(routing.NextVar(index))
                    self.route[vehicle_id].append(self.location[manager.IndexToNode(index)].tolist())
                print(self.route[vehicle_id])
            ans.append(self.route)
        return ans

    def distance_callback(self, from_index, to_index):  # 距离计算
        x1, y1 = self.location[self.manager.IndexToNode(from_index)]
        x2, y2 = self.location[self.manager.IndexToNode(to_index)]
        if x1 == self.h and y1 == self.w:
            return 0
        if x2 == self.h and y2 == self.w:
            return 0
        return int(1e3*self.distance[self.w * x1 + y1][self.w * x2 + y2])


class GetParcels():
    def __init__(self, grid):
        # grid:AOI划分矩阵  couriers:list，轨迹生成所在的AOI parcel_num:每条轨迹包裹个数
        self.grid = grid.grid
        self.h, self.w = grid.h, grid.w

    def get_from_file(self, file):
        self.parcel_lst = np.load(os.path.abspath(file))


if __name__ == '__main__':

    #core config
    aoi_num=30
    folder = 'data/shanghai/4'

    #load aoi
    from util import ws
    path = os.path.join(ws, folder)
    grid = GetGrid(os.path.join(path, 'aoi.csv'))

    #load parcels
    parcels = GetParcels(grid)
    parcels.get_from_file(os.path.join(path, 'parcels.prc'))

    traj = GetTrajectory(parcels, div=10)
    dis = grid.get_dis(os.path.join(path, 'dis.npy'))
    dis = dis.reshape([grid.h * grid.w, grid.h * grid.w])
    answer = traj.generate(grid.h, grid.w, dis, aoi=2,time_limit=1e3)
    np.save(os.path.join(path, 'traj.npy'), answer)