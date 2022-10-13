########## INIT ####################################################################################

from ctypes import * # In order to calc forces & torques , must cast unsigned --to-> signed
# ~~ Special ~~
import numpy as np
from time import sleep 
import serial # pySerial for USB comms w/ Arduino
from serial.tools import list_ports
import struct # for data composition over serial



########## CONNECTION TEST #########################################################################

# List all the ports that pyserial can detect , Results are dependent on operating system
ports = list_ports.comports()
for port in ports:
    print( port.device , '\t' , port.manufacturer , '\t' , port.description ) 
    
    
# Attempt to connect to each of USB port until one succeeds
ser   = None
_BAUD = 115200

for port in ports:
    try:
#        ser = serial.Serial( port, _BAUD ) # This must match the port selected in the Arduino IDE
        ser = serial.Serial( str( port.device ), _BAUD ) # This must match the port selected in the Arduino IDE
        print( "Connected to port:" , ser.name  ) 
        break
    except Exception as ex:
        print( "ERROR: COULD NOT ESTABLISH SERIAL CONNECTION WITH", port, ", Check that the port is correct ..." ) 
        print( ex ) 

if ser is None:
    raise Warning( "attempt_connection: Unable to connect to any of " + str([str( p ) for p in ports]) ) 
