import os
from random import randint, uniform

with open("config.txt") as f:
	content = f.readlines()
content = [x for x in content if not x == "\n"]

config = {}

#dictionary containing all elements
for elem in content:
	split = elem.split("=")
	split[0] = split[0].strip()
	split[1] = split[1].strip("\n").strip()
	if split[0] != "CBM" and split[0] != "CEM" and split[0] != "MaxEurosMinute" and split[0] != "MaxEurosKm":
		try:
			config[split[0]] = int(split[1])
		except:
			print("Variable " + split[0] + " must be an integer")
	else:
		try:
			config[split[0]] = float(split[1])
		except:
			print("Variable " + split[0] + " must be a float")

if "nServices" in config.keys():
	nServices = config["nServices"]
else:
	nServices = 10
if "nDrivers" in config.keys():
	nDrivers = config["nDrivers"]
else:
	nDrivers = 10
if "nBuses" in config.keys():
	nBuses = config["nBuses"]
else:
	nBuses = 5
if "maxBuses" in config.keys():
	maxBuses = config["maxBuses"]
else:
	maxBuses = 5
if "BM" in config.keys():
	BM = config["BM"]
else:
	BM = 50
if "CBM" in config.keys():
	CBM = config["CBM"]
else:
	CBM = 0.5
if "CEM" in config.keys():
	CEM = config["CEM"]
else:
	CEM = 0.75
if "PeriodTime" in config.keys() and config["PeriodTime"] <= 480:
	PeriodTime = config["PeriodTime"]
else:
	PeriodTime = 480
if "MaxMinService" in config.keys() and config["MaxMinService"] <= 480:
	MaxMinService = config["MaxMinService"]
else:
	MaxMinService = 50
if "MaxKMService" in config.keys() and config["MaxKMService"] <= 50:
	MaxKMService = config["MaxKMService"]
else:
	MaxKMService = 50
if "MaxPassengersService" in config.keys() and config["MaxPassengersService"] <= 75:
	MaxPassengersService = config["MaxPassengersService"]
else:
	MaxPassengersService = 75
if "MaxBusCapacity" in config.keys() and config["MaxBusCapacity"] <= 40:
	MaxBusCapacity = config["MaxBusCapacity"]
else:
	MaxBusCapacity = 40
if "MaxEurosMinute" in config.keys() and config["MaxEurosMinute"] <= 5.0:
	MaxEurosMinute = config["MaxEurosMinute"]
else:
	MaxEurosMinute = 0.5
if "MaxEurosKm" in config.keys() and config["MaxEurosKm"] <= 5.0:
	MaxEurosKm = config["MaxEurosKm"]
else:
	MaxEurosKm = 0.5
if "MaxDriver" in config.keys() and config["MaxDriver"] <= 400:
	MaxDriver = config["MaxDriver"]
else:
	MaxDriver = 400

# Services
ST = []
DM = []
DK = []
NP = []

# Buses
cap = []
eurosMin = []
eurosKm = []

# Drivers
maxD = []

for i in range(0, nServices):
	ST.append(randint(0, PeriodTime - 1))
	DM.append(randint(0, min((PeriodTime - ST[i]), MaxMinService)))
	DK.append(randint(0, MaxKMService))
	NP.append(randint(0, MaxPassengersService))

for i in range(0, nBuses):
	cap.append(randint(MaxBusCapacity/2, MaxBusCapacity))
	eurosMin.append(round(uniform(0, MaxEurosMinute), 2))
	eurosKm.append(round(uniform(0, MaxEurosKm), 2))

for i in range(0, nDrivers):
	maxD.append(randint(PeriodTime/2, MaxDriver))

with open("data.dat", "w+") as f:
	f.write("nServices = " + str(nServices) + ";\n")
	f.write("nDrivers = " +  str(nDrivers) + ";\n")
	f.write("nBuses = " + str(nBuses) + ";\n")
	f.write("maxBuses = " + str(maxBuses) + ";\n")
	f.write("BM = " + str(BM) + ";\n")
	f.write("CBM = " + str(CBM) + ";\n")
	f.write("CEM = " + str(CEM) + ";\n\n") # hasta aquí datos de entrada
	f.write("ST = " + repr(ST).replace(",", " ") + ";\n")
	f.write("DM = " + repr(DM).replace(",", " ") + ";\n")
	f.write("DK = " + repr(DK).replace(",", " ") + ";\n")
	f.write("NP = " + repr(NP).replace(",", " ") + ";\n\n") # hasta aquí services
	f.write("cap = " + repr(cap).replace(",", " ") + ";\n")
	f.write("eurosMin = " + repr(eurosMin).replace(",", " ") + ";\n")
	f.write("eurosKm = " + repr(eurosKm).replace(",", " ") + ";\n\n") # hasta aquí buses
	f.write("maxD = " + repr(maxD).replace(",", " ") + ";\n\n") # hasta aquí drivers
f.close()