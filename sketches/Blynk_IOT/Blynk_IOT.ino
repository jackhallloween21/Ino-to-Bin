#define BLYNK_TEMPLATE_ID "TMPL3OSsDG_PH"
#define BLYNK_TEMPLATE_NAME "NodeMCU"
#define BLYNK_AUTH_TOKEN "O7pZhZrXo4SN3ukfZhKRwXXSCB-cA0kf"
#define BLYNK_FIRMWARE_VERSION "0.1.1"

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <DHT.h>
#include <ESP8266HTTPClient.h>

// Your WiFi credentials
char ssid[] = "TonyStarkFiber_2.4";
char pass[] = "Aditya007";
char auth[] = BLYNK_AUTH_TOKEN;

#define BLYNK_PRINT Serial
#define DHTTYPE DHT11
#define DHTPIN D4     // GPIO2
#define relayPin D5   // GPIO14
const int redPin = D3;   // GPIO0
const int greenPin = D1; // GPIO5
const int bluePin = D2;  // GPIO4

const int buttonPin = D6; // Pin connected to the push button (GPIO12)
int sensor_pin = A0;      // Soil Sensor input at Analog PIN A0

bool relayState = LOW;        // Variable to store current state of the relay
unsigned long lastDebounceTime = 0; 
unsigned long debounceDelay = 50; 

BlynkTimer timer;
DHT dht(DHTPIN, DHTTYPE);

// CONFIRMED common-anode LEDs: pin LOW = ON, pin HIGH = OFF.
void writeRGBChannel(int pin, int brightness) {
  brightness = constrain(brightness, 0, 255);
  analogWrite(pin, 255 - brightness);
}

void setup() {
  Serial.begin(9600);
  dht.begin(); 
  
  // Blynk.begin handles Wi-Fi connection and Blynk connection blocking-style
  Blynk.begin(auth, ssid, pass);

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(sensor_pin, INPUT);

  // Initialize PWM for ESP8266
  analogWriteRange(255); 
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(relayPin, OUTPUT);

  digitalWrite(greenPin, HIGH); // Common anode: HIGH turns it OFF
  digitalWrite(bluePin, HIGH);  
  digitalWrite(redPin, HIGH);    
  digitalWrite(relayPin, LOW);  // Relay OFF initially

  timer.setInterval(1000L, sendSensor);
  timer.setInterval(1000L, sendUptime);
}

// Blynk Virtual Pin handler for Relay switch from app
BLYNK_WRITE(V5) {
  int state = param.asInt();
  relayState = state;
  digitalWrite(relayPin, relayState ? HIGH : LOW);
}

// RGB LED Virtual Pins
BLYNK_WRITE(V2) { // Red
  int redValue = param.asInt();
  writeRGBChannel(redPin, redValue); 
}

BLYNK_WRITE(V1) { // Green
  int greenValue = param.asInt();
  writeRGBChannel(greenPin, greenValue); 
}

BLYNK_WRITE(V0) { // Blue
  int blueValue = param.asInt();
  writeRGBChannel(bluePin, blueValue); 
}

void sendSensor() {
  float h = dht.readHumidity();
  float t = dht.readTemperature(); 
  int out_val = analogRead(sensor_pin);
  out_val = map(out_val, 550, 10, 0, 100); // Adjust calibration mapping values if needed
  
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  Blynk.virtualWrite(V8, out_val); // Soil moisture
  Blynk.virtualWrite(V6, h);       // Humidity
  Blynk.virtualWrite(V3, t);       // Temperature
}

void sendUptime() {
  unsigned long millisec = millis();
  unsigned long sec = millisec / 1000;
  unsigned long min = sec / 60;
  unsigned long hr = min / 60;

  sec = sec % 60;
  min = min % 60;
  hr = hr % 24;

  String uptimeString = String(hr) + "h " + String(min) + "m " + String(sec) + "s";
  Blynk.virtualWrite(V4, uptimeString); 
}  

void swtch() {
  int reading = digitalRead(buttonPin); 
  if (reading == LOW && (millis() - lastDebounceTime) > debounceDelay) {  
    lastDebounceTime = millis();
    relayState = !relayState; // Toggle state
    digitalWrite(relayPin, relayState);  
    Serial.println(relayState ? "Relay ON" : "Relay OFF"); 
    
    // Sync state back to Blynk app virtual pin V5 so the toggle button updates visually
    Blynk.virtualWrite(V5, relayState);
  }
}

void loop() {
  Blynk.run();
  timer.run();
  swtch(); // Enabled physical button check
}
