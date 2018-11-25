#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

# serial_to_robot_msg_TEST.py
# James Watson , 2017 April
# Send serial messages to the Uno relay to be interpreted by the robot
# Interpret serial messages from the Uno relay sent by the robot

# == Init ==================================================================================================================================

import serial # pySerial for USB comms w/ Arduino
import time # - for delays
import struct # for data composition over serial
import rospy
# from std_msgs.msg import String
from robot_controller.msg import RoboCmd # --- Commands going to the robot
from robot_controller.msg import RobotStatus # Status coming from the robot

# == End Init ==============================================================================================================================

# == Helper Functions & Classes ==

def tokenize_with_wspace( rawStr , evalFunc = str ): 
    """ Return a list of tokens taken from 'rawStr' that is partitioned with whitespace, transforming each token with 'evalFunc' """
    return [ evalFunc( rawToken ) for rawToken in rawStr.split() ]

class HeartRate: # NOTE: This fulfills a purpose similar to the rospy rate # NOT USED?
    """ Sleeps for a time such that the period between calls to sleep results in a frequency not greater than the specified 'Hz' """
    def __init__( self , Hz ):
        """ Create a rate object with a Do-Not-Exceed frequency in 'Hz' """
        self.period = 1.0 / Hz; # Set the period as the inverse of the frequency , hearbeat will not exceed 'Hz' , but can be lower
        self.last = time.time()
    def sleep( self ):
        """ Sleep for a time so that the frequency is not exceeded """
        elapsed = time.time() - self.last
        if elapsed < self.period:
            time.sleep( self.period - elapsed )
        self.last = time.time()

# == End Helpers ==

# == Serial Command Functions ==

CMDMAX = 250

def constrain_cmd( number ):
	""" Constrain the command parameter to an integer within [ 0 , CMDMAX ] , inclusive """
	number = int( number )
	if number < 0: number = 0
	elif number > CMDMAX: number = CMDMAX
	return number

# ~~ Translate ~~
# 255 , 255 , DISTANCE_CM , DISTANCE_CM , CM_PER_SEC ,  CM_PER_SEC
# Header    | Displacement in cm        | Speed in cm/s

def send_translate_distance_speed( connection , distance , speed ):
	""" Send a translate command over the serial 'connection' with a specified 'distance' and 'speed' """
	distance = constrain_cmd( distance )
	speed    = constrain_cmd( speed )
	connection.write( struct.pack( 'BBBBBB' , 255 , 255 , distance , distance , speed , speed ) )

# ~~ Reverse ~~ // This is for collision recovery
# 251 , 251 , NEGATIVE_CM , NEGATIVE_CM , CM_PER_SEC ,  CM_PER_SEC
# Header    | Displacement in cm        | Speed in cm/s

def send_reverse_distance_speed( connection , distance , speed ):
	""" Send a translate command over the serial 'connection' with a specified 'distance' and 'speed' """
	distance = constrain_cmd( distance )
	speed    = constrain_cmd( speed )
	connection.write( struct.pack( 'BBBBBB' , 251 , 251 , distance , distance , speed , speed ) )

# ~~ Rotate ~~
# 254 , 254 , ANGLE_HALF_DEG , ANGLE_HALF_DEG , DEG_PER_SEC , DEG_PER_SEC
# Header    | Rotation in degrees             | Rotational speed in deg/s
# The robot will always rotate through an arc <= 180deg to achieve the desired angular displacement , Angle is specified as half the 
# desired value, specifying X will result in a 2X rotation , Rotations must be integers and therefore only multiples of 2 degrees will be 
# executed in order to fit within the constraints of one byte

def send_rotate_angle_speed( connection , angle , speed ):
	""" Send a rotate command over the serial 'connection' with a specified 'distance' and 'speed' """
	speed = constrain_cmd( speed )
	if angle < 0: # Angle must be a positive number, fit to [ 0 , 360 ]
		angle += 360
	angle = int( angle / 2.0 ) # Angles are specified by half of that desired, due to the size constraint of a byte
	connection.write( struct.pack( 'BBBBBB' , 254 , 254 , angle , angle , speed , speed ) )

# ~~ Serial Connection ~~

def attempt_connection( COMlist , speed ):
    """ Attempt to connect to each of 'COMlist' until one succeeds """
    ser = None
    for port in COMlist:
        try:
            ser = serial.Serial( port , speed ) # 115200 ) # This must match the port selected in the Arduino IDE
            print "Connected to port:" , port 
            return ser
        except Exception as ex:
            print "ERROR: COULD NOT ESTABLISH SERIAL CONNECTION WITH" , port , ", Check that the port is correct ..."
            print ex
    raise Warning( "attempt_connection: Unable to connect to any of " + str( COMlist ) ) # If we made it to here , we attempted all the ports

# == End Serial Commands ==

# == ROS Functions ==

def drive_cb( data ):
    """ Respond to drive data from the system """
    #rospy.loginfo( rospy.get_caller_id() + 'I heard %s' , data.data)
    
    try:
        # command = raw_input("CMD> ")
        # command = tokenize_with_wspace( command , int ) # Attempt to cast inputs to ints
        """ byte command
            byte magnitude
            byte rate """
        command = [ data.command , data.magnitude , data.rate ]
        print "DEBUG: Got command:" , command
        selection = command[0]
    except:
        print "ERROR: INVALID COMMAND"

    if selection == 0: # ~~ EXIT ~~
        print "EXIT" # This doesn't have an effect anymore?
        # runMenu = False
    elif selection == 1: # ~~ TRANSLATE ~~
        send_translate_distance_speed( ser , command[1] , command[2] )
        print "Sent Translate Command:" , command[1] , command[2]
    elif selection == 2: # ~~ ROTATE ~~
        send_rotate_angle_speed( ser , command[1] , command[2] )
        print "Sent Rotate Command:   " , command[1] , command[2]
    elif selection == 3: # ~~ REVERSE ~~
        send_reverse_distance_speed( ser , command[1] , command[2] )
        print "Sent Reverse Command:  " , command[1] , command[2]
    else: # ~~ ERROR ~~
        print "ERROR: INVALID COMMAND"
        
# == End ROS Func ==


# == Main ==================================================================================================================================

COMLIST = [ '/dev/ttyUSB1' , '/dev/ttyACM0' , '/dev/ttyACM1' , '/dev/ttyACM2' , 'COM0' , 'COM1' , 'COM2']

if __name__ == "__main__":
    
    """ Listen for drive commands from the system """

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    
    rospy.init_node( 'drive_cmd_listener' , anonymous = True ) # Notify ROS of this node
    # The anonymous=True flag tells rospy to generate a unique name for the node so that you can have multiple listener.py nodes run easily
    
    # Let the subscriber handle things in its own thread
    rospy.Subscriber( '/drive_cmd' , RoboCmd , drive_cb ) # callback-based mechanism for subscribing to messages
    
    pub = rospy.Publisher( '/robot_status' , RobotStatus , queue_size = 1 ) # queue_size argument limits the amount of queued messages 

    rate = rospy.Rate( 10 )

    ser = attempt_connection( COMLIST , 9600 ) # Speed must match the port selected in the Arduino IDE
       
    inByte1 = 0
    inByte2 = 0
    
    msgLen = 2 * 3 + 3 # The number of characters of the string representation of the message must be at least this many
    
    while not rospy.is_shutdown(): # While ROS is running
        
        if ser.inWaiting() > msgLen: # Brings it in as a string , with each of the byte values separated by '\n' , Fricken bass-ackwards
            inByte1 = ser.read( ser.inWaiting() )
            statusMsg = [ elem for elem in inByte1.splitlines() ]
            if len( statusMsg ) == 6: # A properly-formed message will have exactly 6 values
                try:
                    msgNums = [ int( elem ) for elem in statusMsg ]
                except: # Sometimes weird strings come over!
                    print "DEBUG: This is a weird message!:" , statusMsg
                    continue
                #          v-- Type                    v-- Distance Value          v-- Angle Value
                if msgNums[0] != msgNums[1] or msgNums[2] != msgNums[3] or msgNums[4] != msgNums[5]: 
                    continue # If the three repeated parts of the message do not match , discard the message
                    
                # Get the status header
                if   msgNums[0] == 252:
                    statusStr = "IDLE"
                elif msgNums[0] == 255:
                    statusStr = "EXEC_TRANS"
                elif msgNums[0] == 254:
                    statusStr = "EXEC_ROTAT"
                elif msgNums[0] == 111: # Something unexpected happened on the robot
                    statusStr = "BAD_STATE"
                else: # The robot sent something unexpected
                    statusStr = "UNKNOWN_ST" 
                    
                # Get the magnitude data
                cmMag = msgNums[2] # Get the linear magnitude
                dgMag = msgNums[4] # Get the angular magnitude
                
                # Assemble and send the message
                """ string status  # Represents the status of the robot
                    float32 cm_mag # cm  traveled or cm  to go
                    float32 dg_mag # deg traveled or deg to go """
                statusMsg = RobotStatus()
                statusMsg.status = statusStr
                statusMsg.cm_mag = cmMag
                statusMsg.dg_mag = dgMag
                pub.publish( statusMsg )
        
        rate.sleep()
        
# == End Main ==============================================================================================================================
