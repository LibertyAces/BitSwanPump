# BitSwan BSPump ElasticSearch performance


## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload size:  `{ "name" : "Chuck Norris" }`  


## Sink

 * `./perf-es-sink.py`: 170 kEPS
 * `./perf-baseline-sink.py`: 243 kEPS (not sending events to ElasticSearch)


*kEPS stands for kilo (1000) events per second*

_Disclaimer_: Your mileage may vary eg. due to a size of the JSON to parse.
