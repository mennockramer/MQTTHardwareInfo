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



clr.AddReference(os.path.dirname(__file__)+"\OpenHardwareMonitorLib.dll")
from OpenHardwareMonitor import Hardware
computer = Hardware.Computer()
computer.MainboardEnabled=True
computer.CPUEnabled=True
computer.RAMEnabled=True
computer.GPUEnabled=True
computer.HDDEnabled=True
computer.Open()

hardwareTypes = [ 
  'Mainboard', 'SuperIO', 'CPU', 'RAM', 'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'HDD' 
]

sensorTypes = [
 'Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level', 'Factor', 'Power', 'Data', 'SmallData'
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
    print(h.Name)

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

      
      payload = payload + "{\"Name\":\""+s.Name+"\","+ "\"SensorType\":\""+sensorTypes[s.SensorType]+"\", \"Value\":\""+str(s.Value)+"\"}"
      
    firstSubHardware =True
    for sub in h.SubHardware :
      sub.Update()
      #print(sub.Name)

      

      

      firstSubSensor =True
      for ss in sub.Sensors :
        #print(ss.Name + " " + sensorTypes[ss.SensorType]+ " " +str(ss.Value) )
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

