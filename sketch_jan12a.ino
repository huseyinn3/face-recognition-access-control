void setup() {
  // Seri haberleşmeyi başlat
  Serial.begin(115200);
  
  // Dahili LED'i çıkış olarak ayarla (çoğu ESP8266'da GPIO2'de)
  pinMode(LED_BUILTIN, OUTPUT);
  
  delay(1000);
  Serial.println("\n\n");
  Serial.println("=========================");
  Serial.println("ESP8266 Test Başladı!");
  Serial.println("=========================");
}

void loop() {
  // LED'i yak-söndür
  digitalWrite(LED_BUILTIN, LOW);   // LED yanar (LOW aktif)
  Serial.println("LED AÇIK - ESP8266 çalışıyor!");
  delay(1000);
  
  digitalWrite(LED_BUILTIN, HIGH);  // LED söner
  Serial.println("LED KAPALI");
  delay(1000);
  
  // Sistem bilgileri
  Serial.print("Çalışma süresi: ");
  Serial.print(millis() / 1000);
  Serial.println(" saniye");
  Serial.println("---");
}