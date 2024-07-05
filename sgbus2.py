import requests
import datetime
import json
import sys
import pickle
import os

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

apikey = 'D2zTkzWOS9i4MvzsW/7p2g=='

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
# stopcode = "42011" # along Bt Timah Rd, near Sixth Ave


if len(sys.argv) == 2:
    inputarg = sys.argv[1]
else:
    print("Options:")
    print("5 digit stop code (e.g. 01112) - displays arrival information")
    print("ls - list recent bus stops")
    print("int - list terminals and interchanges")
    print("clr - clear recent bus stops")
    print("update - update bus stop database")
    exit()
    
if inputarg == "update":
    # updates the bus stop database
    # API only provides 500 records at a time
    # pathbusstops = "/ltaodataservice/BusStops"
    skiprecords = 0
    numrecords = 500
    busstoplist = []
    while numrecords > 0:
        pathbusstops = "/ltaodataservice/BusStops?$skip=%d" % skiprecords
        url = uri + pathbusstops
        response = requests.get(url, headers=headers)
        responsetxt = response.text
        d = json.loads(responsetxt)
        numrecords = len(d['value'])
        print("%d records read" % numrecords)
        if numrecords > 0:
            busstoplist.extend(d['value'])
        skiprecords += 500

    pin = open("busstops.pickle", "wb")
    pickle.dump(busstoplist, pin)
    pin.close()
    exit()

if inputarg == "int":
    fp = open("sgbusintlist.txt", "r")
    filecontent = fp.read()
    print(filecontent)
    exit()

if inputarg == "clr":
    if os.path.isfile("recentstops.pickle"):
        emptylist = []
        pin = open("recentstops.pickle", "wb")
        pickle.dump(emptylist, pin)
        pin.close()
    exit("List of recent stops cleared")

# Reads the bus stops list which contains descriptions and road names
try:
    pin = open("busstops.pickle", "rb")
    busstopslist = pickle.load(pin)
    pin.close()
except:
    exit("Bus stop database does not exist!\nPlease update the bus stop database\nusing the update option before using this script!")

# Choose action according to inputarg
# 'ls' - list 10 recent stops
# 'clr' - clear list of recent stops
# 'update' - update list of bus stops
# 5-digit stop code - show bus arrival information at this stop

if inputarg == "ls":
    if os.path.isfile("recentstops.pickle"):
        pin = open("recentstops.pickle", "rb")
        recentstopslist = pickle.load(pin)
        pin.close()
        recentstopslist.reverse()
        print("Recent stops")
        for stopcode in recentstopslist:
            print("Stop number " + stopcode + " - " + printdesc(busstopslist,stopcode))
        print()
        exit()
    else:
        exit("List of recent stops not found!")
        
# Checks if stop exists in busstopslist
stopcode = inputarg
stopdescription = printdesc(busstopslist, stopcode)
if (stopdescription == ""):
    exit("Stop does not exists!")

try:
    url = uri + path + "BusStopCode=" + stopcode

    response = requests.get(url, headers=headers)
    responsetxt = response.text
    d = json.loads(responsetxt)
except:
    exit("Error retrieving arrival information!")

print()
print("Stop number " + stopcode + " - " + stopdescription)
print("-------------")
for service in d["Services"]:
    servicenumber = service["ServiceNo"]
    print("Svc " + servicenumber + " Arrival Times")
    print(arrivein(service["NextBus"]["EstimatedArrival"]) + " (" + vehtype[service["NextBus"]["Type"]] + ")")
    print(arrivein(service["NextBus2"]["EstimatedArrival"]) + " (" + vehtype[service["NextBus2"]["Type"]] + ")")
    print(arrivein(service["NextBus3"]["EstimatedArrival"]) + " (" + vehtype[service["NextBus3"]["Type"]] + ")")
    print("-------------")

print()

# Update/add to recent stop list
if os.path.isfile("recentstops.pickle"):
    pin = open("recentstops.pickle", "rb")
    recentstopslist = pickle.load(pin)
    pin.close()
    try:
        recentstopslist.remove(stopcode)
        recentstopslist.append(stopcode)
    except ValueError:
        if len(recentstopslist) == 10:
            recentstopslist.pop(0)
        recentstopslist.append(stopcode)
    pin = open("recentstops.pickle", "wb")
    pickle.dump(recentstopslist, pin)
    pin.close()
else:
    # create recentstops.pickle file
    pin = open("recentstops.pickle", "wb")
    recentstopslist = [stopcode]
    pickle.dump(recentstopslist, pin)
    pin.close()
