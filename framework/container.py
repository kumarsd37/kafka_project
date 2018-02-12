__author__ = 'pavan.tummalapalli'

from multi_process_handler import ProcessHandler
from worker import Worker
from weakref import WeakValueDictionary, WeakSet
import settings


class Container:
    """ """
    #metrics_registry = MetricsRegistry()

    def __init__(self, msg_processor, error_handler, **kwargs):
        self.error_handler = error_handler
        self.workers_list = WeakSet()
        self.num_of_workers = kwargs.get('num_of_workers')
        self.worker_settings = kwargs.get('worker_settings')

        if not msg_processor:
            raise Exception('target should not be none')
        self.msg_processor = msg_processor
        self.create_workers()

    def create_workers(self):
        for num in range(0, self.num_of_workers):
            worker = Worker(self.msg_processor, **self.worker_settings)
            self.workers_list.add(worker)

    def start(self):
        for worker in self.workers_list:
            ProcessHandler.start_child_process(worker)
        ProcessHandler.join_all()

    def stop(self):
        pass

    def get_metrics(self):
        pass






