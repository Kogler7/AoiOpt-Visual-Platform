from PySide6.QtCore import *
from abc import ABC, abstractmethod


class AsyncWorker(QObject):
    @abstractmethod
    def runner(self):
        pass


class AsyncProxy:
    pool = QThreadPool.globalInstance()

    def __new__(cls, *args, **kwargs):
        cls.pool.setMaxThreadCount(5)
        return cls.pool

    @staticmethod
    def start(worker: AsyncWorker):
        """申请线程执行 Worker"""
        AsyncProxy.pool.start(worker.runner)

    @staticmethod
    def run(runner, *args, **kwargs):
        """获取线程执行函数"""
        AsyncProxy.pool.start(runner, *args, **kwargs)

    def redirect(self):
        pass
