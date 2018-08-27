# UniPI plugin
#
# Author: Ubee
#
#   This file will provide native support for UniPi in Domoticz. Right now the python plugin support is only supported by the beta version of Domoticz. Install the latest stable release, and
#   then you can easily upgrade to latest beta by running the updatebeta script in the domoticz folder. The plugin system also requires python3 on your Rasp.
#
#   You also need to install the EVOK software before adding this module. Make sure EVOK runs OK. You can check with EVOK built in web interface. Note: there is a problem with the EVOK install
#   script on Raspbian Jessie. EVOK daemon must be started with a /etc/init.d script. The install script tries to use the systemctl command, but this does not work. 
#
#   Once the above mentioned prerequisites are in place, you are ready to install this module. Put this file, plugin.py,  in the following folder and restart the Rasp:
#  
#   domoticz/plugins/UniPIx
#
#   Note 0: The file must be named plugin.py and stored in the above mentioned directory. And the directory must be named UniPIx. Beware of the naming. It is case sensitive, and no other file must
#   be stored in the UniPIx directory.
#
#   Then you are ready to add a UniPi module on the Setup page and the HW tab. Choose "UniPI" in the drop-down list, specify a name of the unit, and the port number used for EVOK. This number must match
#   the one specified in the evok.conf file. You may also choose "Debug" mode, which will give a few more printouts in the domoticz log file if you have specified such one.  Then click "Add". As soon as 
#   you have done this, 8 switches controlling the relays have been added to Domoticz. Temperature devices will show up with a few minutes after the have been connected. The temperatures are read every 
#   60s, and every 3rd minute the system looks for new sensors. If a sensor is lost or disconnected, they will still be visible in Domoticz. You will notice they have disappeared by latest update time. 
#
#   NOTE 1: Don't delete temp devices that are not longer connected to the system. This will lead to a program crash! If you want to get rid of unused (unavailable) temp sensors, you can disable
#   the corresponding device on the Device tab on the Setup page. If you reboot the system, all unavailable temp sensors will disappear.
#
#   NOTE 2: Currently the Domoticz plugin system have a problem with the Chrome browser. Occasionally, it is not possible to add new HW units supported by plugin modules. You recognize this problem
#   by finding the name of the HW type at the end of the drop-down list you use to select the HW type you want to add. If you choose that option anyway, you cannot specify any HW parameters and you will 
#   just load an "empty" module that doesn't work. This problems seems to be correlated with the Chrome browser. Firefox, IE and Edge work fine.
#
#
#
#
"""
<plugin key="UniPIx" name="UniPI" author="ubee" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <params>
    <param field="Port" label="Port" width="30px" required="true" default="8082"/>
    <param field="Mode1" label="Debug" width="75px">
			<options>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal"  default="true" />
			</options>
		</param>
    </params>
</plugin>
"""

import Domoticz,json 

from urllib.request import urlopen
from urllib.parse import urlencode

heartbeatCount=0
HEARTBEAT_DIV=3                     # Every n:th call will trigger temp sensor detection
OneWireIds=list()                   # list of detected 1-wire sensors. First element in list maps to Unit[24] in Domoticz.Device array


UNIPI_URL="localhost:"



def onStart():
#
#   Create all static devices available on UniPi, i.e. 8 relay devices, 12 digital inputs, 2 analog input ports and 1 analog output port.
#
#   Relays are defined as Domoticz Switches - Unit 1..8
#   Ditital Inputs as Domoticz  Switch Contact - Unit 9..20 - Not Implemented 
#   Analog Inputs as Domoticz Voltage - Unit 21,22 - Not implemented
#   Analog Output as Domoticz Voltage - Unit 23 - Not implemented
#
#   1-wire temp sensors are created dynamically when they are connected. They are detected in the onHeartbeat callback function
#   Temp sensors - Unit 24..
#
    global UNIPI_URL
    
  
    Domoticz.Log("onStart called")
    UNIPI_URL=UNIPI_URL+Parameters["Port"]
    if Parameters["Mode1"] == "Debug":
        Domoticz.Debugging(1)
    if (len(Devices) == 0):
        for n in range(1,9):
            Domoticz.Device(Name="Relay "+str(n), Unit=n, TypeName="Switch").Create()
        Domoticz.Log("Relay Devices created.")
#
#   pick up all previolusly detected 1-wire sensors
#
    if len(Devices)>8:      
        response = urlopen("http://"+ UNIPI_URL+"/rest/all").read().decode('utf-8')
        data=json.loads(response)   
        for item in data:
            if item["dev"] == "temp":
                OneWireIds.append(item["circuit"])
    
    DumpConfigToLog()
    Domoticz.Heartbeat(60)
    return True

	

def onStop():
    Domoticz.Log("onStop called")
    return True
 

def onConnect(Status, Description):
    Domoticz.Log("onConnect called")
    return True


def onMessage(Data, Status, Extra):
    Domoticz.Log("onMessage called")
    return True


def onCommand(Unit, Command, Level, Hue):
    
   
    Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    Command = Command.strip()
 #   action, sep, params = Command.partition(' ')
 #   action = action.capitalize()
	

#
#   8 first units are relays that can be toggled
#
    if Unit in range(1,9):
        if (Command == 'On'):
            RelaySet(Unit,1)
            UpdateDevice(Unit,1,'On')

        elif (Command == 'Off'):
            RelaySet(Unit,0)
            UpdateDevice(Unit,0,'Off')	
 

    return True

def onNotification(Data):
    Domoticz.Log("onNotification: " + str(Data))
    return True

def onDisconnect():
    Domoticz.Log("onDisconnect called")
    return True

def onHeartbeat():

#
#   Called periodically
#
#   Every n:th call, the 1-wire bus will be scanned for new temp sensors and added 
#
#   For every call read all temp sensors and update accordingly
#
#   Read digital inputs - not implemented yet
#   Read analog inputs - not implemented yet
#
    global heartbeatCount
    global OneWireIds
    
    Domoticz.Log("onHeartbeat called") 
    response = urlopen("http://"+ UNIPI_URL+"/rest/all").read().decode('utf-8')
    data=json.loads(response)

    if heartbeatCount == 0:
        Domoticz.Log("Scan for new temp sensors")
#
#   For each found temp sensor, check if Domoticz device is defined for this sensor. If not, create the device.
#
        for item in data:
            if item["dev"] == "temp":
                checkAppend(item["circuit"])
            
#
#   Check all defined Domoticz temp devices. If any of those is not available, delete device the device if last update of the device is more than one hour ago.
#      - Not implemented. Maybe is not an good idea to do this? Better to manually delete removed sensors.
#
#   ----- End of update of sensors
#
#   Update Domoticz temp devices with current reading on every hearbeat
#
    if len(OneWireIds) > 0:
        for n in range(0,len(OneWireIds)):
            if findSensor(OneWireIds[n],data):
                Domoticz.Debug("Update temp from 1-wire sensor #"+ str(n+1) +" "+ OneWireIds[n])
                Devices[24+n].Update(nValue=int(findSensor(OneWireIds[n],data)),sValue=str(findSensor(OneWireIds[n],data)))
        
    heartbeatCount=heartbeatCount+1
    if heartbeatCount==HEARTBEAT_DIV:
        heartbeatCount=0
   
   
    return True

 # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    for item in OneWireIds:
        Domoticz.Debug("1-wire sensor "+ item)
    return
	
def UpdateDevice(Unit, nValue, sValue):
 
# Make sure that the Domoticz device still exists (they can be deleted) before updating it
    Domoticz.Debug("Update unit no: "+str(Unit)+" value: "+ str(nValue)+" "+ str(sValue))
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return


#   
#   Control the relay indexed by Unit.
#       nValue = 0  Relay off
#       nValue = 1  Relay on
#    
def RelaySet(Unit,nValue):
    Domoticz.Debug("Relay no: "+str(Unit)+" value: "+ str(nValue))
    response = urlopen("http://"+ UNIPI_URL+"/rest/relay/"+str(Unit),bytes(urlencode({'value': str(nValue)}),'utf-8')).read()
    return



def findSensor(strId,data):

    for item in data:
        if item["dev"] == "temp":
            if item["circuit"]==strId and not item["lost"]:
                return item["value"]
    return False

def checkAppend(sensorId):
#
#   Scan through all temp devices (index 24 and upward, number of devices given by len(OneWireIds). 
#   If sensor is not found, create a new temp device. Store sensorId in options field
#    

    global OneWireIds
    
    for n in range(0,len(OneWireIds)):
        if OneWireIds[n] == sensorId:
            return
       
    OneWireIds.append(sensorId)
    Domoticz.Device(Name="1-wire sensor #"+str(len(OneWireIds)), Unit=24+len(OneWireIds)-1, TypeName="Temperature", Options=sensorId).Create()
    Domoticz.Log("New 1-wire temp sensor found and added, id "+str(sensorId))
     
    return