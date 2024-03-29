# TTools
TTools: Simple toolkit to generate the road network and POIs in any city. Traffic updates and taxi requests (passengers and drivers) in NYC and Chicago can also be generated.

#### 1. How to generate the road network and POIs ? (New York City for example)

```bash
cd ./RoadNetwork
python3 run.py -c "City name, i.e., 'New York City, New York, USA'"
```

### Output:

We output the road networks in './RoadNetwork/RoadNetworks/City Name' directory. Format of the road network file is as follows:

```csv
edges:
[source node, destination node, source latitude, source longitude, destination latitude, destination longitude, length, travel time(free flow), 0(Both for vehicle and pedestrian)/1(Pedestrian road)/2(Vehicle road)]

vertices:
[node Id, OSMID, latitude, longitude]

POIs:
[POI Id, latitude, longitude, source node of mapped edge, destination node of mapped edge, (length from source to POI/length of the edge), type, name(could be none)]
```

<hr>

#### 2. How to generate the traffic flow in New York (Chicago)?

Firstly, we have to generate the road network with the following command line.

For New York:
```bash
cd ./RoadNetwork
python3 run.py -c "New York City, New York, USA"
```

For Chicago:
```bash
cd ./RoadNetwork
python3 run.py -c "Chicago, Illinois, USA"
```

After that, we have to download the raw data with the following URL:

New York: [https://data.beta.nyc/dataset/nyc-real-time-traffic-speed-data-feed-archived](https://data.beta.nyc/dataset/nyc-real-time-traffic-speed-data-feed-archived)

Chicago: [https://data.cityofchicago.org/Transportation/Chicago-Traffic-Tracker-Congestion-Estimates-by-Se/n4j6-wkkf/data](https://data.cityofchicago.org/Transportation/Chicago-Traffic-Tracker-Congestion-Estimates-by-Se/n4j6-wkkf/data)

Download the raw data from the above URL and rename it as {Year}{Month}.csv such as 202102.csv in RawData directory (such as ./NYCTraffic/RawData)

Finally, we download the traffic data of that city from the start time to two hours later (must be in one day, the raw data contains that time period must be downloaded and renamed in a standard format) with the following command line.

```bash
cd NYCTraffic   # cd ChicagoTraffic
python run.py -t "2016-01-01 12:00"
```

### Output:
We output the traffic updates in "./NYCTraffic/ProcessedData" and "./ChicagoTraffic/ProcessedData", the format of the files is as follows.

```
[Source node, destination node, travel time, speed, timestamp]
```

The file name is combined with the start time and end time.

<hr>

#### 3. How to generate the taxi requests in New York City and Chicago?

Firstly, we have to download the raw data from the following URL:

New York City: [https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

Chicago: [https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew/data](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew/data)

and save it as the following format:

New York City: ./NYCTaxiData/RawData/yellow_tripdata_2016-01.csv

Chicago: ./ChicagoTaxiData/RawData/Taxi_Trips.csv

For New York, we download the yellow taxi data in a month, for Chicago, we download all taxi data before any time you want.

Then, you can generate the requests with the following command lines.

```bash
cd ./NYCTaxiData
python run.py -t "2016-01-01 12:00"
```

The taxi data in Chicago can be generated by simply replace the "./NYCTaxiData" with "./ChicagoTaxiData".

### Output:
```
Pedestrian Request line: [timeStamp, 0, Source latitude, Source longitude, destination latitude, destination longitude]
Vehicle Request line: [timestamp, 1, latitude, longitude]
```

if the second location of in a line is 0, which means it is a passenger request. If it is 1, it is a vehicle request.

<hr>

#### 4. Requirements:

```bash
pip3 install -r requirements.txt
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
```

#### 5. Who can benifit from this toolkit?
Someone who is lack of the Spatiotemporal data (or unfamiliar with the data process in mapping the POIs and traffics to road networks) to finish the experiments (No matter for your lesson or for your research). For some experts, we recommand you to use OSMnx, OSM API, networkX,  basic datastructure with java and the raw data directly.

If there exists some errors or you have some questions, please contact me with the following mail address: [ljinchnm@gmail.com](ljinchnm@gmail.com).

