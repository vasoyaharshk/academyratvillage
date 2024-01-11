#include <LiquidCrystal.h>
LiquidCrystal lcd (11,12,5,4,3,2);
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"
 
Adafruit_SHT31 sht31 = Adafruit_SHT31();
byte degree[8] =
{
0b00011,
0b00011,
0b00000,
0b00000,
0b00000,
0b00000,
0b00000,
0b00000
};
 
void setup() {
Serial.begin(9600);
lcd.begin(16,2);
lcd.createChar(1, degree);
 
while (!Serial)
delay(10); // will pause Zero, Leonardo, etc until serial console opens
 
Serial.println("SHT31 test");
if (! sht31.begin(0x44)) { // Set to 0x45 for alternate i2c addr
Serial.println("Couldn't find SHT31");
while (1) delay(1);
}
}
 
void loop() {
float t = sht31.readTemperature();
float h = sht31.readHumidity();
 
if (! isnan(t)) { // check if 'is not a number'
Serial.print("Temp *C = "); Serial.println(t);
lcd.print("Temp = ");
lcd.print(t);
lcd.write(1);
lcd.print("C");
} else {
Serial.println("Failed to read temperature");
lcd.print("Temperature Error");
}
 
if (! isnan(h)) { // check if 'is not a number'
Serial.print("Hum. % = "); Serial.println(h);
lcd.setCursor (0,1);
lcd.print("Hum. = ");
lcd.print(h);
lcd.print(" %");
} else {
Serial.println("Failed to read humidity");
lcd.setCursor (0,1);
lcd.print("Humidity Error");
}
Serial.println();
delay(1000);
lcd.clear();
}
