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
from serial.tools import list_ports
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
            print "Connected to port:" , ser.name 
            return ser
        except Exception as ex:
            print "ERROR: COULD NOT ESTABLISH SERIAL CONNECTION WITH" , port , ", Check that the port is correct ..."
            print ex
    raise Warning( "attempt_connection: Unable to connect to any of " + str( COMlist ) ) # If we made it to here , we attempted all the ports

def list_available_ports():
    """ List all the ports that pyserial can detect , Results are dependent on operating system """
    ports = list_ports.comports()
    for port in ports:
        print port.device , '\t' , port.manufacturer , '\t' , port.description
    return [ port.device for port in ports  ]

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
    msg  = bytearray( package_data_for_SEND( data ) )
    for i in xrange(5):
        connection.write( msg )
        sleep( 0.01 )
    print "Sent" , list( msg )

def SEND_test_bytes( connection ):
    """ Send a known  sequence of bytes """
    data = bytearray([  SOP ,  50 , 100 , EOP ])
    for i in xrange(5):
        connection.write( data )
        sleep( 0.01 )
    print "Sent" , list( data )
    #connection.write( struct.pack( 'BBBB' , *data ) )
    
# ~ Receive ~

def get_all_bytes_from_connection( connection ):
    if connection.in_waiting:
        readResult = connection.read( connection.in_waiting )
        rtnNums    = [ ord( elem ) for elem in list( readResult ) ]
        print rtnNums
        return rtnNums
    else:
        print "No bytes to read!"
        return []
    
def get_messages_from_mass_bytes( intsList , bgnInt , endInt , msgLen ):
    """ Find all the messages in 'intsList' that begin with 'bgnInt' , end with 'endInt' , and are 'msgLen' long """
    i = 0
    streamLen = len( intsList )
    rtnMsgs  = []
    currByte = 0
    currMsg  = []
    reading  = False
    while( i < streamLen ):
        currByte = intsList[i]
        if currByte == bgnInt:
            reading = True
            currMsg = [ bgnInt ]
        elif reading:
            currMsg.append( currByte )
            if len( currMsg ) > msgLen:
                reading = False
                currMsg = []
            elif currByte == endInt:
                rtnMsgs.append( currMsg )
                currMsg = []
                reading = False
        i += 1
    return rtnMsgs
            

# _ End Command _


# = Program Vars =

#COMLIST = [ '/dev/ttyUSB0' , '/dev/ttyS0' ]
#COMLIST = [ '/dev/ttyUSB1' , '/dev/ttyUSB0' ]
COMLIST = [ '/dev/ttyUSB0' ]

#TSTLIST = [ '/dev/ttyS0'   , '/dev/ttyUSB0' ]
#TSTLIST = [ '/dev/ttyUSB0' , '/dev/ttyS0'   ]
TSTLIST = [ '/dev/ttyUSB1' ]

COMMPORTEN = True
TESTPORTEN = True

# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    ser = None
    tst = None
    
    print "Available Ports" , list_available_ports()
    
    if COMMPORTEN:
        #print "Connecting to the serial port ..."
        ser = attempt_connection( COMLIST , 115200 ) # Speed must match the port selected in the Arduino IDE

    if TESTPORTEN:    
        print "Starting the test connections ..."
        tst = attempt_connection( TSTLIST , 115200 ) # Speed must match the port selected in the Arduino IDE

    # Send formatted messages and listen for data back on the test port
    if 1:
        
        # 1. Send test bytes
        for i in xrange( 32 ):
            SEND_read_model_name( ser )
            sleep(0.001)
        
        sleep( 2 )
        
        # 2. Interpret messages
        for i in xrange( 16 ):
            stream = get_all_bytes_from_connection( tst )
            if len( stream ):
                msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 1 + 16 + 1 + 1 )
                print '\t' , len( msgs ) , "messages in" , len( stream ) , "bytes"
            sleep(0.5)           

    # Send formatted messages and listen for any data back
    if 0:
        
        # 1. Send test bytes
        for i in xrange( 32 ):
            SEND_read_model_name( ser )
            sleep(0.001)
        
        sleep( 2 )
        
        # 2. Interpret messages
        for i in xrange( 16 ):
            stream = get_all_bytes_from_connection( ser )
            if len( stream ):
                msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 1 + 16 + 1 + 1 )
                print '\t' , len( msgs ) , "messages in" , len( stream ) , "bytes"
            sleep(0.5)        
    
    # Send test messages and listen for any data back
    if 0:
        
        # 1. Send test bytes
        for i in xrange( 16 ):
            SEND_test_bytes( ser )
            sleep(0.01)
        
        # 2. Interpret messages
        for i in xrange(  8 ):
            stream = get_all_bytes_from_connection( ser )
            if len( stream ):
                msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 4 )
                print '\t' , len( msgs ) , "messages in" , len( stream ) , "bytes"
            sleep(0.5)
    
    
    
    #print "Request model name ..."
    ##SEND_read_model_name( ser )
    ##SEND_read_model_name( tst )
    
    #sleep( 5 )
    
    #print "What came back?"
    #if 1:
        #print "Serial has" , ser.inWaiting() , "bytes in waiting"
        #print "Bytes from serial connection:"
        #get_all_bytes_from_connection( ser )
        
        #print "Test has" , tst.inWaiting() , "bytes in waiting"
        #print "Bytes from test connection:"
        #get_all_bytes_from_connection( tst )
    #else:
        #if 0:
            #get_all_bytes_from_connection( ser )
        #else:
            #get_all_bytes_from_connection( tst )
    
    print "Closing port(s) ..."
    if COMMPORTEN:
        ser.close()
    if TESTPORTEN:
        tst.close()
    
    print "Exit."

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
