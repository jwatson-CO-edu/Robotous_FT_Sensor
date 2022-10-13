/* 
Serial_Relay_V1.ino
James Watson , 2018 November
Serial relay , send every byte received via wired serial out over the wireless connection
*/

// == Init =================================================================================================================================

// ~~ Shortcuts and Aliases ~~
#define Sensor Serial1 // on pins 19 (RX) and 18 (TX)

char readByte = 0;

// == End Init =============================================================================================================================


void setup(){
	// Initialize Serial Communication
	Serial.begin( 115200 ); // Info from desktop comes in over the USB wire
	Sensor.begin( 115200 ); // Info from the robot comes in over the XBee wireless
}

// == Main Loop ============================================================================================================================

void loop(){ // Relay the serial data over wireless , no delays 

	// COMP --> SENSOR
	if( Serial.available() > 0 ){
		while( Serial.available() > 0 ){
      readByte = Serial.read();
			Sensor.write( readByte );
      //Serial.println( readByte );
		}
	}

	// SENSOR --> COMP
	if( Sensor.available() > 0 ){
		while( Sensor.available() > 0 ){
			Serial.write( Sensor.read() );
		}
	}

}

// == End Loop =============================================================================================================================
