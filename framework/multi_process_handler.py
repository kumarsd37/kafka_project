__author__ = 'pavan.tummalapalli'

import logging
import weakref

logger = logging.getLogger(__name__)


class ProcessHandler:

    __child_processes = weakref.WeakValueDictionary()
    size = 10

    @staticmethod
    def start_child_process(target_obj, *args, **kwargs):
        logger.info('starting child process')
        target_obj.start()
        logger.info('started child process with processId {}'.format(target_obj.pid))
        ProcessHandler.__child_processes[target_obj.pid] = target_obj

    @staticmethod
    def terminate_all():
        logger.info('terminating all child processes')
        for pid, target_obj in ProcessHandler.__child_processes.items():
            child_pid = target_obj.pid
            logger.info('terminating child process-{}'.format(child_pid))
            target_obj.unset_event()
            logger.info('terminated child process-{}'.format(child_pid))

    @staticmethod
    def join(target_obj):
        target_obj.join()

    @staticmethod
    def join_all():
        logger.info('joining all child process, it makes parent process will wait until all child process stopped or terminated.')
        for target_obj in ProcessHandler.__child_processes.values():
            target_obj.join()

    @staticmethod
    def get_all_child_processes():
        target_objects = list()
        for target_object in ProcessHandler.__child_processes.values():
            target_objects.append(target_object)
        return target_objects

