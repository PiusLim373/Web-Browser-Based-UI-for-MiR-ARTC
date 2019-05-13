from flask import Flask, render_template, request, jsonify, json, Response
import requests
import time
import threading
import logging

app = Flask(__name__)
debug_mode = False 					#SET THIS TO TRUE FOR DEBUG MODE
status = {}
mission = {}
mission_queue = {}
mission_queue_count = 0
ServerIP = "0.0.0.0"		#Mini PC's IP address, for external device to access the flask server within, **external device need to connect to the same wifi as the Mini PC

if (debug_mode == True):
	MirAddr = "http://localhost:3000"
	headers={}

else:
	MirAddr = "http://192.168.12.214/api/v2.0.0"		#API address of AGV, should be: http://mir.com/api/v2.0.0 or http://192.168.12.214/api/v2.0.0
	headers = {'accept':'application/json', 'authorization': 'Basic YWRtaW46OGM2OTc2ZTViNTQxMDQxNWJkZTkwOGJkNGRlZTE1ZGZiMTY3YTljODczZmM0YmI4YTgxZjZmMmFiNDQ4YTkxOA==', 'Accept-Languege':'en_US','Content-Type': 'application/json'}

MirMissionQAddr = MirAddr + "/mission_queue/"
MirMissionAddr = MirAddr + "/missions/"
MIRStatusAddr = MirAddr + "/status/"

r = requests.get(MirMissionAddr, data = {'key':'value'}, headers=headers)		#Obtain the existing mission list in MIR
mission = json.loads(r.content)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/agv_info')
def agv_info():
	return render_template("agv_info.html")

@app.route('/ur_controller')
def ur_controller():
	return render_template("ur_controller.html")

@app.route('/CheckInit', methods = ['GET'])			#Check the status of MIR when webpage starts
def CheckInit():		
	r = requests.get(MIRStatusAddr, data = {'key':'value'}, headers = headers)
	state_id = json.loads(r.content)
	return str(state_id['state_id'])

@app.route('/MissionList', methods=['GET'])			#Return the whole mission list to webpage
def MissionName():
	global mission
	return jsonify(mission)

@app.route('/SendMission', methods=['POST'])		#Send selected mission to MIR
def SendMission():
	req_data = request.get_json()
	print(req_data)
	mission_id = req_data['mission_id']
	print(mission_id)
	r = requests.post(MirMissionQAddr, json = {'mission_id': mission_id}, headers = headers)
	return 'received'

@app.route('/DeleteMission', methods=['POST'])		#Send selected mission to MIR
def DeleteMission():
	req_data = request.get_json()
	print(req_data)
	mission_id = req_data['mission_id']
	print(mission_id)
	url = MirMissionQAddr + str(mission_id)
	r = requests.delete(url, headers = headers)
	print(url)
	return 'deleted'

@app.route('/statusSSE')							#Server-sent Event (SSE)* for realtime MIR status  
def statusSSE():									#*SSE will only send data to front-end when it detects there is changes in variable, prevent polling
	def gen1():
		global status
		while True:
			time.sleep(0.5)
			r = requests.get(MIRStatusAddr, data = {'key':'value'}, headers = headers)
			status_temp = json.loads(r.content)
			if status != status_temp:
				status = status_temp
				yield 'data:{ "battery_percentage":' + str(status['battery_percentage']) +',"battery_time_remaining":'+ str(status['battery_time_remaining'])+ ',"position_x":' + str(status['position']['x']) + ',"position_y":' + str(status['position']['y']) + ',"velocity_linear":' + str(status['velocity']['linear']) + ',"velocity_angular":' + str(status['velocity']['angular']) + ',"distance_to_next_target":' + str(status['distance_to_next_target']) + ',"state_id":' + str(status['state_id']) +  ',"state_text":"' + str(status['state_text']) +'"}\n\n'
	return Response(gen1(), mimetype='text/event-stream')

@app.route('/MissionQSSE')							#Server-sent Event (SSE) for realtime MIR mission_queue
def MissionQSSE():
	def gen3():
		global mission_queue, mission_queue_count
		while True:
			time.sleep(0.5)
			r = requests.get(MirMissionQAddr, data = {'key':'value'}, headers = headers)
			mission_queue_temp = json.loads(r.content)
			if mission_queue != mission_queue_temp:
				mission_queue = mission_queue_temp
				mission_queue_ID = []
				mission_queue_NAME = []
				i = 0
				while i<len(mission_queue):
					if (mission_queue[i]['state'] == "Pending"):
						mission_queue_ID.append(mission_queue[i]['id'])
						mission_queue_NAME.append(GetMissionName(mission_queue[i]['id']))
					i = i +1
				HTMLData = ""
				CounterData = 0
				data = ""
				j = 0
				while j<len(mission_queue_ID):
					HTMLData = HTMLData + '<tr id="' + str(mission_queue_ID[j]) + '" class="table-light"><th scope="row">' + str(mission_queue_NAME[j]) + '</th><td><span class="badge badge-danger" onclick="DeleteMission(' + str(mission_queue_ID[j]) + ')">Delete</span></td></tr>'
					j = j+1
				CounterData = len(mission_queue_ID)
				mission_queue_count = CounterData
				data = str(CounterData) + ',' + str(HTMLData)
				print(data)
				yield 'data:{}\n\n'.format(data)
	return Response(gen3(), mimetype='text/event-stream')

@app.route('/SSEDoubleCheck', methods=['GET'])
def SSEDoubleCheck():
	global status, mission_queue_count
	jsonData = {'battery_percentage': status['battery_percentage'], 'mission_queue_count': mission_queue_count}
	return jsonify(jsonData)

def GetMissionName(id):
	url = MirMissionQAddr + str(id)
	r = requests.get(url, headers = headers)
	temp = json.loads(r.content)
	url2 = MirMissionAddr + str(temp['mission_id'])
	r2 = requests.get(url2, headers = headers)
	temp2 = json.loads(r2.content)
	return str(temp2['name'])

@app.route('/SSErefresh', methods=['POST'])			#To fix a bug where webpage refresh wont receive data of status and mission queue
def SSErefresh():
	global status, mission_queue
	req_data = request.get_json()
	print(req_data)
	status = req_data
	mission_queue = req_data
	return str(req_data)

@app.route('/MIRRoutine', methods = ['POST'])									#To pause or continue executing mission 
def MIRRoutine():																#UI that controls MIR
	routine = request.form['routine']
	print(routine)
	if routine == "PAUSE":														#Pause MIR without deleting existing mission queue
		requests.put(MIRStatusAddr, json = {'state_id': 4}, headers = headers)
		return "MIR state is changed to PAUSE, all missions stopped temporarily"
	elif routine == "READY":													#Continue execting MIR's mission queue
		requests.put(MIRStatusAddr, json = {'state_id': 3}, headers = headers)
		return "MIR State is changed to READY, executing missions in queue"
	else:
		return "?"	

#///////////////////////////////////////////////////////////////////////////////////////// Script for UR Controller/////////////////////////////////////////////////////////////////////////////////////////#
URMissionJson = {}
OnGoingURMission = False
ProgressBarText = ["", 0]

@app.route('/URMissionHttp', methods = ['GET','POST'])
def URMissionHttp():
	global URMissionJson, OnGoingURMission
	if(request.method == 'GET'):
		if(OnGoingURMission == True):
			print("refreshed")
		return str(OnGoingURMission)

	else:
		URMissionJson = request.get_json()
		print(URMissionJson)
		URMission(URMissionJson)
		return "Mission Completed!"

@app.route('/ProgressBarSSE')							#Server-sent Event (SSE) for Progress Bar
def ProgressBarSSE():
	def gen4():
		global ProgressBarText, URMissionJson
		ProgressBarTexttemp = ""
		i = 0
		for key in URMissionJson['required']:
			i += 2 * URMissionJson['required'][key] + 2
		i += 2
		print(i)
		i_perc = 0
		while True:
			if (ProgressBarTexttemp != ProgressBarText[0]):
				ProgressBarTexttemp = ProgressBarText[0]
				
				data = str(ProgressBarTexttemp) + "_" + str(i_perc)
				i_perc += 100 / i
				yield 'data:{}\n\n'.format(data)
	return Response(gen4(), mimetype='text/event-stream')


def URMission(data):
	global status, URStationList, OnGoingURMission, ProgressBarText
	OnGoingURMission = True
	ProgressBarText = ["", 0]
	arr = []
	for key in data['required'].keys():
		arr.append(key)
	SubMissionCount = len(arr)
	i = 0
	while i < SubMissionCount:
		if(data['required'][arr[i]] == 0):   #Check if there is item needed to pick? 0 means all items has been collected, eg: "Milo":1 means 1 milo is needed 
			i = i+1
		else:
			#make mir go station of submission:
			print("MIR is going to: " + str(arr[i]) + " station")
			ProgressBarText[0] = "MIR is going to " + str(arr[i]) + " station..."
			r = requests.post(MirMissionQAddr, json = {'mission_id': URStationList[arr[i]]}, headers = headers)

			#wait for mir to reach destination
			while (status['state_id'] != 3):
				time.sleep(1)
				pass
			print("MiR has reached " + str(arr[i]) + " station")
			ProgressBarText[0] = "MiR has reached " + str(arr[i]) + " station."
			#send pick mission to ur
			#use: data['required'][arr[i]] to get number of item
			# print("activating ur to pick " + str(data['required'][arr[i]])+ " items")
			#after picking each item, change the number in json, provided that send command to pick only 1 item at a time to UR
			k = data['required'][arr[i]]
			j = 1
			while (j <= k):
				#UR command to pick 1 item below:
				ProgressBarText[0] = "UR is picking 1 " + str(arr[i]) +" ..."
				r = requests.post(MirMissionQAddr, json = {'mission_id': "fc17a978-4b9a-11e9-8c74-94c6911b3ddd"}, headers = headers)
				# time.sleep(5)
				time.sleep(2)
				while (status['state_id'] != 3):
					time.sleep(1)
					pass
				print("Picked 1 " + str(arr[i]))
				ProgressBarText[0] = "Picked 1 " + str(arr[i]) + ", total " + str(arr[i]) + " picked = " + str(j)
				data['required'][arr[i]] = data['required'][arr[i]] - 1
				j = j+1

			# print("pick mission completed, moving to next destination")
			# ProgressBarText[0] = str(arr[i]) + " picking mission completed, moving to next destination."
			i = i+1
	print("MIR is going back to initial location")
	ProgressBarText[0] = "All picking mission finished, routing back to dropoff location..."
	r = requests.post(MirMissionQAddr, json = {'mission_id': "00b31db7-4ae8-11e9-9fce-94c6911b3ddd"}, headers = headers)
	while (status['state_id'] != 3):
		time.sleep(1)
		pass
	print("MIR has successfully completed the UR mission!")
	ProgressBarText[0] = "UR picking mission has completed successfully."
	OnGoingURMission = False
	print(URMissionJson)
	ProgressBarText[0] = "TransmissionsEnded"
	return 0


URStationList = {'Milo':'00b31db7-4ae8-11e9-9fce-94c6911b3ddd','Kokokrunch':'c95c81cc-4b7e-11e9-b2dc-94c6911b3ddd','Nespresso':'nespresso-station_guid','Kitkat':'kitkatstation_guid','Greentea':'greentea-station_guid'}
'''
1. Change the guid for all station in URStationList
2. Create a button to change state from 4 Pause to 3 Ready when ur mission is sent
3. Change the guid for origin
'''


if __name__ == '__main__':
	app.run(host = ServerIP, debug = True)

