#include <Wire.h>
#include "SparkFun_Qwiic_Rfid.h"

#define RFID_ADDR 0x7D // Default I2C address

Qwiic_Rfid myRfid(RFID_ADDR);

String tag;
float scanTime;
int serialInput;

void setup()
{
  // Begin I-squared-C
    Wire.begin();
    Serial.begin(115200);

  if(myRfid.begin())
    Serial.println("Ready to scan some tags!");
  else
    Serial.println("Could not communicate with Qwiic RFID!");

  // Want to clear tags sitting on the Qwiic RFID card?
  //myRfid.clearTags();
}
