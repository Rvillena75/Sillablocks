import serial

PUERTO = "COM6"  # cambia esto por tu puerto real
BAUDIOS = 115200

ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)

print(f"Leyendo desde {PUERTO}...")
print("Acerca un tag RFID.")

while True:
    linea = ser.readline().decode(errors="ignore").strip()
    if linea:
        print(linea)