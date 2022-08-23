import math

import numpy as np
from PySide6.QtCore import QPointF, QPoint, QRect, QRectF, QSize


def int_2d(src: QPointF):
    """对点取整"""
    _x = int(src.x())
    _y = int(src.y())
    return QPoint(_x, _y)


def dec_int_2d(src: QPointF):
    """
    分别取整数和小数部分函数的2D版本
    返回两个点组成的元组
    第一个元素是小数部分组成的点
    第二个元素是整数部分组成的点
    """
    _x = math.modf(src.x())
    _y = math.modf(src.y())
    decimal = QPointF(_x[0], _y[0])
    integer = QPoint(int(_x[1]), int(_y[1]))
    return decimal, integer


def mod_2d(src: QPointF, op: float):
    """对二维点取模"""
    _x = src.x() % op
    _y = src.y() % op
    return QPointF(_x, _y)


def great_than_2d(op1: QPoint, op2: QPoint):
    """
    点的大小比较
    当且仅当op1>op2时返回True
    """
    return op1.x() > op2.x() and op1.y() > op2.y()


def trans_rect(rect: QRect, bias: QPoint, delt: QSize):
    """对Rect做变换"""
    _p = QPoint(rect.x(), rect.y()) + bias
    _s = rect.size() + delt
    return QRect(_p, _s)


def mul_rect(rect: QRect, factor: int):
    """对Rect的长宽做乘积"""
    _p = QPoint(rect.x(), rect.y()) * factor
    _s = QSize(rect.width(), rect.height()) * factor
    return QRect(_p, _s)


def rect_bias(rect: QRect):
    """返回Rect的左上顶点"""
    return QPoint(rect.x(), rect.y())


def size2point(size: QSize):
    """Size转化为Point"""
    return QPoint(size.width(), size.height())


def mul_pot(p1: QPointF, p2: QPointF):
    """两点乘积"""
    return QPointF(p1.x() * p2.x(), p1.y() * p2.y())


def square_size(size: int):
    """方形Size"""
    return QSize(size, size)


def square_point(bias: int):
    """方形偏移点"""
    return QPoint(bias, bias)


def in_rect(p: QPoint, r: QRect):
    """判断点是否在某个Rect中"""
    return r.x() <= p.x() <= r.right() and r.y() <= p.y() <= r.bottom()


def rect_overlap(r1: QRect, r2: QRect):
    """
    判断两个矩形是否重叠
    有额外裕度，以服务实际应用
    """
    return (r2.right() + 1 - r1.x()) * (r1.right() + 1 - r2.x()) > 0 and \
           (r2.bottom() + 1 - r1.y()) * (r1.bottom() + 1 - r2.y()) > 0


def area_of_points(p_lst: list[QPoint]):
    """返回点集所在的最小矩形区域"""
    lp = QPoint(99999999, 99999999)
    rp = QPoint(-9999999, -9999999)
    for p in p_lst:
        lp.setX(min(lp.x(), p.x()))
        lp.setY(min(lp.y(), p.y()))
        rp.setX(max(rp.x(), p.x()))
        rp.setY(max(rp.y(), p.y()))
    return QRect(lp, rp)


def area_of_array(arr: np.array):
    """功能同上"""
    lp = QPoint(99999999, 99999999)
    rp = QPoint(-9999999, -9999999)
    for p in arr:
        lp.setX(min(lp.x(), p[1]))
        lp.setY(min(lp.y(), p[0]))
        rp.setX(max(rp.x(), p[1]))
        rp.setY(max(rp.y(), p[0]))
    return QRect(lp, rp)
