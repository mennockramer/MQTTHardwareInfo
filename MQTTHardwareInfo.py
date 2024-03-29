import time
import paho.mqtt.client
import socket
import datetime
import clr
import os

def on_message(client, userdata, message):
    print("Message: " ,str(message.payload.decode("utf-8")))
    print("Topic  : ",message.topic)
    print("QoS    : ",message.qos)
    print("Retain : ",message.retain)

clr.AddReference(os.path.dirname(__file__)+"\LibreHardwareMonitorLib.dll")
from LibreHardwareMonitor import Hardware
computer = Hardware.Computer()
computer.IsMotherboardEnabled=True
computer.IsCpuEnabled=True
computer.IsMemoryEnabled=True
computer.IsGpuEnabled=True
computer.IsStorageEnabled=True
computer.IsNetworkEnabled=True
computer.Open()

#yes these are hardcoded 
hardwareTypes = [ 
  "Motherboard",
  "SuperIO",
  "Cpu",
  "Memory",
  "GpuNvidia",
  "GpuAmd",
  "GpuIntel",
  "Storage",
  "Network",
  "Cooler",
  "EmbeddedController",
  "Psu",
  "Battery"
  ]

sensorTypes = [
  "Voltage", # V
  "Current", # A
  "Power", # W
  "Clock", # MHz
  "Temperature", # °C
  "Load", # %
  "Frequency", # Hz
  "Fan", # RPM
  "Flow", # L/h
  "Control", # %
  "Level", # %
  "Factor", # 1
  "Data", # GB = 2^30 Bytes
  "SmallData", # MB = 2^20 Bytes
  "Throughput", # B/s
  "TimeSpan", # Seconds 
  "Energy" # milliwatt-hour (mWh)
  ]

client = paho.mqtt.client.Client(socket.gethostname()+"-MQTTHardwareInfo")
client.username_pw_set(username="user", password="passwd")

client.connect("homeassistant.local")
client.on_message=on_message



while True:
  payload = "{\"MQTTHardwareInfo\":["

  firstHardware = True
  for h in computer.Hardware :
    h.Update()
    #print(h.Name)
    #print(h.HardwareType)
    #print(hardwareTypes[h.HardwareType])
    if firstHardware == True or payload == "{\"MQTTHardwareInfo\":[" or h.Sensors == [] :
        firstHardware = False
    else :
        payload = payload + ","

    
    
    firstSensor =True
    for s in h.Sensors : 
      if firstSensor == True :
        firstSensor = False
      else :
        payload = payload + ","

      
      #print("Name:  "+ s.Name)
      #print("Type:  "+ str(s.SensorType))
      #print("Type:  "+ sensorTypes[s.SensorType])
      #print("Value: "+ str(s.Value))
      payload = payload + "{\"Name\":\""+s.Name+"\","+ "\"SensorType\":\""+sensorTypes[s.SensorType]+"\", \"Value\":\""+str(s.Value)+"\"}"
      
    firstSubHardware =True
    for sub in h.SubHardware :
      sub.Update()
      #print(sub.Name)
         

      firstSubSensor =True
      for ss in sub.Sensors :
        #print("Name:  "+ ss.Name)
        #print("Type:  "+ str(ss.SensorType))
        #print("Type:  "+ sensorTypes[ss.SensorType])
        #print("Value: "+ str(ss.Value))
        if firstSubSensor == True :
          firstSubSensor = False
        else :
          payload = payload + ","

        payload = payload + "{\"Name\":\""+ss.Name+"\","+ "\"SensorType\":\""+sensorTypes[ss.SensorType]+"\", \"Value\":\""+str(ss.Value)+"\"}"
      
  #removes mysterious trailing comma
  if payload[-1] == ",":
    payload = payload[:-1]

    

  payload = payload + "]}"

  #print(payload)

  #print(socket.gethostname())
  

  client.loop_start()
  client.subscribe("MQTTHardwareInfo")
  client.publish("MQTTHardwareInfo",payload)
  time.sleep(4)
  client.loop_stop()

