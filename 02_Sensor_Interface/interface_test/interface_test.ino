// ~~ Shortcuts and Aliases ~~
#define Sensor Serial1 // on pins 19 (RX) and 18 (TX)

// == Global Vars ==

// Composition of input and output messages
byte cmd[ 11 ] = { 0 , // Start of Packet (SOP) , 1b
                   0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , // Data 8b
                   0 , 0  }; // Checksum , End of Packet (EOP) - 1b , 1b
byte res[ 19 ] = { 0 , // Start of Packet (SOP) , 1b
                   0 , 0 , 0 , 0 , // Data 16b
                   0 , 0 , 0 , 0 ,  
                   0 , 0 , 0 , 0 , 
                   0 , 0 , 0 , 0 , 
                   0 , 0 }; // Checksum , End of Packet (EOP) - 1b , 1b

// __ End Global __

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}
