## Updated to use v3 of Bus Arrival API

import requests
import datetime
import json
import pickle
import os
import argparse
import re

def arrivein(datestring, monitored):
    if datestring == "":
        return "Arrival time not available"
    currtime = datetime.datetime.now()
    arrivaltime = datetime.datetime.fromisoformat(datestring)
    # Unix time
    difftime = arrivaltime.timestamp() - currtime.timestamp()

    if (difftime < -30):
        return "Arrival time is in the past"
    if (difftime > 30):
        # v3 of Bus Arrival API added the Monitored status = {0,1}
        # 0 if estimate is based on schedule
        # 1 if estimate is based on bus location
        monitoredstatus = ""
        if monitored == 0:
            monitoredstatus = "*"
        return "Arrival in " + monitoredstatus + str(round(difftime/60.0)) + "m"
    # If arrival time is within +/- 30s of current time
    monitoredstatus = ""
    if monitored == 0:
        monitoredstatus = "*"
    return monitoredstatus + "Arrived"

def printdesc(stopslist, stopcode):
    for stop in stopslist:
        if stop["BusStopCode"] == stopcode:
            return stop["Description"] + ", " + stop["RoadName"]
    return ""

# Please set the datamall API key in the environment variable DATAMALLAPIKEY
# We refrain from hardcoding the API key in the script
# apikey = 'APIKEY'
try:
    apikey = os.environ["DATAMALLAPIKEY"]
except:
    apikey = ""

# API Key is provided in the headers via the AccountKey field - see API documentation
headers = {'AccountKey': apikey ,'accept': 'application/json'}

uri = "https://datamall2.mytransport.sg"
path = "/ltaodataservice/v3/BusArrival?"
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


#if len(sys.argv) == 2:
#    inputarg = sys.argv[1]
#else:
#    print("Options:")
#    print("5 digit stop code (e.g. 01112) - displays arrival information")
#    print("ls - list recent bus stops")
#    print("int - list terminals and interchanges")
#    print("clr - clear recent bus stops")
#    print("update - update bus stop database")
#    exit()

commands = {"ls", "int", "clr", "update"}

def validate(arg):
    # For argparse validation
    if arg in commands:
        return arg
    if re.match(r"^\d{5}$", arg):
        return arg

    raise argparse.ArgumentTypeError("Invalid input!")


helptext = "[ XXXXX | ls | int | clr | update ], where XXXXX is the 5 digit stop code (e.g. 01112) - displays arrival information; ls - list recent bus stops; int - list terminals and interchanges; clr - clear recent bus stops; update - update bus stop database"

parser = argparse.ArgumentParser(description="Simple script that displays bus arrival information")
parser.add_argument("input", type=validate, help=helptext)
args = parser.parse_args()


if args.input == "update":
    # updates the bus stop database
    # API only provides 500 records at a time
    # pathbusstops = "/ltaodataservice/BusStops"
    if apikey == "":
        exit("Missing API key!")
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

if args.input == "int":
    fp = open("sgbusintlist.txt", "r")
    filecontent = fp.read()
    print(filecontent)
    exit()

if args.input == "clr":
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

if args.input == "ls":
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
stopcode = args.input
stopdescription = printdesc(busstopslist, stopcode)
if (stopdescription == ""):
    exit("Stop does not exists!")

if apikey == "":
    exit("Missing API key!")
    
try:
    url = uri + path + "BusStopCode=" + stopcode

    response = requests.get(url, headers=headers)
    responsetxt = response.text
    # print(responsetxt)
    d = json.loads(responsetxt)
except:
    exit("Error retrieving arrival information!")

print()
print("Stop number " + stopcode + " - " + stopdescription)
print("-------------")
for service in d["Services"]:
    servicenumber = service["ServiceNo"]
    print("Svc " + servicenumber + " Arrival Times")
    print(arrivein(service["NextBus"]["EstimatedArrival"],service["NextBus"]["Monitored"]) + " (" + vehtype[service["NextBus"]["Type"]] + ")")
    print(arrivein(service["NextBus2"]["EstimatedArrival"], service["NextBus2"]["Monitored"]) + " (" + vehtype[service["NextBus2"]["Type"]] + ")")
    print(arrivein(service["NextBus3"]["EstimatedArrival"], service["NextBus3"]["Monitored"]) + " (" + vehtype[service["NextBus3"]["Type"]] + ")")
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
