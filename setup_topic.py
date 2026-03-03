from confluent_kafka.admin import AdminClient, NewTopic

admin_client = AdminClient(
    {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'
    }
)

topic_name = 'pharma_sensor_logs'

new_topic = NewTopic(
    topic = topic_name,
    num_partitions = 3,
    replication_factor = 2,
    config = {
        'retention.ms': '3600000',
        'cleanup.policy': 'delete'
    }
)

print(f'Trying to create a new topic with topic name {topic_name}')
futures = admin_client.create_topics([new_topic])

for topic, future in futures.items():
    try:
        future.result()
        print(f'Topic created successfully !!!')
    except Exception as e:
        print(f'Failed to created the desired topic with the following error: {e}')