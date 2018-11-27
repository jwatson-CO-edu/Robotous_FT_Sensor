/* 
Serial_Relay_V1.ino
James Watson , 2018 November
Serial relay , send every byte received via wired serial out over the wireless connection
*/

// == Init =================================================================================================================================

// ~~ Shortcuts and Aliases ~~
#define Sensor Serial1 // on pins 19 (RX) and 18 (TX)

// ~~ Variables ~~
bool       gotBytes = false;
bool       sent     = false;
byte       readByte =   0;
byte       SOP      =  85; // Start of Packet , Robotous Manual - pg 9
byte       EOP      = 170; // End of Packet   , Robotous Manual - pg 9
const byte inpLen   = 1 +  8 + 1 + 1; // <packet> SOP | DATA x 8 | CHKSUM | EOP </packet>
const byte outpLn   = 1 + 16 + 1 + 1; // <packet> SOP | DATA x16 | CHKSUM | EOP </packet>
const byte _REPEAT  = 3;

byte input[ inpLen ] = { 0 , 
                         0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 
                         0 , 0 };
byte outpt[ outpLn ] = { 0 , 
                         0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 
                         0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 
                         0 , 0 };


// == End Init =============================================================================================================================

// == Serial Functions ==

void zero_input(){  for( int i = 0 ; i < inpLen ; i++ ){  input[i] = 0;  }  }
void zero_outpt(){  for( int i = 0 ; i < outpLn ; i++ ){  outpt[i] = 0;  }  }

// __ End Serial __

void setup(){
  // Initialize Serial Communication
  Serial.begin( 115200 ); // Info from desktop comes in over the USB wire
  Sensor.begin( 115200 ); // Info from the robot comes in over the XBee wireless

//  Tstcon.begin( 115200 ); 

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

// == Main Loop ============================================================================================================================

void loop(){ // Relay the serial data over wireless , no delays 

  /// ### COMP --to-> SNSR #################################################

  // 1. If we have a number of bytes at least as long as a message , then  
  if( Serial.available() > inpLen - 1 ){
    // 2. While there are still bytes to read , read a byte
    while( Serial.available() ){
      readByte = Serial.read();
      // 3. If the byte is the beginning of a packet , then read a packet's worth of bytes
      if( readByte == SOP ){
        input[0] = readByte;
        for( int i = 1 ; i < inpLen ; i++ ){ input[i] = Serial.read(); } // Read 4 bytes from the serial connection
        // 4. If the packet ends properly , then set joy flag
        if( input[inpLen - 1] == EOP ){
          gotBytes = true;
          digitalWrite(LED_BUILTIN, HIGH);
        // 5. else no joy , erase the input arr if there was none stored already
        }else if( !gotBytes ){
          gotBytes = false;
          zero_input();
          digitalWrite(LED_BUILTIN, LOW);
        }else{
          digitalWrite(LED_BUILTIN, LOW);
        }
      }
    }
  // 6. else do not have enough bytes for message , no joy , ignore
  }else{
    gotBytes = false;
    digitalWrite( LED_BUILTIN , LOW );
  }

  // 7. If we got a properly-formed message , send it to the sensor '_REPEAT' times
 
  for( byte j = 0 ; j < _REPEAT ; j++ ){
    for( byte i = 0 ; i < inpLen ; i++ ){ Sensor.write( input[i] ); } // Write 4 bytes to the serial connection
//      Sensor.write( (byte*)input , sizeof( input ) );
  }

  /// ### SNSR --to-> COMP #################################################

//  if( Sensor.available() > outpLn - 1 ){
//    // 2. While there are still bytes to read , read a byte
//    while( Sensor.available() ){
//      readByte = Sensor.read();
//      Serial.write( readByte );
//    }
//  }



}

// == End Loop =============================================================================================================================
