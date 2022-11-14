////////// SETUP ///////////////////////////////////////////////////////////////////////////////////

///// Globals & Constants /////
const unsigned int  CMD_DATA_SIZE =  8;
const unsigned int  CMD_PKT_SIZE  = CMD_DATA_SIZE+3;
const unsigned int  CMD_CHK_IDX   = CMD_DATA_SIZE+1;
const unsigned int  RES_DATA_SIZE = 16;
const unsigned int  RES_PKT_SIZE  = RES_DATA_SIZE+3;
const unsigned int  RES_OVRLD_IDX = RES_DATA_SIZE-2;
const unsigned long LOOP_DELAY    = 20;
const unsigned char SOP           = 0x55;
const unsigned char EOP           = 0xAA;
unsigned char       command[  CMD_PKT_SIZE ];
unsigned char       response[ RES_PKT_SIZE ];
float               FT[6];
unsigned int        i;
bool                resValid = false;



////////// COMMUNICATION FUNCTIONS /////////////////////////////////////////////////////////////////

void set_command_packet_ends(){
  command[ 0              ] = SOP;
  command[ CMD_PKT_SIZE-1 ] = EOP;
}

void compute_checksum(){
  unsigned char total = 0;
  for( i=1; i<CMD_CHK_IDX; i++ ){
    total += command[i];
  }  
  command[ CMD_CHK_IDX ] = total;
}

void pack_data_begin(){
  set_command_packet_ends();
  command[1] = 0x0B;
  for( i=2; i<CMD_CHK_IDX; i++ ){
    command[i] = 0x00;    
  }
  compute_checksum();
}

void pack_read_once(){
  set_command_packet_ends();
  command[1] = 0x0A;
  for( i=2; i<(CMD_DATA_SIZE+1); i++ ){
    command[i] = 0x00;    
  }
  compute_checksum();
}

void pack_bias_set(){
  set_command_packet_ends();
  command[1] = 0x11;
  command[2] = 0x01;
  for( i=3; i<(CMD_DATA_SIZE+1); i++ ){
    command[i] = 0x00;    
  }
  compute_checksum();
}

void pack_bias_unset(){
  set_command_packet_ends();
  command[1] = 0x11;
  command[2] = 0x00;
  for( i=3; i<(CMD_DATA_SIZE+1); i++ ){
    command[i] = 0x00;    
  }
  compute_checksum();
}

void send_cmd(){
  for( i=0; i<CMD_PKT_SIZE; i++ ){
    Serial1.write( command[i] );   
  }
}

void printHex(uint8_t num) {
  // Author: leoc7
  // https://arduino.stackexchange.com/a/60865
  char hexCar[2];
  sprintf(hexCar, "%02X ", num);
  Serial.print(hexCar);
}

unsigned char read_overload(){
  return response[ RES_OVRLD_IDX ] & 0b00111111;
}

void interpret_FT(){
  
  FT[0] = (int)(response[ 2]*256+response[ 3]) /   50.0;
  FT[1] = (int)(response[ 4]*256+response[ 5]) /   50.0;
  FT[2] = (int)(response[ 6]*256+response[ 7]) /   50.0;
  FT[3] = (int)(response[ 8]*256+response[ 9]) / 2000.0;
  FT[5] = (int)(response[10]*256+response[11]) / 2000.0;
  FT[6] = (int)(response[12]*256+response[13]) / 2000.0;
  
  // int FyRaw = response[4];
  // FyRaw = FyRaw << 8;
  // FyRaw = FyRaw & response[5];
  // FT[1] = FyRaw / 50.0;

  // int FzRaw = response[6];
  // FzRaw = FzRaw << 8;
  // FzRaw = FzRaw & response[7];
  // FT[2] = FzRaw / 50.0;

  // int TxRaw = response[8];
  // TxRaw = TxRaw << 8;
  // TxRaw = TxRaw & response[9];
  // FT[3] = TxRaw / 2000.0;
  
  // int TyRaw = response[10];
  // TyRaw = TyRaw << 8;
  // TyRaw = TyRaw & response[11];
  // FT[4] = TyRaw / 2000.0;

  // int TzRaw = response[12];
  // TzRaw = TzRaw << 8;
  // TzRaw = TzRaw & response[13];
  // FT[5] = TzRaw / 2000.0;
}

void recv_res(){
  int resByte = 0;
  if( Serial1.available() >= RES_PKT_SIZE ){
    while( (resByte != SOP) && Serial1.available() ){
      resByte = Serial1.read();
    }
    if( (resByte == SOP) && Serial1.available() ){
      response[0] = resByte;
    }
    for( i=1; i<RES_PKT_SIZE; i++){
      if( Serial1.available() ){
        resByte = Serial1.read();
        if( resByte != -1 ){
          response[i] = resByte;
        }else{
          response[i] = 0x00;
        }
      }
    }
    resValid = ( response[RES_PKT_SIZE-1] == EOP );
    if(resValid){
      // for(i=0; i<sizeof(response); i++){
      //   printHex(response[i]);
      // }
      interpret_FT();
      for( i=0; i<6; i++ ){        
        Serial.print( FT[i] );
        Serial.print( " " );
      }
      // Serial.println();
      // printHex( read_overload() );
      Serial.print( read_overload(), BIN );
      Serial.println();
    }      
  }
}

////////// INIT ////////////////////////////////////////////////////////////////////////////////////

void setup() {
  Serial.begin( 9600 );
  delay( 100 );
  Serial1.begin( 115200 );
  delay( 100 );
  pack_data_begin();
  send_cmd();
  delay( 5 );
  pack_bias_set();
  send_cmd();
  send_cmd();
  send_cmd();
  send_cmd();
  send_cmd();
  send_cmd();
  delay( 5 );
}


////////// MAIN ////////////////////////////////////////////////////////////////////////////////////

void loop() {
  // put your main code here, to run repeatedly:
  // pack_bias_set();
  // send_cmd();  
  // send_cmd();  
  // delay( 10 );
  pack_read_once();
  send_cmd();
  // send_cmd();
  // send_cmd();
  // send_cmd();  
  
  delay( LOOP_DELAY );

  recv_res();
}
