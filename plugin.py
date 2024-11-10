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
           <li>Application - Mobile application</li>
        </ul>
    </description>
    <params>
        <param field="Username" label="Email" required="true" width="200px"/>
        <param field="Password" label="Password" required="true" width="150px"/>
        <param field="Address" label="Device IP" required="true" width="100px"/>
        <param field="Mode1" label="Application" required="true" width="130px">
            <options>
                <option label="NetHome Plus" value="NetHome Plus" />
                <option label="Midea Air" value="Midea Air" />
                <option label="Ariston Clima" value="Ariston Clima" />
                <option label="MSmartHome" value="MSmartHome" default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug" />
                <option label="False" value="Normal" default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""

import traceback
from midea_beautiful import (
    connect_to_cloud,
    appliance_state,
)
from midea_beautiful.appliance import DehumidifierAppliance
from midea_beautiful.util import strtobool
from typing import cast

with open("/var/log/domoimport.txt", "a") as f:
    f.write("starting midea plugin\n")
try:
    import Domoticz
except Exception:
    tbstr = traceback.format_exc()
    with open("/var/log/domoimport.txt", "a") as f:
        f.write(tbstr)
        f.write("\n")
    exit(1)


class MideaPlugin:
    enabled = True
    humUnit = 1
    tempUnit = 2
    runUnit = 3
    fanUnit = 4
    pumpUnit = 5
    defrostUnit = 6
    onlineUnit = 7
    targetUnit = 8
    tankUnit = 9
    ionUnit = 10
    sleepUnit = 11
    filterUnit = 12
    tankLevelUnit = 13

    def __init__(self):
        self.cloudLoads = 0
        self.cloud = None
        return

    def onStart(self):
        if Parameters["Mode6"] in ("Debug", "File"):  # noqa: F821
            Domoticz.Debugging(1)

        Domoticz.Debug("onStart called")
        for key in Parameters:  # noqa: F821
            mystr = "param: " + str(key) + "->" + str(Parameters[key])  # noqa: F821
            Domoticz.Debug(mystr)

        self.email = Parameters["Username"]  # noqa: F821
        self.password = Parameters["Password"]  # noqa: F821
        self.address = Parameters["Address"]  # noqa: F821
        self.application = Parameters["Mode1"]  # noqa: F821

        Domoticz.Heartbeat(10)
        Domoticz.Device(
            Name="Relative Humidity", Unit=self.humUnit, Type=243, Subtype=6, Used=1
        ).Create()
        Domoticz.Device(
            Name="Temperature", Unit=self.tempUnit, Type=80, Used=1
        ).Create()
        Domoticz.Device(
            Name="Running",
            Unit=self.runUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()
        Domoticz.Device(
            Name="Fan", Unit=self.fanUnit, Type=243, Subtype=6, Used=1
        ).Create()
        Domoticz.Device(
            Name="Pump", Unit=self.pumpUnit, Type=244, Subtype=73, Switchtype=0, Used=1
        ).Create()
        Domoticz.Device(
            Name="Defrost",
            Unit=self.defrostUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()
        Domoticz.Device(
            Name="Online",
            Unit=self.onlineUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()
        Domoticz.Device(
            Name="Humidity Target", Unit=self.targetUnit, Type=243, Subtype=6, Used=1
        ).Create()
        Domoticz.Device(
            Name="Tank Level", Unit=self.tankLevelUnit, Type=243, Subtype=6, Used=1
        ).Create()
        Domoticz.Device(
            Name="Tank Full",
            Unit=self.tankUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()
        Domoticz.Device(
            Name="Ion Mode",
            Unit=self.ionUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()
        Domoticz.Device(
            Name="Sleep Mode",
            Unit=self.sleepUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()
        Domoticz.Device(
            Name="Filter Indicator",
            Unit=self.filterUnit,
            Type=244,
            Subtype=73,
            Switchtype=0,
            Used=1,
        ).Create()

    def onStop(self):
        Domoticz.Log("onStop called")
        Domoticz.Debugging(0)
        Domoticz.Heartbeat(0)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(
            "onCommand called for Unit "
            + str(Unit)
            + ": Parameter '"
            + str(Command)
            + "', Level: "
            + str(Level)
        )

        try:
            appliance = self.getDataDirect()
        except Exception:
            Domoticz.Error("could not get midea data: " + traceback.format_exc())
            return

        # Start / stop
        if Unit == self.runUnit:
            # Running property is not available on LanDevice, must cast to
            # proper type
            if DehumidifierAppliance.supported(appliance.type):
                dehumidifier = cast(DehumidifierAppliance, appliance.state)
            try:
                dehumidifier.running = Command
                appliance.apply()
                self.setValue(MideaPlugin.runUnit, strtobool(Command))
                Domoticz.Log("set appliance status to {}".format(Command))
            except Exception:
                Domoticz.Error(
                    "could not set appliance status to {}".format(Command)
                    + traceback.format_exc()
                )

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log(
            "Notification: "
            + Name
            + ","
            + Subject
            + ","
            + Text
            + ","
            + Status
            + ","
            + str(Priority)
            + ","
            + Sound
            + ","
            + ImageFile
        )

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

        try:
            appliance = self.getDataDirect()
            myState = appliance.state

            if myState is not None and myState.current_temperature > 0:
                self.setValue(MideaPlugin.tempUnit, myState.current_temperature)
                self.setValue(MideaPlugin.humUnit, myState.current_humidity)
                self.setValue(MideaPlugin.runUnit, myState.running)
                self.setValue(MideaPlugin.fanUnit, myState.fan_speed)
                self.setValue(MideaPlugin.pumpUnit, myState.pump)
                self.setValue(MideaPlugin.defrostUnit, myState.defrosting)
                self.setValue(MideaPlugin.onlineUnit, appliance.online)
                self.setValue(MideaPlugin.targetUnit, myState.target_humidity)
                self.setValue(MideaPlugin.tankLevelUnit, myState.tank_level)
                self.setValue(MideaPlugin.tankUnit, myState.tank_full)
                self.setValue(MideaPlugin.ionUnit, myState.ion_mode)
                self.setValue(MideaPlugin.sleepUnit, myState.sleep_mode)
                self.setValue(MideaPlugin.filterUnit, myState.filter_indicator)
        except Exception:
            Domoticz.Error("could not get midea data: " + traceback.format_exc())
            return

    def getCloud(self):
        try:
            myCloud = connect_to_cloud(
                account=self.email,
                password=self.password,
                appname=self.application,
            )
            if myCloud is None:
                Domoticz.Error(
                    "We've tried to load the cloud " + self.cloudLoads + " times."
                )
                return None
            return myCloud
        except Exception:
            Domoticz.Error("cloud connect error: " + traceback.format_exc())
            return None

    def getDataDirect(self):
        if self.cloud is None:
            self.cloud = self.getCloud()
        try:
            myState = appliance_state(address=self.address, cloud=self.cloud)
        except Exception:
            Domoticz.Error("midea state error: " + traceback.format_exc())
            return None
        return myState

    def setValue(self, Unit, Value):
        if Value == "True":
            sValue = "true"
            nValue = 1
        elif Value == "False":
            sValue = "false"
            nValue = 0
        else:
            Domoticz.Debug(
                "calling setValue: {} for unit: {}".format(
                    str(round(float(Value))), str(Unit)
                )
            )
            sValue = str(round(float(Value)))
            nValue = round(float(Value))

            Devices[Unit].Update(nValue=nValue, sValue=sValue)  # noqa: F821


_plugin = MideaPlugin()
_heartbeat_count = 0


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


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin, _heartbeat_count

    # process every 30 heartbeats
    # 10s heartbeats * 30 = 300s
    if _heartbeat_count % 30 == 0:
        _plugin.onHeartbeat()

    _heartbeat_count = _heartbeat_count + 1
