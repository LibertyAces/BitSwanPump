# BitSwan BSPump ElasticSearch Performance testing

## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload size:  `{ "name" : "Chuck Norris" }`  


## Consumer

 * `./test-aiokafka-consumer.py`: 65 kEPS
 * `./test-fastkafka-consumer.py`: 149 kEPS
 * `./test-baseline-consumer.py`: 238 kEPS (not receiving events from Kafka)


*kEPS stands for kilo (1000) events per second*


## Build

	python3 setup.py build_ext --inplace


## Test

	python3 ./test-fastkafka-producer.py
	python3 ./test-fastkafka-consumer.py