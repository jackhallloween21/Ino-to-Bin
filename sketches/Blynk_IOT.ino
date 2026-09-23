#define BLYNK_TEMPLATE_ID "TMPL3OSsDG_PH"
#define BLYNK_TEMPLATE_NAME "NodeMCU"
#define BLYNK_AUTH_TOKEN "O7pZhZrXo4SN3ukfZhKRwXXSCB-cA0kf"
#define BLYNK_FIRMWARE_VERSION "0.1.1"

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <DHT.h>

// #include  <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
// Your WiFi credentials.
// Set password to "" for open networks.
char ssid[] = "TonyStarkFiber_2.4";
char pass[] = "Aditya007";
char auth[] = BLYNK_AUTH_TOKEN;

#define BLYNK_PRINT Serial
#define DHTTYPE DHT11
#define DHTPIN D4
#define relayPin D5
const int redPin = D3;
const int greenPin = D1;
const int bluePin = D2;

// Define the PWM frequency and resolution
const int pwmFrequency = 1000;
const int pwmResolution = 8;


const int buttonPin = D6; // Pin connected to the push button
int sensor_pin = A0; // Soil Sensor input at Analog PIN A0

bool relayState = LOW;    // Variable to store the current state of the relay (false = OFF, true = ON)
bool lastButtonState = HIGH; // Variable to store the last state of the button
unsigned long lastDebounceTime = 0; // Variable to store the last debounce time
unsigned long debounceDelay = 50; // Debounce time in milliseconds

BlynkTimer timer;
DHT dht(DHTPIN, DHTTYPE);

// CONFIRMED common-anode LEDs: pin LOW = ON, pin HIGH = OFF.
// This inverts so the value coming from Blynk behaves intuitively:
// 0 = off, 255 = full brightness.
void writeRGBChannel(int pin, int brightness) {
  brightness = constrain(brightness, 0, 255);
  analogWrite(pin, 255 - brightness);
}

void setup() {

  Serial.begin(9600);
  dht.begin(); // Initialize the DHT sensor here
  Blynk.config(auth);
  Blynk.begin(auth, ssid, pass);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(sensor_pin, INPUT);

  // Initialize PWM for each pin
  analogWriteRange(255); // Set the PWM range for ESP8266
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  pinMode(D1, OUTPUT); // Redundant, already defined as greenPin
  pinMode(D2, OUTPUT); // Redundant, already defined as bluePin
  pinMode(D3, OUTPUT); // Redundant, already defined as redPin
  pinMode(D5, OUTPUT);
  digitalWrite(greenPin, HIGH); // Common anode: HIGH turns it OFF
  digitalWrite(bluePin, HIGH);  // Common anode: HIGH turns it OFF
  digitalWrite(redPin, HIGH);   // Common anode: HIGH turns it OFF
  digitalWrite(D5, LOW); // relay - LOW might turn it ON depending on your relay module
  timer.setInterval(1000L, sendSensor);
  // timer.setInterval(1000L, sendUptime);


}

// This function is called every time the Virtual Pin 0 state changes

/* BLYNK_WRITE(V0) //blue
{
  // Set incoming value from pin V0 to a variable
  int value = param.asInt();
  // Update state
value ? digitalWrite(D2, LOW): digitalWrite(D2, HIGH);
}
BLYNK_WRITE(V1) //green
{
  // Set incoming value from pin V0 to a variable
  int value = param.asInt();
  // Update state
value ? digitalWrite(D1, LOW): digitalWrite(D1, HIGH);
}
BLYNK_WRITE(V2) //red
{
  // Set incoming value from pin V0 to a variable
  int value = param.asInt();
  // Update state
value ? digitalWrite(D3, LOW): digitalWrite(D3, HIGH);
}*/

BLYNK_WRITE(V5)
{
  int state = param.asInt();
 if (state == 1) {
   digitalWrite(relayPin, HIGH); // Turn relay on
 } else {
   digitalWrite(relayPin, LOW); // Turn relay off
 }
}


BLYNK_WRITE(V2) { // Red
  int redValue = param.asInt();
  Serial.print("V2 (red) received: "); Serial.println(redValue);
  writeRGBChannel(redPin, redValue); // 0 = off, 255 = full brightness
}

BLYNK_WRITE(V1) { // Green
  int greenValue = param.asInt();
  Serial.print("V1 (green) received: "); Serial.println(greenValue);
  writeRGBChannel(greenPin, greenValue); // 0 = off, 255 = full brightness
}

BLYNK_WRITE(V0) { // Blue
  int blueValue = param.asInt();
  Serial.print("V0 (blue) received: "); Serial.println(blueValue);
  writeRGBChannel(bluePin, blueValue); // 0 = off, 255 = full brightness
}

void sendSensor()
{
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // or dht.readTemperature(true) for Fahrenheit
    int out_val= analogRead(sensor_pin);
    out_val = map(out_val,550,10,0,100);
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  Serial.println(h);
  Serial.println(t);
  Blynk.virtualWrite(V8, out_val); //moisture
  Blynk.virtualWrite(V6, h);  //V4 is for Humidity
  Blynk.virtualWrite(V3, t);  //V3 is for Temperature
}
/* void sendUptime()
{
  unsigned long millisec = millis();
  unsigned long sec = millisec / 1000;
  unsigned long min = sec / 60;
  unsigned long hr = min / 60;

  sec = sec % 60;
  min = min % 60;
  hr = hr % 24;

  String uptimeString = String(hr) + "h " + String(min) + "m " + String(sec) + "s";

  Blynk.virtualWrite(V7, uptimeString); // Send uptime to Blynk app
} */
void swtch()
{
    int reading = digitalRead(buttonPin); // Read the state of the button
 if (reading == LOW) {  // If the button is pressed (INPUT_PULLUP means LOW when pressed)
    relayState = !relayState; // Toggle the relay state
        digitalWrite(relayPin, relayState);  // Set the relay to the new state
 // Check if the button state has changed (i.e., a press is detected)
      Serial.println(relayState ? "Relay ON" : "Relay OFF"); // Print the relay state
      delay(500); // Debounce delay
    }
 }
void loop() {
    Blynk.run();
    timer.run();
    //swtch();
}
