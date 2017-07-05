#!/usr/bin/env python2.7

###	Import ###
import os, sys
import SocketServer as ss
import socket as s
from urllib2 import urlopen as get
import datetime as d
import time as t
import json as j
import ast
import math

###   Define   ###
### Parameters ###
class NETWORKHANDLER:
	def __init__(self):
		self.depth 		= 0			# current depth while scanning [of Friends]^(D-1) layers
		self.subNetworkList = []	# subnetwork of a node (id) contructed per D specification
		self.node_init 	= ""		# initial node (id) the scanning of a network
		self.NETWORK = {}			# contains the network's pertinent information
									# format: { "id":{"FL":[],"PH":[],"NPS":[]} , ... }
									#	FL:FriendsList, PH:PurchaseHistory, NPS:NetworkPurchaseStatistics
									#	NPS is a two-item list containing subnetwork (wrt node or id) mean, sd
		self.T = 30					# time range metric corresponding to amount of entries to consider
		self.D = 3					# [Friends]*[of Friends]^(D-1) are considered the subnetwork of a node (id)
	def reset(self):				# resets subnetwork calculated for a node (id)
		for n in range(0,len(self.subNetworkList)):
			self.subNetworkList.remove(self.subNetworkList[len(self.subNetworkList)-1])
NH = NETWORKHANDLER()

###  Define   ###
### Functions ###
def path():
	###	returns current directory above in string format
	dirUp = os.path.dirname(os.path.realpath(sys.argv[0])).split("/")
	dirUp_ = ""
	for n in range(1,len(dirUp)-1) :
		dirUp_ = dirUp_ + "/" + dirUp[n]
	return dirUp_

def mean(set):
	### returns mean of argumentative list
	sum = 0.0
	for n in range(0,len(set)):
		sum = float(set[n]) + sum
	mean = float(sum)/float((len(set)))
	return mean

def sigma(set):
	### returns standard deviation of argumentative list
	var = 0.0
	for n in range(0,len(set)):
		var = (float(set[n])-mean(set))**2 + var
	sigma = var/float(len(set))
	sigma = math.sqrt(sigma)
	return sigma

def updatePH(id_,change):
	###	updates PurchaseHistory (PH) corresponding to str(id) and str(change) provided
	###		list full (defined by T) : removes earliest record (index 0), inserts at last (latest)
	###		list not full (defined by T) : appends to list
	set = NH.NETWORK[id_]["PH"]
	if len(set) >= NH.T:
		set.remove(set[0])	
		set.insert(len(set)-1,change)
	if len(set) < NH.T:
		set.insert(len(set)-1,change)
	NH.NETWORK[id_]["PH"] = set

def updateFL(id_a,id_b,change):
	###	updates FriendList (FL) corresponding to str(id)s and str(change) provided
	if (id_a in NH.NETWORK) & (id_b in NH.NETWORK) :		# only permit friend changes between networked individuals
		if (change == "befriend") :
			if (id_b not in NH.NETWORK[id_a]["FL"]) :
				NH.NETWORK[id_a]["FL"].append(id_b)
			if (id_a not in NH.NETWORK[id_b]["FL"]) :
				NH.NETWORK[id_b]["FL"].append(id_a)
		if (change == "unfriend") :
			if (id_b in NH.NETWORK[id_a]["FL"]) :
				NH.NETWORK[id_a]["FL"].remove(id_b)
			if (id_a in NH.NETWORK[id_b]["FL"]) :
				NH.NETWORK[id_b]["FL"].remove(id_a)

def subNetworkList(idSet,self_):
	### accepts as first argument list of str(id)s, returns list of [Friends]*[of Friends]^(D-1) 
	###	second parameter passed, self, determines whether initial node should be included (1), or not (0), in list
	if (NH.depth == 0) & (self_ == 0) :	#	------------------------------------	# if scan is beginning
		NH.node_init = idSet[0]	#	--------------------------------------------	# store initial id to remove later
	if (NH.depth < NH.D) :	#	------------------------------------------------	# if scan depth set by D not attined ...
		for m in range(0,len(idSet)) :	#	------------------------------------	# for each id in idSet ...
			if (idSet[m] in NH.NETWORK) :	#	--------------------------------	# if id in Network ...
				if (idSet[m] not in NH.subNetworkList) :	#	----------------	# if id in idSet is not in list
					NH.subNetworkList.append(idSet[m])		#	----------------	# append to list
				for n in range(0,len(NH.NETWORK[idSet[m]]["FL"])) :	#	--------	# for each friend of id ... 
					if (NH.NETWORK[idSet[m]]["FL"][n] not in NH.subNetworkList) :	# if friend not on subnetwork list ...
						NH.subNetworkList.append(NH.NETWORK[idSet[m]]["FL"][n])		# add friend to subNetworkList
		NH.depth = NH.depth +1	#	--------------------------------------------	# depth of scan incrememnted
		subNetworkList(NH.subNetworkList,self_)	#	----------------------------	# send amassed subnetwork list to function to further amass, per D specification
		return NH.subNetworkList	#	----------------------------------------	# return incompletely amassed subnetwork list
	if (NH.depth == NH.D) :	#	------------------------------------------------	# if scan depth set by D is attained...
		NH.depth = 0	#	----------------------------------------------------	# reset depth tracker
		if (NH.node_init in NH.subNetworkList) & (self_ == 0) :	#	------------	#
			NH.subNetworkList.remove(NH.node_init)	#	------------------------	# remove initial node id if present if self is set to zero
		return NH.subNetworkList	#	----------------------------------------	# return completely amassed subnetwork list	

### Operate I ###
###  Initial  ###

### Logistics ###
timeHolder = 0
eventTime = 0
startTime = t.time()
eventCount = 0
with open("%s/log_input/batch_log.json"%(path())) as existingData:
	for event in existingData:
		event = ast.literal_eval(event)
		if "timestamp" in event:
			eventTime = d.datetime.strptime(event['timestamp'],'%Y-%m-%d %H:%M:%S').strftime('%s')
			eventCount = eventCount + 1
		if eventTime >= timeHolder:
			timeHolder = eventTime

		### Processing ###
		if "event_type" in event:

			if event["event_type"] == "purchase":				
				if (event["id"] not in NH.NETWORK) :				
					NH.NETWORK[event["id"]] = {"FL":[],"PH":[],"NPS":["0","0"]}	
				updatePH(event["id"], event["amount"])		# update network with purchase information

			if (event["event_type"] == "befriend")|(event["event_type"] == "unfriend"):
				if (event["id1"] not in NH.NETWORK) :
					NH.NETWORK[event["id1"]] = {"FL":[],"PH":[],"NPS":["0","0"]}
				if (event["id2"] not in NH.NETWORK) :
					NH.NETWORK[event["id2"]] = {"FL":[],"PH":[],"NPS":["0","0"]}
				updateFL(event["id1"], event["id2"], event["event_type"])		# update network with friend change information

		if "event_type" not in event:
			NH.D = ast.literal_eval(event["D"])		#
			NH.T = ast.literal_eval(event["T"])		# define key parameters, D and T, via pre-existing data stream

print "[[ Existing Data Process {Duration: %ds, Frequency: %dHz} ]]"%(t.time()-startTime,float(eventCount)/(t.time()-startTime))

### Operate II ###
###  Ongoing   ###

### Logistics ###
timeHolder = 0
startTime = t.time()
eventCount = 0
stream = get('http://127.0.0.1:50009')		# read from local stream established by s.py
for event in stream:
	event = event.strip("\n")
	if (event != "") :
		event = ast.literal_eval(event)
	if "timestamp" in event:
		eventTime = d.datetime.strptime(event["timestamp"],'%Y-%m-%d %H:%M:%S').strftime('%s')
		eventCount = eventCount + 1
	if eventTime >= timeHolder:
		timeHolder = eventTime

		### Processing ###
		if "event_type" in event:

			if event["event_type"] == "purchase":				
				if (event["id"] not in NH.NETWORK) :				
					NH.NETWORK[event["id"]] = {"FL":[],"PH":[],"NPS":["0","0"]}	
				updatePH(event["id"], event["amount"])		# update network with purchase information

				###
				### calculate anomolous threshold, store statistics
				###
				###		to increase scope of measurement, until an array size of T is reached,
				###		most recent unaccumulated purchase of each node in a given node's net-
				###		work is accumulated in a list with which statistics are generated
				###
				subNetworkPurchaseHistory = []
				item = 0
				while (item < NH.T) & (len(subNetworkPurchaseHistory) < NH.T) :
					for node in subNetworkList([event["id"]],0):
						if (item <= (len(NH.NETWORK[node]["PH"])-1)):
								subNetworkPurchaseHistory.append(ast.literal_eval(NH.NETWORK[node]["PH"][len(NH.NETWORK[node]["PH"])-(1+item)]))	# append last (most recent) item 
					item = item + 1
				NH.reset()
				if (len(subNetworkPurchaseHistory) > 0) :
					mean_ = mean(subNetworkPurchaseHistory)
					sigma_ = sigma(subNetworkPurchaseHistory)
					anomalyThreshold = mean_ + 3*sigma_
					mean_ = round(mean_, 2)
					sigma_ = round(sigma_, 2)
					NH.NETWORK[event["id"]]["NPS"][0] = str(mean_)		#
					NH.NETWORK[event["id"]]["NPS"][1] = str(sigma_)		# store statistics

				###
				### log if anomalous
				###
				if (len(subNetworkPurchaseHistory) > 0) :
					if (ast.literal_eval(event["amount"]) >= anomalyThreshold) & (len(subNetworkPurchaseHistory) > 1) :
						print "[[ ANOMALY DETECTED ]]"
						et = "\"event_type\":\"%s\""%(event["event_type"])
						ts = "\"timestamp\":\"%s\""%(event["timestamp"])
						id_ = "\"id\":\"%s\""%(event["id"])
						am = "\"amount\":\"%s\""%(event["amount"])
						me = "\"mean\":\"%.2f\""%(mean_)
						sd = "\"sd\":\"%s\""%(sigma_)
						flaggedEvent = "{" + et + ", " + ts + ", " + id_ + ", " + am + ", " + me + ", " + sd + "}"
						flagger = open("%s/log_output/flagged_purchases.json"%(path()),"a")
						flagger.write(str(flaggedEvent))
						flagger.write("\n")

			if (event["event_type"] == "befriend") | (event["event_type"] == "unfriend"):
				if (event["id1"] not in NH.NETWORK) :
					NH.NETWORK[event["id1"]] = {"FL":[],"PH":[],"NPS":["0","0"]}
				if (event["id2"] not in NH.NETWORK) :
					NH.NETWORK[event["id2"]] = {"FL":[],"PH":[],"NPS":["0","0"]}
				updateFL(event["id1"], event["id2"], event["event_type"])		# update network with friend change information

print "[[ Streamed Data Process {Duration: %ds, Frequency: %dHz} ]]"%(t.time()-startTime,float(1000)/(t.time()-startTime))
if (len(subNetworkPurchaseHistory) > 0) :
	flagger.close()
