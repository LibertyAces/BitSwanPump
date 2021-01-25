# Kafka Topic Initializer

This tool connects to a specified Kafka cluster, checks if required topics are present 
and creates the missing ones. The new topics can be configured using a JSON or YAML file.

## Configuration

Configure the module and Kafka connection in the BSPump `.conf` file.
The recommended way is to specify a YAML or JSON `topics_file` with individual configuration of the topics.


```conf
[connection:KafkaConnection]
bootstrap_servers=
  kafka:19092
  kafka:29092

[KafkaTopicInitializer]
topics_file=topics.yml
```

The `topics.yml` file (shown below) holds the configuration for each required topic. 
The parameters `name`, `num_partitions` and `replication_factor` are mandatory. 
`topic_configs` holds the optional parameters, which can be found in 
the [official Kafka documentation](https://kafka.apache.org/documentation/#topicconfigs).

```yaml
- name: fine_topic
  num_partitions: 10
  replication_factor: 1
  topic_configs:
    retention.ms: 60000
- name: great_topic
  num_partitions: 1
  replication_factor: 3
```

Alternatively, it is possible to specify the topics directly in the `.conf` file without the need for the external file:

```conf
[KafkaTopicInitializer]
topics=fine_topic great_topic
num_partitions: 1
replication_factor: 1
```

However, this way it is not possible to configure the optional parameters.

## Example usage

Instantiate the `KafkaTopicInitializer`, passing `BSPumpApplication` instance and `KafkaConnection` ID as arguments. 
Then call the `check_and_initialize()` method before running the pipeline. 

```python
topic_initializer = bspump.kafka.KafkaTopicInitializer(app, "KafkaConnection")
topic_initializer.check_and_initialize()
```