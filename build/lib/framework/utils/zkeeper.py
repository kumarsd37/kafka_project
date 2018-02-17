__author__ = 'pavan.tummalapalli'

import logging

from kazoo.client import KazooClient, KazooState, KazooRetry
from kazoo.exceptions import NoNodeError

logger = logging.getLogger(__name__)


class ZkClient:

    def __init__(self, **zkConfig):
        """

        :param zkConfig:
        :type zkConfig:
        """
        self.logger = logging.getLogger(__name__) or logger

        self.zkHost = zkConfig.get('host')
        self.timeout = zkConfig.get('timeout')
        self.read_only = zkConfig.get('read_only')
        self.retrySettings = zkConfig.get('retry')
        self.kazooRetry = self.__getKazooRetry()
        self.zk = None

    def start(self):
        self.zk = KazooClient(hosts=self.zkHost, timeout=self.timeout, connection_retry=self.kazooRetry)
        self.zk.add_listener(self.__stateListener)
        self.zk.start()

    def __getKazooRetry(self):
        self.kazooRetry = KazooRetry(**self.retrySettings)
        return self.kazooRetry

    def getTopicPartitions(self, topic):
        """
        list all the partitions for the topic specified

        :param topic: topic name
        :type topic: str
        :return: partitions
        :rtype: list

        :raises Exception

        """
        zkTopicPartitionsPath = '/brokers/topics/' + topic + '/partitions'
        if self.zk.exists(zkTopicPartitionsPath):
            partitions = self.zk.get_children(zkTopicPartitionsPath)
        else:
            raise NoNodeError(" Node doesn't exists")
        return partitions

    def stop(self):
        self.zk.stop()

    def __stateListener(self, state):
        if state == KazooState.LOST:
            self.logger.warning("Connection lost to zookeeper")
        elif state == KazooState.SUSPENDED:
            self.logger.warning("Connection to zookeeper suspended")
