#include <HX711.h>
#include <Wire.h>
#include <Servo.h>
#include <Arduino.h>
#include "Adafruit_SHT31.h"

// DOOR 3 STEPPER WITH LIMIT SWITCH FAILSAFE START
#include <TMCStepper.h>
#include <SoftwareSerial.h>

#define DOOR3_STEP_PIN 6
#define DOOR3_DIR_PIN 7
#define DOOR3_R_SENSE 0.11

#define DOOR3_LIMIT_TOP_PIN 24
#define DOOR3_LIMIT_BOTTOM_PIN 25

#define DOOR3_UART_RX_PIN 14

// Door 3 uses only Arduino pin 10 for the TMC UART line.
// SoftwareSerial still needs RX and TX arguments, so the same pin is used for both.
SoftwareSerial door3TMCSerial(DOOR3_UART_RX_PIN, DOOR3_UART_RX_PIN);
TMC2208Stepper door3Driver(&door3TMCSerial, DOOR3_R_SENSE);

float door3_open_rotations = 5.5;
float door3_close_rotations = 5.5;
float door3_limit_reverse_rotations = 0.0;
const long door3_stepsPerRotation = 3200;

const int door3_minDelay = 300;
const int door3_startDelay = 1200;
const int door3_rampPercent = 2;

bool door3_moving = false;
bool door3_stopRequested = false;
bool door3_limitHit = false;

bool door3_lastTopLimitState = HIGH;
bool door3_lastBottomLimitState = HIGH;

enum Door3PositionState {
  DOOR3_UNKNOWN,
  DOOR3_AT_TOP,
  DOOR3_AT_BOTTOM,
  DOOR3_MOVING_UP,
  DOOR3_MOVING_DOWN,
  DOOR3_STOPPED_MIDWAY
};

Door3PositionState door3_state = DOOR3_UNKNOWN;

bool isDoor3TopLimitTriggered()
{
  return digitalRead(DOOR3_LIMIT_TOP_PIN) == LOW;
}

bool isDoor3BottomLimitTriggered()
{
  return digitalRead(DOOR3_LIMIT_BOTTOM_PIN) == LOW;
}

void updateDoor3StateFromLimits()
{
  bool top = isDoor3TopLimitTriggered();
  bool bottom = isDoor3BottomLimitTriggered();

  if (top && !bottom) {
    door3_state = DOOR3_AT_TOP;
  }
  else if (bottom && !top) {
    door3_state = DOOR3_AT_BOTTOM;
  }
}

void monitorDoor3LimitSwitches()
{
  bool topState = digitalRead(DOOR3_LIMIT_TOP_PIN);
  bool bottomState = digitalRead(DOOR3_LIMIT_BOTTOM_PIN);

  if (topState != door3_lastTopLimitState) {
    if (topState == LOW) {
      Serial.println("D3:TOP_LIMIT_SWITCH_PRESSED");
    }
    else {
      Serial.println("D3:TOP_LIMIT_SWITCH_RELEASED");
    }

    door3_lastTopLimitState = topState;
  }

  if (bottomState != door3_lastBottomLimitState) {
    if (bottomState == LOW) {
      Serial.println("D3:BOTTOM_LIMIT_SWITCH_PRESSED");
    }
    else {
      Serial.println("D3:BOTTOM_LIMIT_SWITCH_RELEASED");
    }

    door3_lastBottomLimitState = bottomState;
  }

  updateDoor3StateFromLimits();
}


// DOOR 3 STEPPER WITH LIMIT SWITCH FAILSAFE END

// servo1
#define TIMEOPEN1 150
#define TIMECLOSE1 350
#define SERVOPIN1 4

// servo2
#define TIMEOPEN2 200
#define TIMECLOSE2 200
#define SERVOPIN2 9

// always 90 degrees from open to close

// academy1
#define ANGLEOPEN1 90 //was 80    - 0
#define ANGLECLOSE1 5// was 28   - 1
#define ANGLEOPEN2 130 // was 5   - 2
#define ANGLECLOSE2 168 //was 49     - 3
#define ANGLESEMICLOSE2 1 //ratvillage02: what is this?

// scale
#define CELL1 2   
#define CELL2 3  
#define CELLCALIBRATION 1062 // calibration factor for load cell => strongly dependent on your individual setup
HX711 LoadCell;
bool scaleOn = false;

// temperature sensor
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// led
#define LED 12


// servo1
Servo myservo1;
int steps1 = abs(ANGLEOPEN1 - ANGLECLOSE1);
int delayopen1 = TIMEOPEN1 / steps1;
int delayclose1 = TIMECLOSE1 / steps1;
int state1 = 0;

// servo2
Servo myservo2;
int steps2 = abs(ANGLEOPEN2 - ANGLECLOSE2);
int delayopen2 = TIMEOPEN2 / steps2;
int delayclose2 = TIMECLOSE2 / steps2;
int state2 = 0;

// rfid
char tag[10];

// DOOR 3 STEPPER WITH LIMIT SWITCH FAILSAFE START
void setupDoor3Stepper()
{
  pinMode(DOOR3_STEP_PIN, OUTPUT);
  pinMode(DOOR3_DIR_PIN, OUTPUT);
  pinMode(DOOR3_LIMIT_TOP_PIN, INPUT_PULLUP);
  pinMode(DOOR3_LIMIT_BOTTOM_PIN, INPUT_PULLUP);

  door3_lastTopLimitState = digitalRead(DOOR3_LIMIT_TOP_PIN);
  door3_lastBottomLimitState = digitalRead(DOOR3_LIMIT_BOTTOM_PIN);

  door3TMCSerial.begin(115200);

  door3Driver.begin();
  door3Driver.rms_current(900);
  door3Driver.microsteps(16);

  // quiet mode
  door3Driver.en_spreadCycle(false);
  door3Driver.pwm_autoscale(true);

  updateDoor3StateFromLimits();

  if (door3_state == DOOR3_AT_TOP) {
    Serial.println("D3:SETUP_TOP_LIMIT_TRIGGERED");
  }
  else if (door3_state == DOOR3_AT_BOTTOM) {
    Serial.println("D3:SETUP_BOTTOM_LIMIT_TRIGGERED");
  }
  else {
    Serial.println("D3:SETUP_POSITION_UNKNOWN");
  }
}

void moveDoor3StepsOnly(bool directionUp, float rotations)
{
  long totalSteps = (long)(rotations * door3_stepsPerRotation);
  long rampSteps = totalSteps * door3_rampPercent / 100;

  digitalWrite(DOOR3_DIR_PIN, directionUp ? LOW : HIGH);
  delayMicroseconds(50);

  int currentDelay = door3_startDelay;

  for (long step = 0; step < totalSteps; step++) {
    monitorDoor3LimitSwitches();

    if (door3_stopRequested) {
      Serial.println("D3:BACKOFF_STOP_REQUESTED");
      break;
    }

    if (directionUp && isDoor3TopLimitTriggered()) {
      Serial.println("D3:BACKOFF_STOPPED_TOP_LIMIT");
      break;
    }

    if (!directionUp && isDoor3BottomLimitTriggered()) {
      Serial.println("D3:BACKOFF_STOPPED_BOTTOM_LIMIT");
      break;
    }

    if (step < rampSteps) {
      currentDelay -= 20;
      if (currentDelay < door3_minDelay) currentDelay = door3_minDelay;
    }
    else if (step > totalSteps - rampSteps) {
      currentDelay += 20;
      if (currentDelay > door3_startDelay) currentDelay = door3_startDelay;
    }
    else {
      currentDelay = door3_minDelay;
    }

    digitalWrite(DOOR3_STEP_PIN, HIGH);
    delayMicroseconds(2);
    digitalWrite(DOOR3_STEP_PIN, LOW);
    delayMicroseconds(currentDelay);
  }
}

void backOffDoor3FromLimit(bool hitTopLimit)
{
  bool reverseDirectionUp = !hitTopLimit;

  if (hitTopLimit) {
    Serial.println("D3:BACKOFF_FROM_TOP_START");
  }
  else {
    Serial.println("D3:BACKOFF_FROM_BOTTOM_START");
  }

  moveDoor3StepsOnly(reverseDirectionUp, door3_limit_reverse_rotations);

  door3_state = DOOR3_STOPPED_MIDWAY;

  if (hitTopLimit) {
    Serial.println("D3:BACKOFF_FROM_TOP_COMPLETE");
  }
  else {
    Serial.println("D3:BACKOFF_FROM_BOTTOM_COMPLETE");
  }
}

void moveDoor3Stepper(bool directionUp, float rotations)
{
  door3_moving = true;
  door3_stopRequested = false;
  door3_limitHit = false;

  long totalSteps = (long)(rotations * door3_stepsPerRotation);
  long rampSteps = totalSteps * door3_rampPercent / 100;

  digitalWrite(DOOR3_DIR_PIN, directionUp ? LOW : HIGH);
  delayMicroseconds(50);

  door3_state = directionUp ? DOOR3_MOVING_UP : DOOR3_MOVING_DOWN;

  if (directionUp) {
    Serial.println("D3:CLOSING");
  }
  else {
    Serial.println("D3:OPENING");
  }

  int currentDelay = door3_startDelay;

  for (long step = 0; step < totalSteps; step++) {
    monitorDoor3LimitSwitches();

    if (door3_stopRequested) {
      door3_state = DOOR3_STOPPED_MIDWAY;
      Serial.println("D3:STOP_REQUESTED");
      break;
    }

    if (directionUp && isDoor3TopLimitTriggered()) {
      door3_state = DOOR3_AT_TOP;
      door3_limitHit = true;
      Serial.println("D3:TOP_LIMIT_HIT");
      backOffDoor3FromLimit(true);
      break;
    }

    if (!directionUp && isDoor3BottomLimitTriggered()) {
      door3_state = DOOR3_AT_BOTTOM;
      door3_limitHit = true;
      Serial.println("D3:BOTTOM_LIMIT_HIT");
      backOffDoor3FromLimit(false);
      break;
    }

    if (step < rampSteps) {
      currentDelay -= 20;
      if (currentDelay < door3_minDelay) currentDelay = door3_minDelay;
    }
    else if (step > totalSteps - rampSteps) {
      currentDelay += 20;
      if (currentDelay > door3_startDelay) currentDelay = door3_startDelay;
    }
    else {
      currentDelay = door3_minDelay;
    }

    digitalWrite(DOOR3_STEP_PIN, HIGH);
    delayMicroseconds(2);
    digitalWrite(DOOR3_STEP_PIN, LOW);
    delayMicroseconds(currentDelay);
  }

  if (!door3_stopRequested && !door3_limitHit) {
    door3_state = directionUp ? DOOR3_AT_TOP : DOOR3_AT_BOTTOM;

    if (directionUp) {
      Serial.println("D3:CLOSE_COMPLETE_ROTATIONS");
    }
    else {
      Serial.println("D3:OPEN_COMPLETE_ROTATIONS");
    }
  }

  door3_moving = false;
}

void openDoor3()
{
  updateDoor3StateFromLimits();

  if (door3_moving) {
    Serial.println("D3:OPEN_IGNORED_ALREADY_MOVING");
    return;
  }

  if (isDoor3BottomLimitTriggered() || door3_state == DOOR3_AT_BOTTOM) {
    door3_state = DOOR3_AT_BOTTOM;
    Serial.println("D3:OPEN_IGNORED_ALREADY_BOTTOM");
    return;
  }

  moveDoor3Stepper(false, door3_open_rotations);
}

void closeDoor3()
{
  updateDoor3StateFromLimits();

  if (door3_moving) {
    Serial.println("D3:CLOSE_IGNORED_ALREADY_MOVING");
    return;
  }

  if (isDoor3TopLimitTriggered() || door3_state == DOOR3_AT_TOP) {
    door3_state = DOOR3_AT_TOP;
    Serial.println("D3:CLOSE_IGNORED_ALREADY_TOP");
    return;
  }

  moveDoor3Stepper(true, door3_close_rotations);
}

// DOOR 3 STEPPER WITH LIMIT SWITCH FAILSAFE END


void openDoor1()
{
  if (state1 != 1) {
    state1 = 1;
    myservo1.attach(SERVOPIN1);

    if (ANGLECLOSE1 >= ANGLEOPEN1) {
      for (int pos = ANGLECLOSE1; pos >= ANGLEOPEN1; pos -= 1) {
        myservo1.write(pos);
        delay(delayopen1);
      }
    } else {
      for (int pos = ANGLECLOSE1; pos <= ANGLEOPEN1; pos += 1) {
        myservo1.write(pos);
        delay(delayopen1);
      }
    }
    myservo1.detach();
  }
}

void closeDoor1()
{
  if (state1 != 2) {
    state1 = 2;
    myservo1.attach(SERVOPIN1);

    if (ANGLEOPEN1 >= ANGLECLOSE1) {
      for (int pos = ANGLEOPEN1; pos >= ANGLECLOSE1; pos -= 1) {
        myservo1.write(pos);
        delay(delayclose1);
      }
    } else {
      for (int pos = ANGLEOPEN1; pos <= ANGLECLOSE1; pos += 1) {
        myservo1.write(pos);
        delay(delayclose1);
      }
    }
    myservo1.detach();
  }
}

void openDoor2()
{
  if (state2 != 1) {
    state2 = 1;
    myservo2.attach(SERVOPIN2);

    if (ANGLECLOSE2 >= ANGLEOPEN2) {
      for (int pos = ANGLECLOSE2; pos >= ANGLEOPEN2; pos -= 1) {
        myservo2.write(pos);
        delay(delayopen2);
      }
    } else {
      for (int pos = ANGLECLOSE2; pos <= ANGLEOPEN2; pos += 1) {
        myservo2.write(pos);
        delay(delayopen2);
      }
    }
    myservo2.detach();
  }
}

void closeDoor2()
{
  if (state2 != 2) {
    state2 = 2;
    myservo2.attach(SERVOPIN2);

    if (ANGLEOPEN2 >= ANGLECLOSE2) {
      for (int pos = ANGLEOPEN2; pos >= ANGLECLOSE2; pos -= 1) {
        myservo2.write(pos);
        delay(delayclose2);
      }
    } else {
      for (int pos = ANGLEOPEN2; pos <= ANGLECLOSE2; pos += 1) {
        myservo2.write(pos);
        delay(delayclose2);
      }
    }
    myservo2.detach();
  }
}

void noiseDoor2()
{

  state2 = 0;
  myservo2.attach(SERVOPIN2);

  if (ANGLEOPEN2 >= ANGLESEMICLOSE2) {
    for (int pos = ANGLEOPEN2; pos >= ANGLESEMICLOSE2; pos -= 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  } else {
    for (int pos = ANGLEOPEN2; pos <= ANGLESEMICLOSE2; pos += 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  }

  if (ANGLESEMICLOSE2 >= ANGLEOPEN2) {
    for (int pos = ANGLESEMICLOSE2; pos >= ANGLEOPEN2; pos -= 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  } else {
    for (int pos = ANGLESEMICLOSE2; pos <= ANGLEOPEN2; pos += 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  }

  if (ANGLEOPEN2 >= ANGLESEMICLOSE2) {
    for (int pos = ANGLEOPEN2; pos >= ANGLESEMICLOSE2; pos -= 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  } else {
    for (int pos = ANGLEOPEN2; pos <= ANGLESEMICLOSE2; pos += 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  }

  if (ANGLESEMICLOSE2 >= ANGLEOPEN2) {
    for (int pos = ANGLESEMICLOSE2; pos >= ANGLEOPEN2; pos -= 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  } else {
    for (int pos = ANGLESEMICLOSE2; pos <= ANGLEOPEN2; pos += 1) {
      myservo2.write(pos);
      delay(delayclose2);
    }
  }
  myservo2.detach();

}


void turnLedOn()
{
  digitalWrite(LED, HIGH);
  LoadCell.tare();
  scaleOn = false;
}

void turnLedOff()
{
  digitalWrite(LED, LOW);
  LoadCell.tare();
}




void tempAndScale()
{
  float t = sht31.readTemperature();
  float h = sht31.readHumidity();
  Serial.print("Temperature;"); Serial.print(t); Serial.print("\t");
  Serial.print("Humidity; "); Serial.print(h);
  
  LoadCell.tare();
  scaleOn = true;
}



void getTemperature()
{
  float t = sht31.readTemperature();
  float h = sht31.readHumidity();
  
  Serial.print("Temperature; "); 
  Serial.print(t); 
  Serial.print("H ");
  Serial.print(h);
}



void tareScale()
{
  LoadCell.tare();
  scaleOn = true;
}



void getWeight()
{
  float result = LoadCell.get_units(5);
  Serial.print("Weight*");
  Serial.print(result);
}




void fetchTagData1(char tempTag[])
{
  Serial1.read();

  for (int counter = 0; counter < 10; counter++)
  {
    tempTag[counter] = Serial1.read();
  }

  Serial1.read();
  Serial1.read();
  Serial1.read();
  Serial1.read();
}

void printTag(char tag[])
{
  for (int counter = 0; counter < 10; counter++)
  {
    Serial.print(tag[counter]);
  }
}










void setup()
{
  Serial.begin(9600);
  Serial1.begin(9600);
  sht31.begin(0x44);

  pinMode(LED, OUTPUT);

  LoadCell.begin(CELL1, CELL2); // start connection to HX711
  LoadCell.set_scale(CELLCALIBRATION);
  LoadCell.tare();

  setupDoor3Stepper();

  tempAndScale();
}



void serialEvent()
{
  while (Serial.available())
  {
    char ch = Serial.read();
    Serial.flush();

    if      (ch == '0') { openDoor1(); }
    else if (ch == '1') { closeDoor1(); }

    else if (ch == '2') { openDoor2(); }     // only Door 2
    else if (ch == '3') { closeDoor2(); }    // only Door 2

    else if (ch == 'x') { openDoor3(); }     // only Door 3
    else if (ch == 'y') { closeDoor3(); }    // only Door 3

    else if (ch == '4') { closeDoor1(); openDoor2(); }
    else if (ch == '5') { closeDoor2(); openDoor1(); }

    else if (ch == '6') { turnLedOn(); }
    else if (ch == '7') { turnLedOff(); }

    else if (ch == '8') { tempAndScale(); }
    else if (ch == '9') { getTemperature(); }

    else if (ch == 'a') { tareScale(); }
    else if (ch == 'b') { getWeight(); }
    else if (ch == 'c') { noiseDoor2(); }
  }
}



void loop()
{
  monitorDoor3LimitSwitches();

  if (Serial1.available() > 0)
  {
    delay(30);
    if (Serial1.peek() != 2)
    {
      while (Serial1.available())
      {
        Serial1.read();
      }
    }
    else
    {
      fetchTagData1(tag);
      while (Serial.available())
      {
        Serial.read();
      }
      printTag(tag);

      while (Serial.available())
      {
        Serial.read();
      }
    }
  }
  if (scaleOn) {
    float result = LoadCell.get_units(5);
    if (result > 4)
    {
      Serial.print("Weight:");
      Serial.print(result);
    }
  }
}
