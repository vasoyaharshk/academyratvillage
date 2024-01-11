// HX711 circuit wiring
#include <HX711.h>
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;


HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 Demo");
  Serial.println("Initializing the scale");
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale();
  scale.tare();    
}

  void loop() {
    Serial.println("Put known weight on the scale");
    delay(10000);
    Serial.println(scale.get_units(10));
    delay(10000);    
  }