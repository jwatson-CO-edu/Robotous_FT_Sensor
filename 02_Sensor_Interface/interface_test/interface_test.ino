/* 
Serial_Relay_V1.ino
James Watson , 2018 November
Serial relay , send every byte received via wired serial out over the wireless connection
*/

// == Init =================================================================================================================================

// ~~ Shortcuts and Aliases ~~
#define Sensor Serial1 // on pins 19 (RX) and 18 (TX)
#define Tstcon Serial3 // on pins 15 (RX) and 14 (TX)

char readByte = 0;

// == End Init =============================================================================================================================


void setup(){
  // Initialize Serial Communication
  Serial.begin( 115200 ); // Info from desktop comes in over the USB wire
  Sensor.begin( 115200 ); // Info from the robot comes in over the XBee wireless
  Tstcon.begin( 115200 ); 
}

// == Main Loop ============================================================================================================================

void loop(){ // Relay the serial data over wireless , no delays 

  // COMP --> SENSOR
  if( Tstcon.available() > 0 ){
    while( Tstcon.available() > 0 ){
      readByte = Tstcon.read();
      Sensor.write( readByte );
      Serial.print( "Got byte: " );
      Serial.println( readByte );
    }
  }

  // SENSOR --> COMP
  if( Sensor.available() > 0 ){
    while( Sensor.available() > 0 ){
      readByte = Sensor.read();
      Serial.write( readByte );
      Tstcon.write( readByte );
    }
  }

  delay( 250 ); // [ms]
  Tstcon.write( 255 );
  Sensor.write( 255 );

}

// == End Loop =============================================================================================================================
