# BitSwan BSPump JSON Parsing performance


## Benchmarks

Client machine: `Intel(R) Xeon(R) CPU E3-1226 v3 @ 3.30GHz`  
Payload:  `{ "name" : "Chuck Norris" }`  


## Json To Dict Parsing

 * `./perf-jsonbytestodict.py`: 190 kEPS (using `JsonBytesToDict` and `orjson`)
 * `./perf-jsontodict.py`: 142 kEPS (using `JsonToDict` and `json` module from a standard Python library)
 * `./perf-baseline.py`: 263 kEPS (not parsing JSONs)


*kEPS stands for kilo (1000) events per second*

_Disclaimer_: Your mileage may vary eg. due to a size of the JSON to parse.
