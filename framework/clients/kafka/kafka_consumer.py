__author__ = 'pavan.tummalapalli'

import logging

from kafka import KafkaConsumer, ConsumerRebalanceListener, OffsetAndMetadata, TopicPartition
from kafka.errors import KafkaError, CommitFailedError
from six import iteritems

from abstract_client import AbstractConsumer

logger = logging.getLogger(__name__)


class Consumer(AbstractConsumer):

    def __init__(self, **kwargs):

        assert kwargs , 'unrecognized configs'
        assert kwargs.get('client_config'), 'unrecognized client config'
        self.kwargs = kwargs

        super().__init__()

        try:
            self.consumer_client = KafkaConsumer(**kwargs.get('client_config'))
        except KafkaError as e:
            raise e

    def subscribe(self, topics, enable_listener=False):
        logger.info('subscribing to topics {}'.format(topics))
        if topics is None and len(topics) <= 0:
            raise Exception('topics should not be none')
        try:
            self.consumer_rebalance_listener = self.getRebalanceListener(enable_listener=enable_listener)
            self.consumer_client.subscribe(topics, listener=self.consumer_rebalance_listener)
        except (KafkaError, Exception) as e:
            raise e

    def seek(self, topic_partition, offset):
        """
        seek to specific partition.

        :param topic_partition: topic_partition object consists of topic and offset
        :type topic_partition: TopicPartition
        :param offset: offset to seek
        :type offset: int

        """
        try:

            self.consumer_client.seek(topic_partition, offset)
        except KafkaError as e:
            logger.exception('cant seek to specific offset')
            raise e

    def initial_poll(self, max_retries, timeout_ms=0):
        """
        when we subscribe to topics with ConsumerRebalanceListener, the consumer coordinator won't assign
        the specific partitions to the consumer unless the consumer poll.

        :param max_retries: maximum retries for polling
        :type max_retries: int
        :raises KafkaError
        """
        poll_success = False
        while max_retries > 0 and not poll_success:
            try:
                logger.info('polling consumer for topics specified')
                self.consumer_client.poll(timeout_ms=timeout_ms)
                poll_success = True
            except (KafkaError, Exception) as exc:
                logger.warning(exc, exc_info=True)
                max_retries -= 1
                if max_retries == 0:
                    raise KafkaError('Initial poll has failed to start the consumer-{}'.format(self.consumer_config.get('consusmer_id')))

    def assign(self, topic_partitions):
        """
        Manually assign a list of TopicPartitions to this consumer.

        :param topic_partitions: list of topic partition tuple
        :type topic_partitions: list
        :raises KafkaError
        """
        topic_partitions_list = list()
        for topic, partition in topic_partitions:
            tp = TopicPartition(topic, partition)
            topic_partitions_list.append(tp)
        try:
            self.consumer_client.assign(topic_partitions_list)
        except KafkaError as exc:
            logger.error(exc, exc_info=True)
            raise exc

    def assignment(self):
        """
        Get the TopicPartitions currently assigned to this consumer.

        If partitions were directly assigned using
        :meth:`~Consumer.assign`, then this will simply return the
        same partitions that were previously assigned.  If topics were
        subscribed using :meth:`~Consumer.subscribe`, then this will
        give the set of topic partitions currently assigned to the consumer
        (which may be None if the assignment hasn't happened yet, or if the
        partitions are in the process of being reassigned).

        :return: {TopicPartition, ...}
        :rtype: set
        """
        try:
            assignment = self.consumer_client.assignment()
            return assignment
        except KafkaError as exc:
            logger.error(exc, exc_info=True)
            raise exc

    def beginning_offsets(self, topic_partitions):
        """
        Get the first offset for the given partitions.
        This method does not change the current consumer position of the partitions.

        .. note::
            This method may block indefinitely if the partition does not exist.

        :param list of topic_partitions)
        :type list
        :return: The earliest available offsets for the given partitions.
        :rtype: ({TopicPartition: int})
        :raises KafkaError
        """
        try:
            res = self.consumer_client.beginning_offsets(topic_partitions)
            return res
        except KafkaError as e:
            raise e

    def seek_to_beginning(self, topic_partitions):
        """
        seek to beginning of the partitions
        :param topic_partitions:
        :type topic_partitions:
        :return:
        :rtype:
        """
        try:
            res = self.consumer_client.seek_to_beginning(topic_partitions)
            return res
        except KafkaError as e:
            raise e

    def consume(self, *args, **kwargs):
        timeout = kwargs.get('timeout') or self.kwargs.get('timeout') or 5
        max_records = kwargs.get('max_records') or self.kwargs.get('max_records') or 5
        try:
            records = iteritems(self.consumer_client.poll(timeout_ms=timeout, max_records=max_records))
            messages = []
            for record in records:
                if record is not None:
                    logger.debug(record)
                    # message returns tuple of (TopicPartition, list(ConsumerRecord)
                    for consumerRecord in record[1]:
                        logger.debug(consumerRecord)
                        messages.append(consumerRecord)
            return messages

        except (KafkaError, Exception) as e:
            raise e

    def commit(self, topic_partition_offset=None):
        """
        commit the last read offsets

        :param topic_partition_offset: list of topic, partition, tuple
        :type topic_partition_offset: list
        :raises CommitFailedError
        """
        if topic_partition_offset is not None:
            offsets = {
                TopicPartition(topic_partition_offset[0], topic_partition_offset[1]): OffsetAndMetadata(topic_partition_offset[2]+1, None)
            }
        else:
            offsets = None
        try:
            self.consumer_client.commit(offsets=offsets)
        except CommitFailedError as e:
            raise e

    def commit_async(self, offsets=None, callback=None):
        """
        Commit offsets to kafka asynchronously, optionally firing callback.
        This commits offsets only to Kafka.
        The offsets committed using this API will be used on the first fetch after every rebalance and also on startup.
        As such, if you need to store offsets in anything other than Kafka, this API should not be used.
        To avoid re-processing the last message read if a consumer is restarted, the committed offset should be the next message your application should consume, i.e.: last_offset + 1.

        :param offsets: dictionary of TopicPartition and OffsetAndMetadata
        :type offsets: (dict or None)
        :param: Called as callback(offsets, response)
        :type: (function or None)
        :return future object
        :rtype Future
        """
        try:
            self.consumer_client.commit_async(offsets, callback)
        except KafkaError as e:
            raise e

    def partitions_for_topic(self, topic):
        """
        Get metadata about the partitions for a given topic.

        :param topic: Topic to check.
        :type topic: str
        :return: Partition ids
        :rtype: set
        """
        try:
            partitions = self.consumer_client.partitions_for_topic(topic)
            return partitions
        except KafkaError as e:
            raise e

    class HandleRebalanceListener(ConsumerRebalanceListener):
        """
        class to handle partition assignments at the time of rebalanced.
        """

        def __init__(self, consumer_client):
            self.consumer_client = consumer_client

        def on_partitions_revoked(self, revoked):
            pass

        def on_partitions_assigned(self, assigned):
            pass

    def getRebalanceListener(self, enable_listener):
        """
        returns ConsumerRebalanceListener.

        :param enable_listener: if enabled ConsumerRebalanceListener will be used.
        :type enable_listener: bool
        :return: (ConsumerRebalanceListener or None)
        :rtype: Multiple
        """
        if enable_listener:
            return Consumer.HandleRebalanceListener(self.consumer_client)
        else:
            return None

    def serialize_message(self, message, *args, **kwargs):
        pass

    def deserialize_message(self, message, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        """
        Close the consumer, we can commit the messages if needed before closing.
        """
        if kwargs.get('autocommit') is not None:
            autocommit = kwargs.get('autocommit')
        else:
            autocommit = False
        logger.info('closing consumer....')
        self.consumer_client.close(autocommit)







