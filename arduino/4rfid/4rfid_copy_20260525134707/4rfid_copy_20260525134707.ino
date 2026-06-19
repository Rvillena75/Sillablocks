#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 27
#define NUM_READERS 4
#define BUTTON_PIN 17

// Orden: lector 1, lector 2, lector 3, lector 4.
byte SS_PINS[NUM_READERS] = {16, 5, 21, 4};

const unsigned long TAG_REMOVAL_MS = 1500;
const unsigned long BUTTON_DEBOUNCE_MS = 25;
const byte UID_CONFIRMATIONS_REQUIRED = 2;

MFRC522 readers[NUM_READERS] = {
  MFRC522(SS_PINS[0], RST_PIN),
  MFRC522(SS_PINS[1], RST_PIN),
  MFRC522(SS_PINS[2], RST_PIN),
  MFRC522(SS_PINS[3], RST_PIN),
};

// ==========================
// FUNCIONES AUXILIARES
// ==========================

void uidToString(const MFRC522::Uid *uid, char *output, size_t outputSize) {
  const char HEX_DIGITS[] = "0123456789ABCDEF";
  size_t position = 0;

  for (byte i = 0; i < uid->size && position + 2 < outputSize; i++) {
    output[position++] = HEX_DIGITS[(uid->uidByte[i] >> 4) & 0x0F];
    output[position++] = HEX_DIGITS[uid->uidByte[i] & 0x0F];
  }

  output[position] = '\0';
}

bool readPresentTag(MFRC522 &reader, char *uid, size_t uidSize) {
  byte atqa[2];
  byte atqaSize = sizeof(atqa);

  // WUPA detecta tanto tarjetas nuevas (IDLE) como tarjetas que siguen
  // colocadas (HALT). PICC_IsNewCardPresent() solo cubre el primer caso.
  MFRC522::StatusCode status = reader.PICC_WakeupA(atqa, &atqaSize);
  if (status != MFRC522::STATUS_OK && status != MFRC522::STATUS_COLLISION) {
    return false;
  }

  if (!reader.PICC_ReadCardSerial()) {
    return false;
  }

  uidToString(&reader.uid, uid, uidSize);
  // Dejarla en HALT permite que WUPA confirme su presencia en el siguiente ciclo.
  reader.PICC_HaltA();
  reader.PCD_StopCrypto1();
  return uid[0] != '\0';
}

// ==========================
// SETUP
// ==========================

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Todos los lectores comparten SPI. Mantener cada CS en HIGH antes de
  // iniciar el bus evita que un RC522 contienda durante el arranque.
  for (byte i = 0; i < NUM_READERS; i++) {
    pinMode(SS_PINS[i], OUTPUT);
    digitalWrite(SS_PINS[i], HIGH);
  }

  // ESP32 SPI por defecto:
  // SCK  = GPIO 18
  // MISO = GPIO 19
  // MOSI = GPIO 23
  SPI.begin();

  Serial.println("SILABLOCKS_4RFID_READY");

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

// ==========================
// LOOP
// ==========================

void loop() {
  static unsigned long lastSeen[NUM_READERS] = {0};
  static char currentUid[NUM_READERS][21] = {{0}};
  static char candidateUid[NUM_READERS][21] = {{0}};
  static byte candidateConfirmations[NUM_READERS] = {0};
  static bool stableButtonState = HIGH;
  static bool sampledButtonState = HIGH;
  static unsigned long buttonChangedAt = 0;
  unsigned long ahora = millis();

  // ==========================
  // LECTURA DEL BOTON
  // ==========================

  bool buttonState = digitalRead(BUTTON_PIN);

  if (buttonState != sampledButtonState) {
    sampledButtonState = buttonState;
    buttonChangedAt = ahora;
  }

  if (sampledButtonState != stableButtonState &&
      ahora - buttonChangedAt >= BUTTON_DEBOUNCE_MS) {
    stableButtonState = sampledButtonState;
    if (stableButtonState == LOW) {
      Serial.println("BUTTON,ENTER");
    }
  }

  // ==========================
  // LECTURA DE LOS RFID
  // ==========================

  for (byte i = 0; i < NUM_READERS; i++) {
    char detectedUid[21] = {0};
    if (readPresentTag(readers[i], detectedUid, sizeof(detectedUid))) {
      lastSeen[i] = ahora;

      if (strcmp(detectedUid, currentUid[i]) == 0) {
        candidateUid[i][0] = '\0';
        candidateConfirmations[i] = 0;
      } else {
        if (strcmp(detectedUid, candidateUid[i]) == 0) {
          candidateConfirmations[i]++;
        } else {
          strncpy(candidateUid[i], detectedUid, sizeof(candidateUid[i]) - 1);
          candidateUid[i][sizeof(candidateUid[i]) - 1] = '\0';
          candidateConfirmations[i] = 1;
        }
      }

      if (candidateConfirmations[i] >= UID_CONFIRMATIONS_REQUIRED) {
        strncpy(currentUid[i], detectedUid, sizeof(currentUid[i]) - 1);
        currentUid[i][sizeof(currentUid[i]) - 1] = '\0';
        candidateUid[i][0] = '\0';
        candidateConfirmations[i] = 0;
        Serial.print("SLOT,");
        Serial.print(i);
        Serial.print(",");
        Serial.println(currentUid[i]);
      }
    }
  }

  for (byte i = 0; i < NUM_READERS; i++) {
    if (lastSeen[i] != 0 && ahora - lastSeen[i] >= TAG_REMOVAL_MS) {
      bool hadConfirmedTag = currentUid[i][0] != '\0';
      currentUid[i][0] = '\0';
      candidateUid[i][0] = '\0';
      candidateConfirmations[i] = 0;
      lastSeen[i] = 0;
      if (hadConfirmedTag) {
        Serial.print("SLOT,");
        Serial.print(i);
        Serial.println(",");
      }
    }
  }
}
