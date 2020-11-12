# BitSwan BSPump ElasticSearch Performance testing

Technology: ElasticSearch


## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload size:  `{ "name" : "Chuck Norris" }`  


## JsonBytesToDictParser

 * `./perf-jsonbytestodict.py`: 180 kEPS
 * `./perf-baseline.py`: 263 kEPS (not parsing JSONs)


*kEPS stands for kilo (1000) events per second*
