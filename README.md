# Singapore bus arrival timing on Linux command line

This is a small and simple Python script that queries the bus arrival timing API from [LTA DataMall](https://datamall.lta.gov.sg/content/datamall/en.html) and displays the result on the command line. There are no distracting ads or crashy apps here - only whatever is needed to find out the bus arrival times. This has been tested and designed to run in an Android environment command line environment such as [termux](https://termux.dev/en/).

*Update 26 Aug 2024*: Script has been updated following the introduction of Bus Arrival API v3. The script `sgbus3.py` should be used. Usage instructions below should be updated.

## Usage

A Python interpreter needs to be installed, as well as the following Python libraries:

```
- requests
- datetime
- json
- sys
- pickle
- os
```

Once the script has been copied over to an appropriate directory, it can be run like any Python script: `python sgbus2.py <bus stop code/option>`.

There is a line in the script that sets the API key variable. This key can be obtained for free after signing up at the [LTA DataMall](https://datamall.lta.gov.sg/content/datamall/en.html) site. The line containing the assignment `apikey = <apikey>` should be edited to set up this key.

When this script run for the first time, the complete list of bus stop codes and descriptions should be downloaded using the `update` option: `python sgbus2.py update`. The script will store this list in a pickle file named `busstops.pickle`, which will be used in other sections of the script.

To obtain bus arrival timings for a stop, run the script with the 5-digit bus stop code as the only argument. This 5-digit code can be found at all bus stops in Singapore. The example below displays the arrival timings for bus stop number 01112, located somewhere near Bugis MRT Station.

```
$ python sgbus2.py 01112

Stop number 01112 - Opp Bugis Stn Exit C, Victoria St
-------------
Svc 12 Arrival Times
Arrival time is in the past (Single Deck)
Arrival in 9m (Double Deck)
Arrival in 19m (Single Deck)
-------------
Svc 12e Arrival Times
Arrival in 24m (Double Deck)
Arrival time not available ()
Arrival time not available ()
-------------
Svc 175 Arrival Times
Arrival in 2m (Single Deck)
Arrival in 18m (Single Deck)
Arrival time not available ()
-------------
Svc 197 Arrival Times
Arrival in 6m (Double Deck)
Arrival in 19m (Double Deck)
Arrival in 25m (Single Deck)
-------------
Svc 63 Arrival Times
Arrival in 16m (Single Deck)
Arrival in 19m (Single Deck)
Arrival in 27m (Single Deck)
-------------
Svc 7 Arrival Times
Arrival in 6m (Double Deck)
Arrival in 14m (Double Deck)
Arrival in 20m (Single Deck)
-------------
Svc 80 Arrival Times
Arrival in 23m (Double Deck)
Arrival in 29m (Single Deck)
Arrival in 42m (Double Deck)
-------------
Svc 851 Arrival Times
Arrival in 2m (Single Deck)
Arrival in 9m (Single Deck)
Arrival in 15m (Double Deck)
-------------
Svc 851e Arrival Times
Arrival in 17m (Single Deck)
Arrival time not available ()
Arrival time not available ()
-------------
Svc 960 Arrival Times
Arrival in 3m (Single Deck)
Arrival in 6m (Double Deck)
Arrival in 18m (Single Deck)
-------------
Svc 960e Arrival Times
Arrival in 15m (Single Deck)
Arrival time not available ()
Arrival time not available ()
-------------
Svc 980 Arrival Times
Arrival time is in the past (Single Deck)
Arrival in 11m (Single Deck)
Arrival in 31m (Single Deck)
-------------

```

This script also stores a list of 10 recently queried bus stop codes in the file `recentstops.pickle`. To display this list, use the `ls` option.

```
$ python sgbus2.py ls
Recent stops
Stop number 01112 - Opp Bugis Stn Exit C, Victoria St
Stop number 67391 - Blk 333B, Sengkang East Way
Stop number 42011 - Sixth Ave Ctr, Bt Timah Rd

```

This list can be cleared using the `clr` option: `python sgbus2.py clr`.

To display help text, run the script without any argument: `python sgbus2.py`.
