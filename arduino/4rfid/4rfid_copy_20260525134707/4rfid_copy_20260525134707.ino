#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 27
#define NUM_READERS 4
#define BUTTON_PIN 17

// Orden: lector 1, lector 2, lector 3, lector 4.
byte SS_PINS[NUM_READERS] = {16, 5, 21, 4};

MFRC522 readers[NUM_READERS] = {
  MFRC522(SS_PINS[0], RST_PIN),
  MFRC522(SS_PINS[1], RST_PIN),
  MFRC522(SS_PINS[2], RST_PIN),
  MFRC522(SS_PINS[3], RST_PIN),
};

// ==========================
// FUNCIONES AUXILIARES
// ==========================

String uidToString(MFRC522::Uid *uid) {
  String uidStr = "";

  for (byte i = 0; i < uid->size; i++) {
    if (uid->uidByte[i] < 0x10) {
      uidStr += "0";
    }

    uidStr += String(uid->uidByte[i], HEX);
  }

  uidStr.toUpperCase();
  return uidStr;
}

// ==========================
// SETUP
// ==========================

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

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
  static unsigned long lastSend[NUM_READERS] = {0};
  static unsigned long lastSeen[NUM_READERS] = {0};
  static String currentUid[NUM_READERS] = {"", "", "", ""};
  static bool lastButtonState = HIGH;

  const unsigned long INTERVALO_ENVIO = 250; // Evita saturar el puerto Serial.
  const unsigned long TIEMPO_SIN_LECTURA = 900; // Limpia el espacio si ya no se lee tag.
  unsigned long ahora = millis();

  // ==========================
  // LECTURA DEL BOTON
  // ==========================

  bool buttonState = digitalRead(BUTTON_PIN);

  // Con INPUT_PULLUP:
  // HIGH = no presionado
  // LOW  = presionado
  if (lastButtonState == HIGH && buttonState == LOW) {
    Serial.println("BUTTON,ENTER");
  }

  lastButtonState = buttonState;

  // ==========================
  // LECTURA DE LOS RFID
  // ==========================

  for (byte i = 0; i < NUM_READERS; i++) {
    if (!readers[i].PICC_IsNewCardPresent()) {
      continue;
    }

    if (!readers[i].PICC_ReadCardSerial()) {
      continue;
    }

    if (ahora - lastSend[i] >= INTERVALO_ENVIO) {
      lastSend[i] = ahora;

      String uid = uidToString(&readers[i].uid);
      lastSeen[i] = ahora;

      if (uid != currentUid[i]) {
        currentUid[i] = uid;
        Serial.print("SLOT,");
        Serial.print(i);
        Serial.print(",");
        Serial.println(uid);
      }
    }

    // No llamar PICC_HaltA() si quieres lectura continua mientras el tag esté puesto.
    // readers[i].PICC_HaltA();
    // readers[i].PCD_StopCrypto1();
  }

  for (byte i = 0; i < NUM_READERS; i++) {
    if (currentUid[i] != "" && ahora - lastSeen[i] >= TIEMPO_SIN_LECTURA) {
      currentUid[i] = "";
      Serial.print("SLOT,");
      Serial.print(i);
      Serial.println(",");
    }
  }
}
