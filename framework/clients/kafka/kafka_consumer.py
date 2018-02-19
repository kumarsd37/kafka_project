__author__ = 'pavan.tummalapalli'

import logging

from kafka import KafkaConsumer, ConsumerRebalanceListener, OffsetAndMetadata, TopicPartition
from kafka.errors import KafkaError, CommitFailedError
from six import iteritems

from .meta import TopicPartitionOffset

from framework.abstract_client import AbstractConsumer

logger = logging.getLogger(__name__)


class Consumer(AbstractConsumer):

    def __init__(self, **kwargs):
        """
        constructor for kafka consumer

        :keyword Arguments

        - name (`str`) - name of the inbound client to create
        - config (`dict`) - config of kafka consumer client
            - topics (`list`) - list of topics to be subscribed by the each consumer
            - enable_external_commit (`bool`) - If True, offsets are stored at external client
            - external_commit_config (`dict`) - config for external commit client
                - redis (`dict`) -  config for storing external commit
                    - namespace (`str`) - common prefix for set of keys, which uniquely identifies the set of keys among all the keys.
                    - delimiter (`str`) - used in between joining namespace and key
                    - client_config (`dict`) - redis client config
                        - host (`str`) - redis host
                        - port (`str`) - redis port
                        - password (`str`) - redis password. default null
                        - db_number (`int`) - By default redis open 16 db's while creating connection. we can specify specific db number to open it at the time of creating the connection.
                        - max_connections (`int`) - maximum number of connections to be opened in pooling.

            - client-config: (`dict`) - kafka python consumer client settings

        .. Note:: kafka consumer client Configuration parameters are described in more detail at http://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html#
        """

        # checking if kwargs are present
        assert kwargs, 'unrecognized configs'
        self.kwargs = kwargs

        # checking if kafka consumer client_config is present or not.
        assert kwargs.get('client_config'), 'unrecognized client config'
        self.client_config = kwargs.get('client_config')

        assert self.client_config.get('group_id'), 'group_id should not be None'
        self.group_id = self.client_config.get('group_id')

        # initialize the auto commit by getting the enable auto commit value from config
        # if client config has no auto commit set by default it will be False.
        self.enable_auto_commit = self.client_config.get('enable_auto_commit') or False

        # check if external
        self.enable_external_commit = kwargs.get('enable_external_commit')

        if self.enable_external_commit:
            assert kwargs.get('external_commit_config'), 'external commit config missing'
            self.external_commit_config = kwargs.get('external_commit_config')

        # we will pass internal commit or external commit to based upon the setting.
        self._commit = None

        # used at the time of consumer rebalanced
        self.handle_rebalance_listener = None

        assert kwargs.get('topics'), 'topics should not be none'
        self.topics = kwargs.get('topics')

        self.poll_timeout = kwargs.get('poll_timeout') or 500
        self.max_records = kwargs.get('max_records') or 1

        super().__init__()

        try:
            self.consumer_client = KafkaConsumer(**self.client_config)
            self.subscribe(topics=self.topics, listener=self.get_rebalance_listener())

            if self.enable_auto_commit and self.enable_external_commit:
                raise Exception('cant commit to kafka and external simultaneously')
            elif self.enable_external_commit:
                try:
                    self.external_commit_client = self.create_external_commit_dao(self.external_commit_config)
                    self._commit = self.external_commit
                except (KeyError, Exception) as exc:
                    raise exc
            elif not self.enable_auto_commit:
                self._commit = self.internal_commit

        except KafkaError as exc:
            raise exc

    def subscribe(self, topics, listener=None):
        """
        subscribe to list of topics to be specified. if consumer group_id is specified, listener will be
        invoked at the time of each rebalance operation

        :param topics: list of topics
        :type topics: list
        :param listener: object of kafka-python ConsumerRebalanceListener (optional, default: None)
        :type listener: ConsumerRebalanceListener
        :raises: KafkaError: if not able to subscribe to topics
        :raises Exception: unhandled exception
        """
        logger.info('subscribing to topics {}'.format(topics))
        if not topics and len(topics) <= 0:
            raise Exception('topics should not be none')
        try:
            self.consumer_client.subscribe(topics, listener=listener)
        except (KafkaError, Exception) as exc:
            raise exc

    def seek(self, topic_partition, offset):
        """
        seek to specific partition

        :param topic_partition: topic_partition object consists of topic and offset
        :type topic_partition: TopicPartition
        :param offset: offset to seek
        :type offset: int

        """
        try:

            self.consumer_client.seek(topic_partition, offset)
        except KafkaError as exc:
            logger.exception('cant seek to specific offset')
            raise exc

    def assign(self, topic_partitions):
        """
        Manually assign a list of TopicPartitions to this consumer

        :param topic_partitions: list of topic partition tuple
        :type topic_partitions: list(TopicPartition)
        :raises KafkaError: if unable to assign the partition
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
        Get the TopicPartitions currently assigned to this consumer

        If partitions were directly assigned using
        :meth:`~Consumer.assign`, then this will simply return the
        same partitions that were previously assigned.  If topics were
        subscribed using :meth:`~Consumer.subscribe`, then this will
        give the set of topic partitions currently assigned to the consumer
        (which may be None if the assignment hasn't happened yet, or if the
        partitions are in the process of being reassigned)

        :return: {TopicPartition, ...}
        :rtype: set
        """
        try:
            assignment = self.consumer_client.assignment()
            return assignment
        except KafkaError as exc:
            logger.error(exc, exc_info=True)
            raise exc

    def beginning_offsets(self, topic_partition_offsets):
        """
        Get the first offset for the given partitions
        This method does not change the current consumer position of the partitions

        :param topic_partition_offsets: list of topic_partition_offsets
        :type topic_partition_offsets: list(TopicPartitionOffset)
        :return: The earliest available offsets for the given partitions
        :rtype: list(TopicPartitionOffset)
        :raises KafkaError: if not able to find the beginning offsets
        """
        topic_partition_list = list()
        for topic_partition_offset in topic_partition_offsets:
            topic_partition = TopicPartition(topic_partition_offset.topic, topic_partition_offset.partition)
            topic_partition_list.append(topic_partition)
        try:
            res = self.consumer_client.beginning_offsets(topic_partition_list)
            return res
        except KafkaError as exc:
            raise exc

    def seek_to_beginning(self, topic_partitions):
        """
        seek to beginning of the partitions

        :param topic_partitions: list of topic partition objects
        :type topic_partitions: list(TopicPartition)
        """
        try:
            res = self.consumer_client.seek_to_beginning(topic_partitions)
            return res
        except KafkaError as exc:
            raise exc

    def pre_consume(self, *args, **kwargs):
        """ operation need to be performed before pre consume """
        pass

    def consume(self, *args, **kwargs):
        """
        consumes the batch of messages from polling
        """

        try:
            records = iteritems(self.consumer_client.poll(timeout_ms=self.poll_timeout, max_records=self.max_records))
            messages = []
            for record in records:
                if record is not None:
                    logger.debug(record)
                    # message returns tuple of (TopicPartition, list(ConsumerRecord)
                    for consumerRecord in record[1]:
                        logger.debug(consumerRecord)
                        messages.append(consumerRecord)
            return messages

        except (KafkaError, Exception) as exc:
            raise exc

    def post_consume(self, *args, **kwargs):
        """
        operation need to performed after consuming the message
        """
        if self._commit:
            message = args[0]
            topic_partition_offset = TopicPartitionOffset(message.topic, message.partition, message.offset)
            try:
                self.commit(topic_partition_offset)
            except Exception as exc:
                logger.error(exc.__str__(), exc_info = True)

    def create_external_commit_dao(self, config):
        """
        create external commit client object

        :param config: config of redis
        :type config: dict
        :return: external commit client object
        :rtype: KafkaRedisOffsetCommitDAO
        """
        from framework.utils.caching.redis_pool import RedisPoolConnection
        from .redis_commit import KafkaRedisOffsetCommitDAO
        try:
            redis_config = config['redis']['client_config']
            consumer_group = self.group_id
            namespace = config.get('redis').get('namespace')
            delimiter = config['redis'].get('delimiter') or ':'
            redis_pooled_connection = RedisPoolConnection(**redis_config)
            kafka_redis_offset_commit_dao = KafkaRedisOffsetCommitDAO(redis_pooled_connection, consumer_group=consumer_group, namespace=namespace, delimiter=delimiter)
            return kafka_redis_offset_commit_dao
        except (KeyError, Exception) as exc:
            logger.error(exc.__str__())
            raise exc

    def external_commit(self, topic_partition_offset=None):
        """
        commit the offset to external client

        :param topic_partition_offset: Topic Partition Offset object
        :type topic_partition_offset: TopicPartitionOffset
        :raises ConnectionError: if unable to connect to redis
        :raises TimeoutError: if timeout has occurred
        :raises Exception: if unhandled exception has occurred
        """
        try:
            response = self.external_commit_client.commit_offset(topic_partition_offset)
            if not response:
                raise Exception('kafka external commit failed for topic:{}, partition:{} and offset:{}'.format(topic_partition_offset.topic, topic_partition_offset.partition, topic_partition_offset.offset))
        except (ConnectionError, TimeoutError, Exception) as exc:
            logger.exception(str(exc))
            raise exc

    def last_committed_offset_from_external(self, topic_partition_offset):
        """
        :param topic_partition_offset: Topic Partition Offset object
        :type topic_partition_offset: TopicPartitionOffset
        :return: topic partition offset
        :rtype: TopicPartitionOffset
        :raises ConnectionError: if unable to connect to redis
        :raises TimeoutError: if timeout has occurred
        :raises Exception: if unhandled exception has occurred
        """
        try:
            tpo = self.external_commit_client.get_topic_partition_offset(topic_partition_offset)
        except (ConnectionError, TimeoutError, Exception) as exc:
            logger.exception(str(exc))
            raise exc
        return tpo

    def internal_commit(self, topic_partition_offset):
        """
        commit the last read offsets

        :param topic_partition_offset: list of topic, partition, tuple
        :type topic_partition_offset: list(TopicPartitionOffset)
        :raises CommitFailedError: if unable to commit to kafka. it occurs when consumer rebalanced happened
        """
        if topic_partition_offset is not None:
            offsets = {
                TopicPartition(topic_partition_offset.topic, topic_partition_offset.partition): OffsetAndMetadata(
                    topic_partition_offset.offset + 1, None)
            }
        else:
            offsets = None
        try:
            self.consumer_client.commit(offsets=offsets)
        except CommitFailedError as exc:
            raise exc

    def last_committed_offset(self, topic_partition_offset):
        tpo = TopicPartition(topic_partition_offset.topic, topic_partition_offset.partition)
        try:
            offset = self.consumer_client.committed(tpo)
        except KafkaError as exc:
            raise exc
        return offset

    def commit_async(self, topic_partition_offset=None, callback=None):
        """
        Commit offsets to kafka_client asynchronously, optionally firing callback
        This commits offsets only to Kafka
        The offsets committed using this API will be used on the first fetch after every rebalance and also on startup
        As such, if you need to store offsets in anything other than Kafka, this API should not be used
        To avoid re-processing the last message read if a consumer is restarted, the committed offset should be the next message your application should consume, i.e.: last_offset + 1

        :param topic_partition_offset: topic partition offset
        :type topic_partition_offset: TopicPartitionOffset
        :param callback: Called as callback(offsets, response)
        :type callback: function, optional
        :raises CommitFailedError: if unable to commit to kafka. it occurs when consumer rebalanced happened
        """
        if topic_partition_offset is not None:
            offsets = {
                TopicPartition(topic_partition_offset.topic, topic_partition_offset.partition): OffsetAndMetadata(
                    topic_partition_offset.offset + 1, None)
            }
        else:
            offsets = None

        try:
            self.consumer_client.commit_async(offsets, callback)
        except KafkaError as exc:
            raise exc

    def commit(self, topic_partition_offset=None):
        """
        commit the offsets to either internal client or external client

        :param topic_partition_offset: Topic Partition Offset object
        :type topic_partition_offset: TopicPartitionOffset
        """
        self._commit(topic_partition_offset)

    def partitions_for_topic(self, topic):
        """
        Get metadata about the partitions for a given topic

        :param topic: Topic to check
        :type topic: str
        :return: Partition ids
        :rtype: set
        """
        try:
            partitions = self.consumer_client.partitions_for_topic(topic)
        except KafkaError as exc:
            raise exc
        return partitions

    def on_partitions_assigned(self, assigned):
        """
        list of assigned partitions after each consumer rebalance operation

        :param assigned: list of topic partition objects
        :type assigned: list(TopicPartition)
        """
        if self.enable_external_commit:
            for tp in assigned:
                topic = tp.topic
                partition = tp.partition
                tpo = self.external_commit_client.get_topic_partition_offset(TopicPartitionOffset(topic, partition, None))
                logger.info('last committed offset for topic:{} , partition:{} is {}'.format(topic, partition, tpo.offset))
                if tpo.offset:
                    self.consumer_client.seek(tp, tpo.offset)
                    
    def on_partitions_revoked(self, revoked):
        """
        list of partitions revoked after each consumer rebalance operation

        :param revoked: list of topic partition objects
        :type revoked: list(TopicPartition)
        """
        pass

    def get_rebalance_listener(self):
        """ return the object of ConsumerRebalanceListener  """

        HandleRebalanceListener = type('HandleRebalanceListener', (ConsumerRebalanceListener,),
            {
                'on_partitions_assigned': self.on_partitions_assigned,
                'on_partitions_revoked': self.on_partitions_revoked
             }
        )
        self.handle_rebalance_listener = HandleRebalanceListener()
        return self.handle_rebalance_listener
        
    def deserialize_message(self, message, *args, **kwargs):
        """ deserialize the message """
        pass

    def close(self, *args, **kwargs):
        """
        Close the consumer, we can commit the messages if needed before closing
        """
        logger.info('closing kafka consumer consumer....')
        self.consumer_client.close()