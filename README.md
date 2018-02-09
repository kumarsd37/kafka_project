# kafka_project

Kafka project is a framework which injects the message processor logic into inbound and outbound producer and consumer.

Framework suports multiple producer clients to send the information processed from the processor logic

**Key functionalities of producer:**

- producer client should only need to provide kafka settings by default.
- providing synchronous and asynchronous sending data.
- additional settings are provided for concurrency.
- message filter based routing.
