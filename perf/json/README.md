# BitSwan BSPump ElasticSearch Performance testing

Technology: ElasticSearch


## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload size:  `{ "name" : "Chuck Norris" }`  


## JsonBytesToDictParser

 * `./test-jsonbytestodict-sink.py`: 180 kEPS
 * `./test-baseline.py`: 263 kEPS (not parsing JSONs)


*kEPS stands for kilo (1000) events per second*
