#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "robotous_comm_serial.py"
__version__  = "2018.11"
__desc__     = "Read and interpret data from the Robotous RFT40-SA01-C Force-Torque Sensor"
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
from ctypes import * # In order to calc forces & torques , must cast unsigned --to-> signed
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

ATTEMPTS = 1
PRINTSND = False

def SEND_CMD( connection , data ):
    """ Send a structure command packet to the sensor """
    msg  = bytearray( package_data_for_SEND( data ) )
    for i in xrange( ATTEMPTS ):
        connection.write( msg )
        sleep( 0.01 )
    if PRINTSND:
        print "Sent" , list( msg )    

def SEND_read_model_name( connection ):
    """ Request the model name of the device """
    data = [  1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )

def SEND_FT_1_Sample_Output( connection ):
    """ Request a single F-T sensor reading """
    data = [ 10 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )
    
def SEND_Read_Overload_Log( connection ):
    """ Read the overloads for each axis """
    data = [ 18 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )    
    
def SEND_Read_Filter_Setting( connection ):
    """ Request the filter settings """
    data = [  9 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )  
    
def SEND_Set_Filter_Setting( connection , cutoffHz ):
    """ Request the filter setting change """
    CMD      = 8
    filtFlag = 0
    filtFreq = 0
    byteLookup = { 
        0:        0   ,	# No filtering
        500:	  1 ,    30:	 8   , # Cutoff Frequency
        300:	  2 ,    20:	 9   ,
        200:	  3 ,    10:	10   ,
        150:	  4 ,     5:	11   ,
        100:	  5 ,     3:	12   ,
        50:	  6 ,     2:	13   ,
        40:	  7 ,     1:	14    
    }    
    if cutoffHz not in byteLookup:
        raise KeyError( "Filter setting " + str( cutoffHz ) + " is not available, Must be one of " + str( list( byteLookup.keys() ) ) )
    elif cutoffHz == 0:
        filtFlag = 0
        filtFreq = 0
    else:
        filtFlag = 1
        filtFreq = byteLookup[ cutoffHz ]        
    data = [  8 , filtFlag , filtFreq ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )  
    
def SEND_FT_Output_Begin( connection ):
    """ Request a single F-T sensor reading """
    data = [ 11 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )
    
def SEND_FT_Output_End( connection ):
    """ Request a single F-T sensor reading """
    data = [ 12 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ]
    SEND_CMD( connection , data )
    
# ~ Receive ~

_ERRCODES = {
    0 : "Unsupported command" ,
    1 : "Setting range error" , 
    2 : "Data storage error"
}

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

def RECV_read_model_name( packetList ):
    """ Interpret bytes as the model name """
    data = packetList[ 2 : -2 ]
    rtnStr = ""
    for bite in data:
        rtnStr += chr( bite )
    return rtnStr

def F_and_T_from_upper_lower( upperByte , lowerByte ):
    """ Perform the force and torque calculations from the 'upperByte' and 'lowerByte' , per page 15 of the manual , Return ( F , T ) """
    # NOTE: This function computes both the force [0] and torque [1] interpretations , and it is up to the client code to choose correcly
    raw = c_uint16( 256 ).value * c_uint16( upperByte ).value + c_uint16( lowerByte ).value
    raw = c_int16( raw )
    #      ( Force      , Torque       )
    return ( raw.value / 50.0 , raw.value / 2000.0 )

def interpret_force_bytes( data_D2toD14 ):
    """ Interpret response data bytes R1 to R14 as a sensor reading 
    R1  : Fx's upper byte  ,  R2  : Fx's lower byte
    R3  : Fy's upper byte  ,  R4  : Fy's lower byte
    R5  : Fz's upper byte  ,  R6  : Fz's lower byte
    R7  : Tx's upper byte  ,  R8  : Tx's lower byte
    R9  : Ty's upper byte  ,  R10 : Ty's lower byte
    R11 : Tz's upper byte  ,  R12 : Tz's upper byte
    R12 : Overload Status
    """
    return [
        F_and_T_from_upper_lower( data_D2toD14[  0 ] , data_D2toD14[  1 ] )[0] , # F_x , Force
        F_and_T_from_upper_lower( data_D2toD14[  2 ] , data_D2toD14[  3 ] )[0] , # F_y , Force
        F_and_T_from_upper_lower( data_D2toD14[  4 ] , data_D2toD14[  5 ] )[0] , # F_z , Force
        F_and_T_from_upper_lower( data_D2toD14[  6 ] , data_D2toD14[  7 ] )[1] , # T_x , Torque
        F_and_T_from_upper_lower( data_D2toD14[  8 ] , data_D2toD14[  9 ] )[1] , # T_y , Torque
        F_and_T_from_upper_lower( data_D2toD14[ 10 ] , data_D2toD14[ 11 ] )[1] , # T_z , Torque
    ] , data_D2toD14[ 12 ]

def RECV_FT_1_Sample_Output( packetList ):
    """ Receive and interpret a single F-T reading """
    data = packetList[ 2 : -4 ]
    print "Interpret" , len( data ) , "bytes"
    return interpret_force_bytes( data )

def RECV_Read_Overload_Log( packetList ):
    """ Read and interpret the overloads list 
    R1 : Fx Overload count
    R2 : Fy Overload count
    R3 : Fz Overload count
    R4 : Tx Overload count
    R5 : Ty Overload count
    R6 : Tz Overload count    
    """
    return packetList[ 2 : 8 ]

def RECV_Read_Filter_Setting( packetList ):
    """ Read and interpret the filter setting 
    R1 : Filter Type --> { 0: No filter , 1: Maybe filter }
    R2 : Filter detailed setting value -->
    """
    data = packetList[ 2 : 4 ]
    HzLookup = { 
        0:        0   ,	# No filtering
        1:	500   ,    8:	30   , # Cutoff Frequency
        2:	300   ,    9:	20   ,
        3:	200   ,   10:	10   ,
        4:	150   ,   11:	 5   ,
        5:	100   ,   12:	 3   ,
        6:	 50   ,   13:	 2   ,
        7:	 40   ,   14:	 1   
    }
    return { "FilterOn" : bool( data[0] ) , "CutoffHz" : HzLookup[ data[1] ] }
    
def RECV_Set_Filter_Setting( packetList ):
    """ Interpret the filter setting change result """
    data = packetList[ 2 : 4 ]
    return { "Success": bool( data[0] ) , "ErrorCode" : ( "OK" if data[0] else _ERRCODES[ data[1] ] ) }

# _ End Command _


# = Program Vars =

#COMLIST = [ '/dev/ttyUSB0' , '/dev/ttyS0' ]
#COMLIST = [ '/dev/ttyUSB1' , '/dev/ttyUSB0' ]
COMLIST = [ '/dev/ttyUSB0' ]

#TSTLIST = [ '/dev/ttyS0'   , '/dev/ttyUSB0' ]
#TSTLIST = [ '/dev/ttyUSB0' , '/dev/ttyS0'   ]
TSTLIST = [ '/dev/ttyUSB1' ]

COMMPORTEN = True
TESTPORTEN = False

# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    ser = None
    tst = None
    
    print "Available Ports" , endl , list_available_ports()
    
    BAUD = 115200 # 921600 # 460800 # 230400 # 115200 # 57600
    
    if COMMPORTEN:
        #print "Connecting to the serial port ..."
        ser = attempt_connection( COMLIST , BAUD ) # Speed must match the port selected in the Arduino IDE

    if TESTPORTEN:    
        print "Starting the test connections ..."
        tst = attempt_connection( TSTLIST , BAUD ) # Speed must match the port selected in the Arduino IDE

    # Send formatted messages and listen for data back on the test port
    if 0:
        
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
    if 1:
        
        sendTrials = 1
        recvTrials = 1        
        
        # 1. Send test bytes
        for i in xrange( sendTrials ):
            
            # Test 1 : Read Model Name
            #SEND_read_model_name( ser )
            
            # Test 2 : Get a force reading
            #SEND_FT_1_Sample_Output( ser )
            
            # Test 3 : Read overload count
            #SEND_Read_Overload_Log( ser )
            
            # Test 4 : Read filter settings
            #SEND_Read_Filter_Setting( ser )
            
            # Test 5 : Set the filter cutoff
            #SEND_Set_Filter_Setting( ser , 500 )
            
            # Test 6 : Stream data
            SEND_FT_Output_Begin( ser )
            
            sleep(0.001)
        
        sleep( 1 )
        
        if 0:
            # 2. Interpret messages
            for i in xrange( recvTrials ):
                stream = get_all_bytes_from_connection( ser )
                if len( stream ):
                    
                    # Command Message
                    #msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 1 + 8 + 1 + 1 )
                    
                    # Response Message
                    msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 1 + 16 + 1 + 1 )     
                    for msg in msgs:
                        
                        # Test 1 : Get model name
                        #print '\t\t' , RECV_read_model_name( msg )
                        
                        # Test 2 : Get sensor reading
                        #print '\t\t' , RECV_FT_1_Sample_Output( msg )
                        
                        # Test 3 : Get overload count
                        #print '\t\t' , RECV_Read_Overload_Log( msg )                    
                        
                        # Test 4 : Read filter settings
                        #print '\t\t' , RECV_Read_Filter_Setting( msg )  
                        
                        # Test 5 : Set the filter cutoff
                        print '\t\t' , RECV_Set_Filter_Setting( msg )                    
                
                print '\t' , len( msgs ) , "messages in" , len( stream ) , "bytes"
            sleep(0.25) 
        
        if 1:
            
            limit = 50
            count =  0
            
            while 1:
                stream = get_all_bytes_from_connection( ser )
                if len( stream ):
                    
                    # Command Message
                    #msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 1 + 8 + 1 + 1 )
                    
                    # Response Message
                    msgs = get_messages_from_mass_bytes( stream , SOP , EOP , 1 + 16 + 1 + 1 )     
                    for msg in msgs:
                        
                        try:
                            # Test 2 : Get sensor reading
                            print '\t\t' , RECV_FT_1_Sample_Output( msg )   
                        except:
                            print '\t\tBad Reading!'
                sleep( 0.05 )
                count += 1
                if count >= limit:
                    break
    
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
    
    print "Closing stream ..."
    if COMMPORTEN:
        SEND_FT_Output_End( ser )
    if TESTPORTEN:
        SEND_FT_Output_End( tst )
        
    print "Closing port(s) ..."
    if COMMPORTEN:
        ser.close()
    if TESTPORTEN:
        tst.close()
    
    print "Exit."

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
