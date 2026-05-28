#include <LiquidCrystal.h>
#include <Stepper.h>
#include <HX711.h>
#include <Wire.h>
#define number_of_subjects  50

LiquidCrystal lcd(6, 7, 8, 9, 10, 11);
HX711 LoadCell;
char tag[22];
String tags_array[number_of_subjects] = {"041A9DB979", "041A9C89B3", "041A9C7958", "0419A8212D",
"0417CA5FDE", "041A9DBD90", "0419A86ECB", "0419A8218D", "0417CA97FA", "0419A8701C", "041A9D7BE0","0419A822D2", "041A9DBDF9", "041A9DB349", "0419A81BFB", "041A9D86C5",
"041AE65516", "041AE648FE", "041AE64A89", "041AE6375F", "041AE66B73", "041AE65A2F", "041AE62FB2", "041AE66483", "041AE65969",
"041AE63F9A","041AE6404F","041AE63FB7","041AE63E2D","041AE658D2","041AE63C1D","041AE6462F","041AE663ED","041AE63405", "041AE65D09",
"041AE66DCA","041AE63559","041AE64291","041AE6569B","041AE66AE8","041AE66B84","041AE65690","041AE64344","041AE64919"};
String subjects_array[number_of_subjects] = {"manual", "T1", "T2", "T3",
"A41", "A42", "A43", "A44", "A45", "A46", "A47", "A48", "A49", "A50", "A51", "A52",
"A53", "A54", "A55", "A56", "A58", "A60", "A61", "A62", "A63",
"A64","A65", "A66", "A67","A68", "A69", "A70", "A71", "A72","A73",
"A74","A75","A76","A77","A78","A79","A80","A81","A82"};


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
  lcd.clear();
  lcd.setCursor(0, 0);
  for (int counter = 0; counter < 10; counter++)
  {
    lcd.print(tag[counter]);
  }

  int position = -1;
  for (int counter = 0; counter < number_of_subjects; counter++)
  {
    for (int counter2 = 0; counter2 < 10; counter2++)
    {
      Serial.print(counter);
      Serial.print(counter2);
      Serial.print(tag[counter2]);
      Serial.print(" ");
      if (tag[counter2] == tags_array[counter].charAt(counter2)) {
        position = counter;
      }
      else 
      {
        position = -1;
        Serial.print("   ");
        break;
      }
    }
    if (position >= 0)
    {
      break;
    }
  }

  if (position >= 0) {
    //Serial.print(position);
    lcd.setCursor(11, 0);
    int length_name = subjects_array[position].length();
    for (int counter = 0; counter < length_name; counter++)
    {
      lcd.print(subjects_array[position].charAt(counter));
    }
  }
}



void setup()
{
  Serial.begin(9600);
  Serial1.begin(9600);
  lcd.begin(16, 2);
  LoadCell.begin(2, 3); // start connection to HX711
  LoadCell.set_scale(1062); // calibration factor for load cell => strongly dependent on your individual setup 
  LoadCell.tare();
}



void loop()
{
    
  if (Serial1.available() > 0)
  {
    delay(30);
    if (Serial1.peek() != 2)
    {
      while(Serial1.available())
      {
        Serial1.read();
      }
    }
    else
    {
      fetchTagData1(tag);
      while(Serial.available())
      {
        Serial.read();
      }
      printTag(tag);

      LoadCell.tare();

      while(Serial.available())
      {
        Serial.read();
      }
    }
  }
  
  float result = LoadCell.get_units(5);
  lcd.setCursor(0, 1);
  lcd.print(result);
  delay(1000);
 
}
