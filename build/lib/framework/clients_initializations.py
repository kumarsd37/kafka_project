__author__ = 'pavan.tummalapalli'


import logging

from kafka.errors import NoBrokersAvailable, KafkaError

from framework.clients.file import FileWriter
from framework.clients.kafka import Consumer
from framework.clients.kafka import Producer

logger = logging.getLogger(__name__)


def getKafkaConsumer(**consumer_client_config):
    try:
        logger.info('creating consumer client....')
        consumer_client = Consumer(**consumer_client_config)
    except (NoBrokersAvailable, KafkaError, Exception) as exc:
        logger.error(exc, exc_info=True)
        raise exc
    return consumer_client


def getKafkaProducer(**producer_client_config):
    try:
        logger.info('creating producer client....')
        producer_client = Producer(**producer_client_config)
    except (KafkaError, Exception) as exc:
        logger.error(exc, exc_info=True)
        raise exc
    return producer_client


def getFileWriter(**file_config):
    try:
        logger.info('creating file writer client.....')
        file_client = FileWriter(**file_config)
        return file_client
    except IOError as exc:
        logger.error(exc, exc_info=True)
        raise exc


client_initialize_mappings = dict()

client_initialize_mappings['file_writer'] = getFileWriter
client_initialize_mappings['kafka_producer'] = getKafkaProducer
client_initialize_mappings['kafka_consumer'] = getKafkaConsumer

# todo : try to individual initilizations python file and import the initialization file in mapping python file.
# todo : update the client_initialize_mappings dictionary.
# todo: try to use register command line option to update the mapping dictionary file.


