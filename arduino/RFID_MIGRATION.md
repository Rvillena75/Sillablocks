# Migracion a Arduino Uno + lector RFID 13.56 MHz

El servidor SilaBlocks no cambia: sigue recibiendo eventos por:

```txt
GET http://localhost:5000/nfc?letra=<valor>
```

El Arduino reemplaza al telefono como lector fisico. El flujo queda:

```txt
Cubo RFID -> Arduino Uno + RC522 -> Serial USB -> rfid_bridge.py -> sila_server.py
```

## 1. Conexion del RC522

```txt
RC522 SDA/SS -> Arduino D10
RC522 SCK    -> Arduino D13
RC522 MOSI   -> Arduino D11
RC522 MISO   -> Arduino D12
RC522 RST    -> Arduino D9
RC522 3.3V   -> Arduino 3.3V
RC522 GND    -> Arduino GND
```

No alimentes el RC522 con 5V.

## 2. Cargar el sketch

Abre en Arduino IDE:

```txt
arduino/sketch_may1a/sketch_may1a.ino
```

Instala la libreria `MFRC522`, selecciona la placa `Arduino Uno`, el puerto `COM`
correspondiente y sube el sketch.

## 3. Obtener los UIDs reales

Con el sketch cargado, abre el monitor serial a `9600` baudios y acerca cada
cubo/tag. El Arduino imprimira valores como:

```txt
SILABLOCKS_RFID_READY
A1B2C3D4
11223344
```

Anota que UID corresponde a cada cubo.

## 4. Mapear UID a bloque del juego

Edita:

```txt
arduino/rfid_uid_map.json
```

Ejemplo:

```json
{
  "A1B2C3D4": "MA",
  "11223344": "MÁ",
  "55667788": "BORRAR",
  "99AABBCC": "RESET"
}
```

Los valores deben coincidir con los bloques y comandos que ya entiende el
servidor: `MA`, `MÁ`, `PA`, `SA`, `BORRAR`, `RESET`, `ENTER`, `SIGUIENTE`,
`ANTERIOR`, etc.

## 5. Ejecutar el prototipo

Terminal 1:

```powershell
.\.venv\Scripts\python.exe arduino\sila_server.py
```

Terminal 2:

```powershell
.\.venv\Scripts\python.exe arduino\rfid_bridge.py COM3
```

Cambia `COM3` por el puerto real del Arduino.

Abre la pantalla:

```txt
http://localhost:5000
```

Cuando acerques un cubo, el puente imprimira algo como:

```txt
A1B2C3D4 -> MA
```

y el bloque aparecera en la pantalla del juego.

## 6. Prueba sin Arduino

Para validar el mapeo sin enviar al servidor:

```powershell
.\.venv\Scripts\python.exe arduino\rfid_bridge.py --simulate A1B2C3D4 --dry-run
```

Para enviar un UID simulado al servidor:

```powershell
.\.venv\Scripts\python.exe arduino\rfid_bridge.py --simulate A1B2C3D4
```
