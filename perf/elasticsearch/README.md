# BitSwan BSPump ElasticSearch Performance testing

## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload size:  `{ "name" : "Chuck Norris" }`  


## Sink

 * `./test-es-sink.py`: 243 kEPS
 * `./test-baseline-sink.py`: 170 kEPS (not sending events to ElasticSearch)


*kEPS stands for kilo (1000) events per second*
