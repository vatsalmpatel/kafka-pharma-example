# High-Availability Kafka Pipeline: Pharmaceutical IoT Sensor Telemetry

## Project Overview
In pharmaceutical manufacturing, strict environmental control is critical. Bioreactors, cold-storage units, and packaging zones require real-time, fault-tolerant monitoring. Missing a single temperature anomaly due to a server crash can result in compromised vaccines or therapeutics.

This project implements an enterprise-grade, highly available Apache Kafka data pipeline designed to ingest, route, and process live IoT sensor telemetry from multiple manufacturing zones. 

### Key Features
* **Multi-Broker Cluster:** Utilizes a 3-node Kafka cluster with Zookeeper for distributed processing.
* **Fault Tolerance (High Availability):** Configured with a Replication Factor of 2. The pipeline survives intentional broker termination (Chaos Engineering) with zero data loss.
* **Parallel Processing (Consumer Groups):** Data is partitioned by manufacturing zone across 3 partitions, allowing multiple consumer instances to process the stream simultaneously.
* **Data Retention Policies:** Configured for automatic ephemeral storage management (1-hour retention) to prevent disk overflow in high-velocity streaming environments.

## Architecture


* **Producer:** Python script simulating high-frequency JSON payloads of temperature and humidity readings.
* **Broker:** 3 Kafka nodes running locally via Docker Compose.
* **Consumers:** Python scripts acting as a Consumer Group, parallel-processing specific partitions based on the sensor's manufacturing zone.

## 🛠️ Prerequisites
* **Docker & Docker Compose:** To orchestrate the Kafka cluster.
* **Python 3.9+**
* **uv:** Fast Python package and virtual environment manager.

> **Note for macOS Users:** If running this project from an external ExFAT/FAT32 drive, virtual environment symlinks may fail. It is recommended to run this project from your internal macOS drive.

## Setup and Execution

### 1. Spin Up the Infrastructure
Start the 3-node Kafka cluster and Zookeeper in the background using Docker Compose.

```bash
docker-compose up -d
```

### 2. Set Up the Python Environment
Initialize your virtual environment using uv and install the Confluent Kafka client.

```bash
uv init
uv add confluent-kafka
```

### 3. Configure the Kafka Topic
Run the setup script to provision the pharma_sensor_logs topic. This defines the 3 partitions, replication factor of 2, and the 1-hour retention policy.

```bash
uv run setup_topic.py
```

### 4. Start the IoT Producer
Launch the producer to begin generating and streaming simulated telemetry from the Bioreactor, Cold Storage, and Packaging zones.

```bash
uv run pharma_producer.py
```

(Leave this terminal window running).

### 5. Launch the Distributed Consumer Group
To see Kafka's parallel processing in action, open multiple new terminal windows. In each new window, activate the environment (source .venv/bin/activate) and start a consumer worker:

Terminal 2 (Worker A):
```bash
uv run pharma_consumer.py Worker-A
```

Terminal 3 (Worker B):
```bash
uv run pharma_consumer.py Worker-B
```

Terminal 4 (Worker C):
```bash
uv run pharma_consumer.py Worker-C
```

Watch the terminal outputs as Kafka automatically rebalances the cluster, eventually assigning exactly one manufacturing zone (partition) to each worker.

## Chaos Engineering: Testing Fault Tolerance
To prove the resilience of the replication factor, simulate a hardware failure while the producer and consumers are actively processing data:

Open a new terminal and forcefully kill one of the brokers:

```Bash
docker stop kafka-2
```

Observe the output: The producer and consumers will seamlessly failover to the surviving brokers (kafka-1 and kafka-3). No sensor readings will be dropped.

Bring the node back online to watch the cluster heal and sync the missing data:
```Bash
docker start kafka-2
```

## Tear Down
To stop the cluster and completely remove the Docker containers, networks, and volumes, run:
```Bash
docker-compose down -v
```