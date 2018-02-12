__author__ = 'pavan.tummalapalli'

num_of_workers = 3

# worker type decides whether we want to run the worker using thread or process
worker_type = 'thread'
worker_thread_name_prefix = 'Test_workers_'

inbound_client = 'kafka'
outbound_client = 'kafka'

inbound_client_settings = {

        'max_retries': 3,
        'max_records': 1,
        'poll_timeout': 10,
        'enable_listener': True,
        'close_timeout': 5,
        'client_config':{
            'bootstrap_servers': '172.16.15.227:9092',
            #'security_protocol':'SSL',
            #'ssl_cafile': os.path.join(ssl_dir, 'ca.pem'),
            #'ssl_certfile': os.path.join(ssl_dir, 'service.cert'),
            #'ssl_keyfile': os.path.join(ssl_dir, 'service.key'),
            'group_id': '_'.join([inbound_topic, 'consumer_group']),
            'enable_auto_commit': False,
            'session_timeout_ms': 27000,
            'heartbeat_interval_ms': 9000,
            'auto_offset_reset': 'earliest'
        }
    }

outbound_client_settings = {

        'future_timeout': 5,
        'close_timeout': 5,
        'client_config': {
            'bootstrap_servers': '172.16.15.227:9092',
            #'security_protocol':'SSL',
            #'ssl_cafile': os.path.join(ssl_dir, 'ca.pem'),
            #'ssl_certfile': os.path.join(ssl_dir, 'service.cert'),
            #'ssl_keyfile': os.path.join(ssl_dir, 'service.key'),
            #'client_id': '_'.join([inbound_topic, 'producer_client']),
            'acks': 1,
            'retries': 1,
            'batch_size': 16384,
            'linger_ms': 5,
            'buffer_memory': 33554432,
            'connections_max_idle_ms': 9 * 60 * 1000,
            'max_block_ms': 60000,
            'max_request_size': 1048576,
            'metadata_max_age_ms': 300000,
            'retry_backoff_ms': 100,
            'request_timeout_ms': 30000,
            'max_in_flight_requests_per_connection': 5,
        }
 }
