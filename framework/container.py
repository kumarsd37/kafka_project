import threading

__author__ = 'pavan.tummalapalli'

from worker import Worker
import logging

logger = logging.getLogger(__name__)


class Container:
    
    __workers_list = dict()
    __error_handler = None
    __message_processor = None
    __num_of_workers = None
    __inbound_client_settings = None
    __outbound_client_settings = None
    
    @staticmethod
    def create_container(msg_processor, **kwargs):
        #__class__.__error_handler = error_handler
        __class__.__num_of_workers = kwargs.get('num_of_workers')
        __class__.__inbound_client_settings = kwargs.get('inbound_client_settings')
        __class__.__outbound_client_settings = kwargs.get('outbound_client_settings')

        if not msg_processor:
            raise Exception('msg_processor should not be none')
        __class__.__msg_processor = msg_processor
        __class__.create_workers()

        for key in __class__.__workers_list.keys():
            logger.debug('key is {}'.format(key))

    @staticmethod
    def create_workers():
        for num in range(0, __class__.__num_of_workers):
            try:
                __class__.__workers_list[num] = Worker(__class__.__msg_processor, __class__.__inbound_client_settings, __class__.__outbound_client_settings)
            except Exception as exc:
                logger.error(exc, exc_info=True)
                raise exc


    @staticmethod
    def start():
        logger.debug('total number of worker threads {}'.format(len(list(__class__.__workers_list.keys()))))
        for worker_object in __class__.__workers_list.values():
            worker_object.start()
            logger.info('started new worker thread {}'.format(worker_object.ident))
        __class__.join_all()

    @staticmethod
    def join_all():
        for worker_object in __class__.__workers_list.values():
            worker_object.join()

    @staticmethod
    def stop():
        for worker in __class__.__workers_list.values():
            logger.info('I am clearing ....')
            if worker.event.is_set():
                worker.clear_event()

    @staticmethod
    def get_metrics():
        pass






