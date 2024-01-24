// Code for servo motor, incudes buzzer sounds

#include "ArCOM.h" // Import serial communication wrapper
#include <Servo.h>

#define ANGLEMAX 97 //Closed position (lower number door down, upper door up)
#define ANGLEMIN 65 // Opened position
#define TIMEOPEN 200
#define TIMECLOSE 200 //400
#define SERVOPIN 8
#define PIEZOPIN 10

unsigned long FirmwareVersion = 1;
ArCOM Serial1COM(Serial1); // Wrap Serial5 (equivalent to Serial on Arduino Leonardo and Serial1 on Arduino Due)
byte opCode = 0;
Servo myservo;

int steps = ANGLEMAX - ANGLEMIN;
int delayopen = TIMEOPEN / steps;
int delayclose = TIMECLOSE / steps;
int state = 0;


void setup()
{
  Serial1.begin(1312500);// Initialize Serial1 with a rate of 1312500 (Bpod rate)
  SerialUSB.begin(9600);
}

void loop()
{
  if (Serial1COM.available()) {
    opCode = Serial1COM.readByte();
    SerialUSB.println(opCode);

    switch(opCode) {
      case 11: // open
        if(state != 1) {
          state = 1;
          myservo.attach(SERVOPIN);
          for(int pos = ANGLEMAX; pos >= ANGLEMIN; pos -= 1) {
            myservo.write(pos);
            delay(delayopen);
          }
          myservo.detach();
        }
        break;

      case 12: // close
        if(state != 2) {
          state = 2;
          myservo.attach(SERVOPIN);
          for(int pos = ANGLEMIN; pos <= ANGLEMAX; pos += 1) {
            myservo.write(pos);
            delay(delayclose);
          }
          myservo.detach();
        }
        break;
        
      case 13: // high pitch never ends
        tone(PIEZOPIN, 12000);
        break;

      case 14: // low pitch 250 ms
        tone(PIEZOPIN, 4000);
        break;

      case 15: // off
        noTone(PIEZOPIN);
        break;
    }
  }
}

void returnModuleInfo() {
  Serial1COM.writeByte(65); // Acknowledge
  Serial1COM.writeUint32(FirmwareVersion); // 4-byte firmware version
  //Serial1COM.writeByte(sizeof(moduleName)-1); // Length of module name
  //Serial1COM.writeCharArray(moduleName, sizeof(moduleName)-1); // Module name
  Serial1COM.writeByte(0); // 1 if more info follows, 0 if not
}
