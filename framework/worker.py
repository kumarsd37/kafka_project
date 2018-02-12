__author__ = 'pavan.tummalapalli'

from multiprocessing import Process


class Worker(Process):

    def __init__(self):
        pass

    def process_and_dispatch(self, message):
        """
        process the message using processor and dispatch the processed result to outbound client.
        :param message: message to be processed
        :type message:
        :return:
        :rtype:
        """
        pass

    def run_with_handler(self, target, error_handler):
        try:
            target.func(message)
        except ('get the error handlers'):
            ''' check what exceptions to raise and what exceptions to ignore '''

    def run(self, target=None):
        pass

    def close(self):
        pass

