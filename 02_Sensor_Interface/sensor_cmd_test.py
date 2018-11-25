#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "sensor_cmd_test.py"
__version__  = "2018.11"
__desc__     = "A_ONE_LINE_DESCRIPTION_OF_THE_FILE"
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 2.7

Dependencies: numpy
"""


"""  
~~~ Developmnent Plan ~~~
[ ] ITEM1
[ ] ITEM2
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
# ~~ Special ~~
import numpy as np
from time import sleep 
import serial # pySerial for USB comms w/ Arduino
import struct # for data composition over serial
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# == Serial Functions ==

# = Connection Functions =

def attempt_connection( COMlist , speed ):
    """ Attempt to connect to each of 'COMlist' until one succeeds """
    ser = None
    for port in COMlist:
        try:
            ser = serial.Serial( port , speed ) # This must match the port selected in the Arduino IDE
            print "Connected to port:" , port 
            return ser
        except Exception as ex:
            print "ERROR: COULD NOT ESTABLISH SERIAL CONNECTION WITH" , port , ", Check that the port is correct ..."
            print ex
    raise Warning( "attempt_connection: Unable to connect to any of " + str( COMlist ) ) # If we made it to here , we attempted all the ports

# _ End Connection _


# = Command Functions = 

CMDMAX = 250
SOP    =  85 # Start of Packet , Robotous Manual - pg 9
EOP    = 170 # End of Packet   , Robotous Manual - pg 9

def constrain_cmd( number ):
    """ Constrain the command parameter to an integer within [ 0 , CMDMAX ] , inclusive """
    number = int( number )
    if number < 0: number = 0
    elif number > CMDMAX: number = CMDMAX
    return number

def one_byte_checksum( *byteWords ):
    """ Return the checksum as given by page 10 of the robotous manual """
    return sum( byteWords ) % 256 # FIXME : IS THIS CORRECT?

def package_data_for_SEND( data ):
    """ Return a list of numbers that ma """
    if len( data ) != 8:
        raise IndexError( "SEND data must comprise 8 bytes!" )
    rtnByteList = [ SOP ]
    for datum in data:
        rtnByteList.append( constrain_cmd( datum ) )
    rtnByteList.append( one_byte_checksum( *data ) )
    rtnByteList.append( EOP )
    return rtnByteList

# ~ Send ~

def SEND_read_model_name( connection ):
    """ Request the model name of the device """
    data = [ 1 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ]
    send = package_data_for_SEND( data )
    print "Sending:" , send 
    connection.write( struct.pack( 'BBBBBBBBBBB' , *send ) )

def SEND_set_baud_rate( connection ):
    """ Set the baud rate """
    
# ~ Receive ~

def get_all_bytes_from_connection( connection ):
    readResult = connection.read( connection.inWaiting() )
    print readResult
    splitReslt = [ elem for elem in readResult.splitlines() ]    
    print splitReslt

# _ End Command _


# = Program Vars =

#COMLIST = [ '/dev/ttyUSB0' , '/dev/ttyS0' ]
COMLIST = [ '/dev/ttyUSB1' , '/dev/ttyUSB0' ]

#TSTLIST = [ '/dev/ttyS0'   , '/dev/ttyUSB0' ]
TSTLIST = [ '/dev/ttyUSB0' , '/dev/ttyS0'   ]

# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    #print "Connecting to the serial port ..."
    ser = attempt_connection( COMLIST , 115200 ) # Speed must match the port selected in the Arduino IDE
    
    print "Starting the test connections ..."
    tst = attempt_connection( TSTLIST , 115200 ) # Speed must match the port selected in the Arduino IDE
    
    print "Request model name ..."
    #SEND_read_model_name( ser )
    #SEND_read_model_name( tst )
    
    sleep( 5 )
    
    print "What came back?"
    if 1:
        print "Serial has" , ser.inWaiting() , "bytes in waiting"
        print "Bytes from serial connection:"
        get_all_bytes_from_connection( ser )
        
        print "Test has" , tst.inWaiting() , "bytes in waiting"
        print "Bytes from test connection:"
        get_all_bytes_from_connection( tst )
    else:
        if 0:
            get_all_bytes_from_connection( ser )
        else:
            get_all_bytes_from_connection( tst )
    
    print "Closing port ..."
    #ser.close()
    tst.close()
    
    print "Exit."

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________