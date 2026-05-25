#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 27
#define NUM_READERS 4
#define BUTTON_PIN 17


// Orden: lector 1, lector 2, lector 3, lector 4.
byte SS_PINS[NUM_READERS] = {2, 15, 21, 4};

MFRC522 readers[NUM_READERS] = {
  MFRC522(SS_PINS[0], RST_PIN),
  MFRC522(SS_PINS[1], RST_PIN),
  MFRC522(SS_PINS[2], RST_PIN),
  MFRC522(SS_PINS[3], RST_PIN),
};

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  SPI.begin(); // Usa pines SPI por defecto: SCK=18, MISO=19, MOSI=23 en ESP32

  Serial.println("=== Test RC522 x4 ===");

  for (byte i = 0; i < NUM_READERS; i++) {
    readers[i].PCD_Init();
    delay(100);

    Serial.print("Lector ");
    Serial.print(i + 1);
    Serial.print(" | SS/SDA GPIO ");
    Serial.print(SS_PINS[i]);
    Serial.print(" | Version RC522: 0x");

    byte v = readers[i].PCD_ReadRegister(readers[i].VersionReg);
    Serial.println(v, HEX);

    if (v == 0x00 || v == 0xFF) {
      Serial.print("ERROR: No se detecta el lector ");
      Serial.print(i + 1);
      Serial.println(". Revisa cableado, SDA/SS, GND, 3.3V, SCK, MISO, MOSI y RST.");
    } else {
      Serial.print("Lector ");
      Serial.print(i + 1);
      Serial.println(" detectado correctamente.");
    }
  }

  Serial.println("Acerca un tag NFC a cualquier lector o presiona el boton...");
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
  Serial.println("BOTON PRESIONADO");
  delay(300);
  }

  for (byte i = 0; i < NUM_READERS; i++) {
    if (!readers[i].PICC_IsNewCardPresent()) {
      continue;
    }

    if (!readers[i].PICC_ReadCardSerial()) {
      continue;
    }

    Serial.print("Lector ");
    Serial.print(i + 1);
    Serial.print(" detecto tag! UID:");

    for (byte j = 0; j < readers[i].uid.size; j++) {
      Serial.print(readers[i].uid.uidByte[j] < 0x10 ? " 0" : " ");
      Serial.print(readers[i].uid.uidByte[j], HEX);
    }

    Serial.println();

    readers[i].PICC_HaltA();
    readers[i].PCD_StopCrypto1();

    delay(300);
  }
}