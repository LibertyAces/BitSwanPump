# BitSwan BSPump JSON Parsing performance


## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload:  `{ "name" : "Chuck Norris" }`  


## JsonBytesToDictParser

 * `./perf-jsonbytestodict.py`: 190 kEPS (using `orjson`)
 * `./perf-jsontodict.py`: 142 kEPS (using `json` module from a standard Python library)
 * `./perf-baseline.py`: 263 kEPS (not parsing JSONs)


*kEPS stands for kilo (1000) events per second*
