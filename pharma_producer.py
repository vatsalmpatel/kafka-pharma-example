import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'client.id': 'pharma-iot-producer'
}

producer = Producer(conf)
topic_name = 'pharma_sensor_logs'

zones = [
    'Zone_A_Bioreactor',
    'Zone_B_ColdStorage',
    'Zonc_C_Packaging'
]

def safe_delivery_report(err,msg):
    if err is not None:
        print(f"Delivery failed with {err.name()} and code {err.code()}")
    else:
        print(f"Delivered {msg.key().decode('utf-8')} to partition [{msg.partition()}]")

def generate_sensor_reading():
    zone = random.choice(zones)

    if "Bioreactor" in zone:
        temp = round(random.uniform(36.5, 37.5), 2)
    elif "ColdStorage" in zone:
        temp = round(random.uniform(2.0, 8.0), 2)
    else:
        temp = round(random.uniform(20.0, 25.0), 2)

    humidity = round(random.uniform(40.0, 60.0), 1)
    
    return {
        'sensor_id': f"{zone}_Primary",
        'zone': zone,
        'temperature_celsius': temp,
        'humidity_percent': humidity,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }

print(f'Starting to publish data to topic {topic_name}')

try:
    while True:
        reading = generate_sensor_reading()
        json_payload = json.dumps(reading).encode('utf-8')
        message_key = reading['zone'].encode('utf-8')
        producer.produce(
            topic = topic_name,
            key = message_key,
            value = json_payloadc,
            callback = safe_delivery_report
        )

        producer.poll(0)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nStopping the producer due to a keyboard interrupt !!!")
finally:
    print("Flushing final records to the topic !!")
    producer.flush()
    print("Producer has finally closed successfully !!!")