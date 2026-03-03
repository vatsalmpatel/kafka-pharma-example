import json
import sys
from confluent_kafka import Consumer, KafkaError

conf = {
    'bootstrap.servers' : 'localhost:9092,localhost:9093,localhost:9094',
    'group.id' : 'pharma-sensor-monitoring-group',
    'auto.offset.reset' : 'earliest',
    'enable.auto.commit' : True
}

consumer = Consumer(conf)
topic_name = 'pharma_sensor_logs'

consumer.subscribe([topic_name])
worker_id = sys.argv[1] if len(sys.argv) > 1 else 'Worker-1'

print(f"[{worker_id}] Starting up... Joining group 'pharma-sensor-monitoring-group'")
print(f"[{worker_id}] Waiting for Kafka to assign a partition...")

try:
    while True:
        msg = consumer.poll(timeout = 1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._Partition_EOF:
                continue
            else:
                print(f'[{worker_id}] Error: {msg.error()}')
                break
        
        record_value = msg.value().decode('utf-8')
        sensor_data = json.loads(record_value)
        zone = sensor_data['zone']
        temp = sensor_data['temperature_celsius']
        partition = msg.partition()
        print(f"[{worker_id}] Read Partition [{partition}] | {zone} | Temp: {temp}°C")
except KeyboardInterrupt:
    print(f"\n[{worker_id}] Shutting down...")
finally:
    consumer.close()
    print(f"[{worker_id}] Successfully disconnected from cluster.")