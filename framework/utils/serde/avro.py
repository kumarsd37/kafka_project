import io
import fastavro as avro


def write(records=None, schema=None):
    """
    serialize message with schema

    :param records: list of messages
    :type records: list
    :param schema: avro schema
    :type schema: dict
    :return: serialized message
    :rtype: bytearray
    """
    try:
        out = io.BytesIO()
        avro.writer(out, schema, records)
        return out.getvalue()
    except Exception as e:
        raise e


def read(records=None, schema=None):
    """
    deserialize message with or without schema

    :param records: list of messages
    :type records: list
    :param schema: avro schema
    :type schema: dict
    :return: deserialized message
    :rtype: Fastavro Iterator Object
    """
    try:
        op = io.BytesIO(records)
        reader = avro.reader(op, reader_schema=schema)
        return reader
    except Exception as e:
        raise e









