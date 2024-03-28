import requests
import datetime
import json
import sys
import pickle

def arrivein(datestring):
    if datestring == "":
        return "Arrival time not available"
    currtime = datetime.datetime.now()
    arrivaltime = datetime.datetime.fromisoformat(datestring)
    # Unix time
    difftime = arrivaltime.timestamp() - currtime.timestamp()

    if (difftime < -30):
        return "Arrival time is in the past"
    if (difftime > 30):
        return "Arrival in " + str(round(difftime/60.0)) + "m"
    # If arrival time is within +/- 30s of current time
    return "Arrived"

def printdesc(stopslist, stopcode):
    for stop in stopslist:
        if stop["BusStopCode"] == stopcode:
            return stop["Description"] + ", " + stop["RoadName"]
    return ""

apikey = 'aaaaaaaaaaaaaaaaaaaaaaaa'

# API Key is provided in the headers via the AccountKey field - see API documentation
headers = {'AccountKey': apikey ,'accept': 'application/json'}

uri = "http://datamall2.mytransport.sg"
path = "/ltaodataservice/BusArrivalv2?"
occupancy = {"SEA" : "Seats Available", "SDA" : "Standing Available", "LSD" : "Limited Standing"}
vehtype = {"SD" : "Single Deck", "DD" : "Double Deck", "BD" : "Bendy", "" : ""}
# To fix the above - temporary hack to prevent key error when referencing empty vehicle type value

# This API accepts one mandatory parameter and one optional
# BusStopCode (mandatory) e.g. 83139
# ServiceNo (optional) e.g. 15
# stopcode = "83139"
# stopcode = "14039"
# stopcode = "67391" # SK bus stop
# stopcode = "08057" # stop near PS, Dhoby Ghaut MRT
# stopcode = "03218" # stop in CBD along Shenton Way
# stopcode = "01112" # stop opposite Bugis Junction
stopcode = "42011" # along Bt Timah Rd, near Sixth Ave

if len(sys.argv) == 2:
    stopcode = sys.argv[1]

url = uri + path + "BusStopCode=" + stopcode

response = requests.get(url, headers=headers)
responsetxt = response.text
d = json.loads(responsetxt)

# Reads the bus stops list which contains descriptions and road names
pin = open("busstops.pickle", "rb")
busstopslist = pickle.load(pin)
pin.close()

print()
print("Stop number " + stopcode + " - " + printdesc(busstopslist, stopcode))
print("-------------")
for service in d["Services"]:
    servicenumber = service["ServiceNo"]
    print("Svc " + servicenumber + " Arrival Times")
    print(arrivein(service["NextBus"]["EstimatedArrival"]) + " (" + vehtype[service["NextBus"]["Type"]] + ")")
    print(arrivein(service["NextBus2"]["EstimatedArrival"]) + " (" + vehtype[service["NextBus2"]["Type"]] + ")")
    print(arrivein(service["NextBus3"]["EstimatedArrival"]) + " (" + vehtype[service["NextBus3"]["Type"]] + ")")
    print("-------------")

print()
