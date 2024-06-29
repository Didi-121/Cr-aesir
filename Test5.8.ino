//Serial1 is used for comunication with raspberry pi while Serial is used for dynamixel shield
//Pines 19 (RX) y 18 (TX)
#include <DualG2HighPowerMotorShield.h>
#include <DynamixelShield.h>

DynamixelShield dxl;
//This namespace is required to use Control table item names
using namespace ControlTableItem;

//This struct is used to store important info of each servo 
typedef struct Servos {

  int id;
  int cw_limit;
  int ccw_limit;

  /*There are 4 types of setting the position of a servo
    1 = 0 to 1023
    2 = 0 to 1023 but the direction is flipped (1023 - actualPosition)
    3 = 0 to 4095
    4 = 0 to 4095 but the direction is flipped (4095 - actualPosition)*/
  int directionType; 

  //Servo that moves at the same time
  int mirrorServo;

  float protocol;

  //if it is connected with other servos 
  bool mirroring; 
  bool conected; 

  uint8_t op_mode;

};

Servos servo0 = {0, 1130, 3243, 4, 1, 1.0, false, false, OP_POSITION};
Servos servo1 = {1, 2745, 631, 3, NULL, 1.0,  false, false, OP_POSITION };
Servos servo2 = {2, 3830, 1794, 3, NULL, 1.0, false, false, OP_POSITION };

Servos servo3 = {4, 792, 222 , 2, 4, 1.0, false, false, OP_POSITION };
Servos servo4 = {3, 231, 801, 1, NULL, 1.0, false, false, OP_POSITION };

Servos servo5 = {5, 227, 1000, 1, 6, 1.0, true, false, OP_POSITION };
Servos servo6 = {6, 796, 207, 2, NULL, 1.0, false, false, OP_POSITION };

Servos servo7 = {7, 1023, 222, 1, NULL, 1.0, false, false, OP_POSITION };

Servos servo8 = {8, 0, 4000, 1, NULL, 2.0, false, false, OP_POSITION };
Servos servo9 = {9, 9868, 2411, 1, NULL, 2.0, false, false, OP_CURRENT_BASED_POSITION };

Servos servos_list[10] = {servo0, servo1, servo2, servo3, servo4, servo5, servo6, servo7, servo8, servo9};

//String used to store mesagges from the raspberry pi 
String received, chopped, information_tosend;

//ints used to control the servos
int id, mirrorID, position, mirrorPosition, ctrlTableItem;
int servoSpeed = 121;

DualG2HighPowerMotorShield18v22 pololuDriver;
//speed of pololu driver 0-400 
int dcSpeed = 400; 

float dxl_protocol;

void setup() {

  //serial1 is used for communication with the raspberry pi
  Serial1.begin(9600);
  Serial1.setTimeout(5);
  
  // Set Port baudrate to  1M this has to match with DYNAMIXEL's servos baud rate 
  dxl.begin(1000000);

  for(int i = 0 ; i<= sizeof(servos_list) ; i++){
    servoSetup(i);
  }

  pololuDriver.init();
  pololuDriver.calibrateCurrentOffsets();
  delay(10);
  //flip a motor's direction:
  pololuDriver.flipM1(true);

}

void loop() {

  if (Serial1.available()) {

    // Recieve information from the raspberry. EG of a command for moving a servo: SF01
    received = Serial1.readString();
    Serial1.println("d: Raw information received: " + received);

    //Many commands could be received with one message 
    while(received != ""){ 
        
      //get the command from the message and deletes it from the original string
      chopped = chopper(received, ' ');
      //Serial1.println("d: chopped or used command: " + chopped);

      //First char of the command
      switch (chopped[0]) {

        //case for Dc motors
        case 'D' : 
          chopped.remove(0, 1);

          //second char of the comand
          switch (chopped[0]) {

            case 'W':
              chopped.remove(0, 1);
              pololuDriver.enableDrivers();
              pololuDriver.setM1Speed(dcSpeed);
              pololuDriver.setM2Speed(dcSpeed);
              stopIfFault();
              break;

            case 'S':
              chopped.remove(0, 1);
              pololuDriver.enableDrivers();
              delay(1);
              pololuDriver.setM1Speed( dcSpeed * -1);
              pololuDriver.setM2Speed( dcSpeed * -1);
              stopIfFault();
              break;

            case 'A':
              chopped.remove(0, 1);
              pololuDriver.enableDrivers();
              delay(1);
              pololuDriver.setM1Speed( dcSpeed * -1);
              pololuDriver.setM2Speed( dcSpeed );
              stopIfFault();
              break;

            case 'D':
              chopped.remove(0, 1);
              pololuDriver.enableDrivers();
              delay(1);
              pololuDriver.setM1Speed( dcSpeed );
              pololuDriver.setM2Speed( dcSpeed * -1);
              stopIfFault();
              break;

            default:
              pololuDriver.enableDrivers();
              delay(1);
              pololuDriver.setM1Speed(0);
              pololuDriver.setM2Speed(0);
              stopIfFault();
              break;
          }
          break;

        //case for servos
        case 'S':
          chopped.remove(0, 1);
          
          //second char of the command
          switch (chopped[0]) {

            //move the servo forward
            case 'F':
              chopped.remove(0, 1);
              id = hex(chopped);

              if( ! servos_list[id].mirroring  ){

                writeServo(MOVING_SPEED, id, servoSpeed);
                writeServo(GOAL_POSITION, id, servos_list[id].cw_limit);
                Serial1.println("jalo");

              }else{

                mirrorID = servos_list[id].mirrorServo;
                writeServo(MOVING_SPEED, id, servoSpeed);
                writeServo(MOVING_SPEED, mirrorID , servoSpeed);
                writeServo(GOAL_POSITION, id , servos_list[id].cw_limit);
                writeServo(GOAL_POSITION, mirrorID, servos_list[mirrorID].cw_limit);
                Serial1.println("jalo");
     
              }
              break;

            // B move the servo backward
            case 'B':
              chopped.remove(0, 1);
              id = hex(chopped);
              
              if( ! servos_list[id].mirroring ){

                writeServo(MOVING_SPEED, id, servoSpeed);
                writeServo(GOAL_POSITION, id, servos_list[id].ccw_limit);

              }else{

                mirrorID = servos_list[id].mirrorServo;
                
                writeServo(MOVING_SPEED, id, servoSpeed);
                writeServo(MOVING_SPEED, mirrorID , servoSpeed);
                writeServo(GOAL_POSITION, id , servos_list[id].ccw_limit);
                writeServo(GOAL_POSITION, mirrorID, servos_list[mirrorID].ccw_limit);

              }
              break;

            //P is for moving the servo to an specific position
            case 'P':
              chopped.remove(0, 1);

              id = hex(chopped);
              position = hex(chopped, 3);

              if(position >= servos_list[id].cw_limit && position <= servos_list[id].ccw_limit  || position <= servos_list[id].cw_limit && position >= servos_list[id].ccw_limit  ){
          
                if( ! servos_list[id].mirroring ){
             
                  writeServo(MOVING_SPEED, id, servoSpeed);
                  writeServo(GOAL_POSITION, id, position);
                
                }else{

                  mirrorID = servos_list[id].mirrorServo;

                  switch ( servos_list[mirrorID].directionType){

                    case 1:
                    mirrorPosition = position;
                    break;

                    case 2:
                    mirrorPosition = 1023 - position;
                    break;

                    case 3:
                    mirrorPosition = position;
                    break;

                    case 4:
                    mirrorPosition = 4095 - position;
                    break;

                    default:
                    Serial1.print("e: directiontype isnt recognized");
                    break;
                  }
                  
                  writeServo(MOVING_SPEED, id, servoSpeed);
                  writeServo(MOVING_SPEED, mirrorID, servoSpeed);
                  writeServo(GOAL_POSITION, id, position);
                  writeServo(GOAL_POSITION, mirrorID, mirrorPosition);

                }
              }
              break;

            // R is for reading servo info 
            case 'R':
              chopped.remove(0, 1);
              ctrlTableItem = hex(chopped);

              if(chopped.substring(0) == "" ){

                for( id = 0; id <= sizeof(servos_list) ; id++ ){

                  information_tosend = readServo(PRESENT_POSITION, id);
                  if (information_tosend);
                  Serial1.println("i: id " + String(id) + " " + information_tosend );

                }

              }else{

                id = hex(chopped);
                readServo(ctrlTableItem, id);
                
                information_tosend = readServo(ctrlTableItem, id);
                if (information_tosend);
                Serial1.println("i: id: " + String(id) + " " + information_tosend );

              }
              break;

            // The default command is for stop the servo 
            default:
              id = hex(chopped);

              if( ! servos_list[id].mirroring ){

                position = readServo(PRESENT_POSITION, id);
                writeServo(GOAL_POSITION, id, position);

              }else {

                mirrorID = servos_list[id].mirrorServo;
                position = readServo( PRESENT_POSITION, id );
                mirrorPosition = readServo( PRESENT_POSITION, mirrorID );
                writeServo(GOAL_POSITION, id, position);
                writeServo(GOAL_POSITION, mirrorID, mirrorPosition);

              }
              break;
          }
          break;

        //V is for changing variables   
        case 'V':
        chopped.remove(0,1);

        switch (chopped[0]) {

          case 'Z':
          chopped.remove(0,1);
          dcSpeed = 255;
          break;

          case 'X':
          chopped.remove(0,1);
          dcSpeed = 150;
          break;

          case 'K':
          chopped.remove(0,1);
          dcSpeed = 64;
          break;

          case 'B':
          chopped.remove(0,1);
          servos_list[0].mirroring = true;
          break;

          case 'N':
          chopped.remove(0,1);
          //servos_list[0].mirroring = false;
          break;

        }
      }
    }
  }
}



void servoSetup(uint8_t id){

  // Turn off torque when configuring items in EEPROM area
  uint8_t opmode = servos_list[id].op_mode;

  if( servos_list[id].protocol != dxl_protocol){

    dxl_protocol = servos_list[id].protocol;
    dxl.setPortProtocolVersion( servos_list[id].protocol );
    delay(10);

    }

  dxl.torqueOff(id);
  dxl.setOperatingMode(id, opmode );
  dxl.torqueOn(id);

  if(id == 9)
  dxl.setGoalCurrent(id , 900);
  
}

// Overload
int hex(String& num) {
  return hex(num, 2);
}

// Transform a number in hexadecimal into a decimal
int hex(String& num, int size) {
  if (num.length() >= size) {
    String temp = num.substring(0, size);
    num.remove(0, size);

    int ret = 0;

    for (int i = 0; i < size; i++) {

      if (temp[temp.length() - (i + 1)] >= '0' && temp[temp.length() - (i + 1)] <= '9') {

        ret += ((temp[temp.length() - (i + 1)] - 48) << (4 * i));

      } else if (temp[temp.length() - (i + 1)] >= 'A' && temp[temp.length() - (i + 1)] <= 'F') {
        //Serial1.println(temp[temp.length()-(i+1)]);
        ret += ((temp[temp.length() - (i + 1)] - 55) << (4 * i));
      }
    }
    return ret;
  }
  return 0;
}

// Function used to ping the motor before giving an instruction
bool writeServo(uint8_t cont, uint8_t id, int32_t data){

if( servos_list[id].protocol != dxl_protocol){
 dxl_protocol = servos_list[id].protocol;
 dxl.setPortProtocolVersion(servos_list[id].protocol);
delay(10);
}

if(dxl.ping(id)){

  if( servos_list[id].conected ){

  information_tosend = String(dxl.writeControlTableItem(cont, id, data));
  Serial1.println("d: cmd " + information_tosend + "ctr:  " + cont + "data: " + data);


  }else{

    servos_list[id].conected = true;
    servoSetup(id);
    information_tosend = String(dxl.writeControlTableItem(cont, id, data));
    Serial1.println("d: cmd " + information_tosend + "ctr:  " + cont + "data: " + data);
  }
  return true;

}
return false;

}

//Function used to ping the motor before read servo information
int readServo(uint8_t item_idx, uint8_t id){

if( servos_list[id].protocol != dxl_protocol){
 dxl_protocol = servos_list[id].protocol;
 dxl.setPortProtocolVersion(servos_list[id].protocol);
delay(10);
}

if(dxl.ping(id)){
int read;

  if( servos_list[id].conected ){

  read = dxl.readControlTableItem( item_idx,  id);

  }else{
    servos_list[id].conected = true;
    servoSetup(id);
    read = dxl.readControlTableItem( item_idx,  id);
  }

  return read;

}

return false;
}

//This function returns a part of the string and deltes it from the original 
String chopper(String& comand, char cut){
  int cut_index = comand.indexOf(cut);
  String temporal;

  if(cut_index != -1){
    temporal = comand.substring(0, cut_index); 
    comand.remove(0, cut_index + 1); 

  }else{
    temporal = comand.substring(0, cut_index); 
    comand.remove(0, cut_index); 
  }
  return temporal;
}

void stopIfFault()
{
  if (pololuDriver.getM1Fault())
  {
    pololuDriver.disableDrivers();
    delay(1);
    Serial1.println("e: M1 fault");
  }
  if (pololuDriver.getM2Fault())
  {
    pololuDriver.disableDrivers();
    delay(1);
    Serial1.println("e: M2 fault");
  }
}