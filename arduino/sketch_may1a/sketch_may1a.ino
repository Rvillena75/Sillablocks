#include <SPI.h>
#include <MFRC522.h>

// Wiring for Arduino Uno + MFRC522/RC522 13.56 MHz reader:
// SDA/SS -> D10, SCK -> D13, MOSI -> D11, MISO -> D12, RST -> D9
// Power the reader from 3.3V, not 5V.
const byte SS_PIN = 10;
const byte RST_PIN = 9;
const unsigned long READ_COOLDOWN_MS = 700;

MFRC522 rfid(SS_PIN, RST_PIN);

String lastUid = "";
unsigned long lastReadAt = 0;

String uidToText(MFRC522::Uid *uid) {
  String text = "";
  for (byte i = 0; i < uid->size; i++) {
    if (uid->uidByte[i] < 0x10) {
      text += "0";
    }
    text += String(uid->uidByte[i], HEX);
  }
  text.toUpperCase();
  return text;
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for Serial on boards that need it.
  }

  SPI.begin();
  rfid.PCD_Init();
  Serial.println("SILABLOCKS_RFID_READY");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  String uid = uidToText(&rfid.uid);
  unsigned long now = millis();

  if (uid != lastUid || now - lastReadAt >= READ_COOLDOWN_MS) {
    Serial.println(uid);
    lastUid = uid;
    lastReadAt = now;
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
