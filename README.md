# SilaBlocks

SilaBlocks es un prototipo fisico-digital para practicar lectura inicial. El
nino usa cubos fisicos con NFC/RFID para construir silabas y palabras; el PC
recibe esos inputs por red local y muestra una experiencia visual con misiones,
recompensas y una aldea donde se gastan recursos.

El objetivo del MVP actual es demostrar este loop:

```txt
Escanear cubos -> completar mision -> ganar Lumenes/Fragmentos -> comprar en la aldea -> ver progreso persistente
```

## Estado actual

El proyecto ya tiene un MVP local funcional:

- Backend FastAPI en `arduino/sila_server.py`.
- Contrato NFC estable: `GET /nfc?letra=<valor>`.
- Buffer por bloques fisicos, no solo texto plano.
- Cinco misiones: `MAMA`, `PAPA`, `CASA`, `MESA`, `BOTA`.
- Pantalla de mision en `/`.
- Aldea/tienda en `/aldea`.
- Progreso local de demo en `arduino/game_state.json`, reiniciado al arrancar
  el servidor.
- Estado base versionado en `arduino/game_state.example.json`.
- Inventario de tienda con `GET /shop` y compras con `POST /buy`.
- Eventos visuales para mision y tienda.
- Tests automatizados con `pytest`.

El stack futuro definido para el frontend de juego es:

```txt
Phaser 4 + TypeScript + Vite
```

Por ahora, el frontend activo sigue siendo HTML/CSS/JavaScript servido por
FastAPI. La migracion a Phaser debe hacerse despues de estabilizar el loop
misiones-recompensas-aldea.

## Requisitos

- Windows + PowerShell.
- Python 3.11+.
- Dependencias de `arduino/requirements.txt`.
- Opcional para RFID: Arduino Uno + RC522 + puente serial.

## Instalacion

Desde la raiz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r arduino\requirements.txt
```

## Ejecutar el servidor

```powershell
.\.venv\Scripts\python.exe arduino\sila_server.py
```

El servidor queda en:

```txt
http://localhost:5000
```

Para usar un telefono en la misma red WiFi, abrir la URL con la IP local del PC:

```txt
http://<PC_LOCAL_IP>:5000/nfc?letra=MA
```

## Pantallas principales

- `http://localhost:5000/`: mision actual.
- `http://localhost:5000/aldea`: aldea y tienda.

## Flujo de demo manual

1. Abrir `http://localhost:5000/`.
2. Si quieres dejar todo en cero antes de presentar:

```powershell
.\scripts\reset_demo.ps1
```

El script ejecuta `RESET_TODO`, revisa `/health`, `/buffer` y `/progress`, y
muestra URLs con la IP local del PC para configurar el telefono.

3. Escanear o simular:

```powershell
Invoke-RestMethod "http://localhost:5000/nfc?letra=MA"
Invoke-RestMethod "http://localhost:5000/nfc?letra=M%C3%81"
```

4. Revisar progreso:

```powershell
Invoke-RestMethod http://localhost:5000/progress
```

5. Abrir `http://localhost:5000/aldea`.
6. Comprar una mejora si hay recursos:

```powershell
Invoke-RestMethod http://localhost:5000/buy -Method Post -ContentType "application/json" -Body '{"item_id":"small_lantern"}'
```

7. Resetear demo si se necesita partir limpio:

```powershell
Invoke-RestMethod "http://localhost:5000/nfc?letra=RESET_TODO"
```

## API principal

### Estado y pantalla

- `GET /health`: healthcheck.
- `GET /`: pantalla de mision.
- `GET /aldea`: pantalla de aldea/tienda.
- `GET /buffer`: estado completo de mision.
- `WebSocket /ws`: actualizaciones en tiempo real.

### Input NFC/RFID

- `GET /nfc?letra=<valor>`
- `POST /nfc`
- `DELETE /buffer`

Comandos especiales:

- `BORRAR`, `DELETE`, `BACKSPACE`: eliminan el ultimo bloque.
- `RESET`: reinicia la mision actual.
- `RESET_TODO`: reinicia toda la demo y progreso persistente.
- `ENTER`: valida el estado actual.
- `SIGUIENTE`: avanza despues de completar una mision.
- `ANTERIOR`: vuelve a la mision anterior.

### Progreso y tienda

- `GET /progress`: recursos, misiones, compras y zonas.
- `GET /shop`: inventario y disponibilidad.
- `POST /buy`: compra una mejora.

Ejemplo:

```json
{
  "item_id": "small_lantern"
}
```

## Estructura relevante

```txt
.
├── README.md
├── AGENTS.md
├── stack_tecnico.md
├── plan_frontend.md
├── docs/
│   ├── estado_actual.md
│   └── proximos_pasos.md
├── Descripcion del juego/
├── arduino/
│   ├── sila_server.py
│   ├── game_state.example.json
│   ├── requirements.txt
│   ├── rfid_bridge.py
│   ├── rfid_uid_map.json
│   ├── game/
│   │   ├── buffer.py
│   │   ├── engine.py
│   │   ├── missions.py
│   │   ├── progress.py
│   │   └── shop.py
│   ├── static/
│   └── templates/
└── tests/
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

La suite cubre rutas principales, buffer por bloques, misiones, comandos,
progreso persistente, tienda y compras.

## Documentacion adicional

- [Estado actual](docs/estado_actual.md)
- [Proximos pasos](docs/proximos_pasos.md)
- [Stack tecnico](stack_tecnico.md)
- [Plan frontend](plan_frontend.md)
- [Migracion RFID](arduino/RFID_MIGRATION.md)

## Reglas de desarrollo importantes

- No romper `GET /nfc?letra=...`.
- Mantener `available_blocks` como guia visual, no como filtro duro.
- Guardar progreso local sin datos personales de ninos.
- Mantener `arduino/game_state.json` como archivo runtime ignorado por Git.
- Priorizar demo estable sobre arquitectura compleja.
- Antes de migrar a Phaser, mantener funcional el MVP HTML actual.
