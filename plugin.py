# Midea Dehumidifier plugin
#
# Author: meaninglessvanity
#
"""
<plugin key="MideaDehum" name="Midea Dehumidifier" author="meaninglessvanity" version="0.0.1"
        wikilink="http://www.domoticz.com/wiki/plugins/plugin.html">
    <description>
        <h2>Midea Dehumidifier</h2><br/>
        Configuration options...
        <ul style="list-style-type:square">
           <li>Email - Your MSmartHome email</li>
           <li>Password - Your MSmartHome password</li>
           <li>Device IP - Your dehumidifier's IP Address</li>
        </ul> 
    </description>
    <params>
        <param field="Mode1" label="Email" required=true width="200px"/>
        <param field="Mode2" label="Password" required=true width="150px"/>
        <param field="Mode3" label="Device IP" required=true width="100px"/>
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""
import traceback
import midea_beautiful
from midea_beautiful import connect_to_cloud, appliance_state, DEFAULT_APPKEY, DEFAULT_HMACKEY, DEFAULT_IOTKEY

with open('/var/log/domoimport.txt', 'a') as f:
   f.write("starting midea plugin\n")
try: 
    import Domoticz
    import subprocess
except Exception as err:
    tbstr = traceback.format_exc()
    with open('/var/log/domoimport.txt', 'a') as f:
       f.write(tbstr)
       f.write("\n")
    exit(1);
    
class MideaPlugin:
    enabled = True
    humUnit = 1
    tempUnit= 2
    runUnit = 3
    fanUnit = 4
    pumpUnit= 5
    defrostUnit=6
    onlineUnit=7
    targetUnit=8
    tankUnit=9
    ionUnit=10
    sleepUnit=11
    filterUnit=12
    tankLevelUnit=13

    def __init__(self):
       
        self.cloudLoads = 0;
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        for key in Parameters:
           mystr = "param: " + str(key) + '->' + str(Parameters[key])
           Domoticz.Debug(mystr)

        Domoticz.Heartbeat(300);

        Domoticz.Device(Name="Relative Humidity", Unit=self.humUnit, Type=243,Subtype=6, Used=1).Create()
        Domoticz.Device(Name="Temperature", Unit=self.tempUnit, Type=80, Used=1).Create()
        Domoticz.Device(Name="Running", Unit=self.runUnit, Type=244, Subtype=73, Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Fan", Unit=self.fanUnit, Type=243,Subtype=6, Used=1).Create()
        Domoticz.Device(Name="Pump", Unit=self.pumpUnit, Type=244,Subtype=73,Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Defrost", Unit=self.defrostUnit, Type=244,Subtype=73,Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Online", Unit=self.onlineUnit, Type=244, Subtype=73, Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Humidity Target", Unit=self.targetUnit, Type=243,Subtype=6, Used=1).Create()
        Domoticz.Device(Name="Tank Level", Unit=self.tankLevelUnit, Type=243,Subtype=6, Used=1).Create()
        Domoticz.Device(Name="Tank Full", Unit=self.tankUnit, Type=244, Subtype=73, Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Ion Mode", Unit=self.ionUnit, Type=244, Subtype=73, Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Sleep Mode", Unit=self.sleepUnit, Type=244, Subtype=73, Switchtype=0, Used=1).Create()
        Domoticz.Device(Name="Filter Indicator", Unit=self.filterUnit, Type=244, Subtype=73, Switchtype=0, Used=1).Create()
 
        # if (not "Dimmer" in Devices):
        #    Domoticz.Unit(Name="Dimmer", Unit=2, TypeName="Dimmer", DeviceID="Dimmer").Create()

    def onStop(self):
        Domoticz.Log("onStop called")
        Domoticz.Debugging(0);
        Domoticz.Heartbeat(0);

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, DeviceID, Unit, Command, Level, Color):
        Domoticz.Log("onCommand called for Device " + str(DeviceID) + " Unit " + str(Unit) + ": Parameter '" + str(
            Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")


    def getCloud(self):
       try:
          myCloud = connect_to_cloud(account=Parameters["Mode1"], password=Parameters["Mode2"], appname="MSmartHome", appid=DEFAULT_APPKEY, hmackey=DEFAULT_HMACKEY, iotkey=DEFAULT_IOTKEY)
          if (myCloud is None):
             Domoticz.Debug("We've tried to load the cloud "+self.cloudLoads+" times.")
             return None
          return myCloud
       except Exception as err:
          Domoticz.Debug("cloud connect error: "+traceback.format_exc())
          return None


_plugin = MideaPlugin()
_cloud = None
 
def onStart():
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(DeviceID, Unit, Command, Level, Color)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin,_cloud

    try: 
       appliance = getDataDirect()
       myState = appliance.state
       if (myState is not None and myState.current_temperature > 0):
          setValue(MideaPlugin.tempUnit,myState.current_temperature)
          setValue(MideaPlugin.humUnit,myState.current_humidity)
          setValue(MideaPlugin.runUnit,myState.running)
          setValue(MideaPlugin.fanUnit,myState.fan_speed)
          setValue(MideaPlugin.pumpUnit,myState.pump)
          setValue(MideaPlugin.defrostUnit,myState.defrosting)
          setValue(MideaPlugin.onlineUnit,appliance.online)
          setValue(MideaPlugin.targetUnit,myState.target_humidity)
          setValue(MideaPlugin.tankLevelUnit,myState.tank_level)
          setValue(MideaPlugin.tankUnit,myState.tank_full)
          setValue(MideaPlugin.ionUnit,myState.ion_mode)
          setValue(MideaPlugin.sleepUnit,myState.sleep_mode)
          setValue(MideaPlugin.filterUnit,myState.filter_indicator)
    except Exception as err:
       Domoticz.Debug("could not get midea data: "+traceback.format_exc());
       return;

def getDataDirect():
    global _cloud,_plugin
    if (_cloud is None):
       _cloud = _plugin.getCloud()
    try:
       myState = appliance_state(address=Parameters["Mode3"], cloud=_cloud)
    except Exception as err:
       Domoticz.Debug("midea state error: "+traceback.format_exc())
       return None
    return myState

def setValue(Unit,Value):
   if Value == "True": 
      sValue = "true"
      nValue = 1
   elif Value == "False":
      sValue = "false"
      nValue = 0
   else :
      Domoticz.Debug("calling setValue: "+str(round(float(Value))))
      sValue = str(round(float(Value)))
      nValue = round(float(Value))

   Devices[Unit].Update(nValue=nValue,sValue=sValue)
        
