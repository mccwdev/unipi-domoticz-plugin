UNIPI plugin for Domoticz home automation

Original plugin author "Ubee"
Further development "GaryG"

Currently supported HW:
  - Neuron 1.1
  - Neuron S103
  
  
  

Right now the python plugin support is only supported by the beta version of Domoticz. Install the latest stable release, and
then you can easily upgrade to latest beta by running the updatebeta script in the domoticz folder. The plugin system also requires python3 on your Rasp.
You also need to install the EVOK software before adding this module. Make sure EVOK runs OK. You can check with EVOK built in web interface. Note: there is a problem with the EVOK install
script on Raspbian Jessie. EVOK daemon must be started with a /etc/init.d script. The install script tries to use the systemctl command, but this does not work. 
Once the above mentioned prerequisites are in place, you are ready to install this module. Put this file, plugin.py,  in the following folder and restart the Rasp:

 domoticz/plugins/UniPIx

Note 0: The file must be named plugin.py and stored in the above mentioned directory. And the directory must be named UniPIx. Beware of the naming. It is case sensitive, and no other file must
be stored in the UniPIx directory.
Then you are ready to add a UniPi module on the Setup page and the HW tab. Choose "UniPI" in the drop-down list, specify a name of the unit, and the port number used for EVOK. This number must match
the one specified in the evok.conf file. You may also choose "Debug" mode, which will give a few more printouts in the domoticz log file if you have specified such one.  Then click "Add". As soon as 
you have done this, 8 switches controlling the relays have been added to Domoticz. Temperature devices will show up with a few minutes after the have been connected. The temperatures are read every 
60s, and every 3rd minute the system looks for new sensors. If a sensor is lost or disconnected, they will still be visible in Domoticz. You will notice they have disappeared by latest update time. 

NOTE 1: Don't delete temp devices that are not longer connected to the system. This will lead to a program crash! If you want to get rid of unused (unavailable) temp sensors, you can disable
the corresponding device on the Device tab on the Setup page. If you reboot the system, all unavailable temp sensors will disappear.

NOTE 2: Currently the Domoticz plugin system have a problem with the Chrome browser. Occasionally, it is not possible to add new HW units supported by plugin modules. You recognize this problem
by finding the name of the HW type at the end of the drop-down list you use to select the HW type you want to add. If you choose that option anyway, you cannot specify any HW parameters and you will 
just load an "empty" module that doesn't work. This problems seems to be correlated with the Chrome browser. Firefox, IE and Edge work fine.
