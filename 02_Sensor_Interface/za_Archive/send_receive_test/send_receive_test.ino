/* 
Serial_Relay_V1.ino
James Watson , 2018 November
Serial relay , send every byte received via wired serial out over the wireless connection
*/

// == Init =================================================================================================================================

// ~~ Shortcuts and Aliases ~~
#define Sensor Serial1 // on pins 19 (RX) and 18 (TX)
#define Tstcon Serial2 // on pins 17 (RX) and 16 (TX)

// ~~ Variables ~~
bool gotBytes = false;
byte readByte =   0;
byte SOP      =  85; // Start of Packet , Robotous Manual - pg 9
byte EOP      = 170; // End of Packet   , Robotous Manual - pg 9
byte input[ 4 ]  = { 0 , 0 , 0 , 0 };
byte output[ 4 ] = { 1 , 2 , 4 , 8 };


// == End Init =============================================================================================================================


void setup(){
  // Initialize Serial Communication
  Serial.begin( 115200 ); // Info from desktop comes in over the USB wire
  Sensor.begin( 115200 ); // Info from the robot comes in over the XBee wireless
  Tstcon.begin( 115200 ); 
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

// == Main Loop ============================================================================================================================

void loop(){ // Relay the serial data over wireless , no delays 

  if( Serial.available() > 3 ){
    while( Serial.available() ){
      readByte = Serial.read();
      if( readByte == SOP ){
        input[0] = readByte;
        for( byte i = 1 ; i < 4 ; i++ ){ input[i] = Serial.read(); } // Read 4 bytes from the serial connection
        if( input[3] == EOP ){
          gotBytes = true;
          digitalWrite(LED_BUILTIN, HIGH);
        }else{
          gotBytes = false;
          digitalWrite(LED_BUILTIN, LOW);
        }
      }
    }
  }else{
    gotBytes = false;
    digitalWrite(LED_BUILTIN, LOW);
  }

  if( gotBytes ){
    for( byte i = 0 ; i < 4 ; i++ ){ Sensor.write( input[i] ); } // Write 4 bytes to the serial connection
  }

  if( Tstcon.available() > 3 ){
    while( Tstcon.available() ){
      Serial.write( Tstcon.read() );
    }
  }

//  for( int i = 0 ; i < 4 ; i++ ){
//    Serial.write( 125 );
//  }

//  // COMP --> SENSOR
//  if( Tstcon.available() > 0 ){
//    while( Tstcon.available() > 0 ){
//      readByte = Tstcon.read();
//      Sensor.write( readByte );
//      Serial.print( "Got byte: " );
//      Serial.println( readByte );
//    }
//  }
//
//  // SENSOR --> COMP
//  if( Sensor.available() > 0 ){
//    while( Sensor.available() > 0 ){
//      readByte = Sensor.read();
//      Serial.write( readByte );
//      Tstcon.write( readByte );
//    }
//  }

//  delay( 250 ); // [ms]
//  Tstcon.write( 255 );
//  Sensor.write( 255 );

}

// == End Loop =============================================================================================================================
