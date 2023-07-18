# midea_dehum_plugin
A plugin for Domoticz to automate a Midea Dehumidifier

## Limitations
- For now, this only works if you have an account with MSmartHome.  This could be expanded to use other methods if there is call for it.
- There is currently no editing support.

To install:

```
sudo pip3 install midea-beautiful
cd <DOMOTICZ_HOME>/plugins   
git clone https://github.com/meaninglessvanity/midea_dehum_plugin.git
sudo systemctl restart domoticz
```

To use:

Create a new Midea Dehumidifier hardware item and provide the necessary info!

You will get devices for various aspects of the dehumidifier.
