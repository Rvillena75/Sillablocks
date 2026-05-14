# Estado actual de SilaBlocks

Actualizado: 2026-05-14.

## Resumen

SilaBlocks ya funciona como MVP local de lectura inicial con input fisico,
misiones, recompensas, progreso persistente y tienda. El sistema esta preparado
para una demo universitaria sin nube ni cuentas de usuario.

El backend FastAPI sigue siendo la fuente de verdad. El frontend actual es HTML,
CSS y JavaScript servido por el mismo backend. La migracion futura definida es a
Phaser 4 + TypeScript + Vite.

## Arquitectura actual

```txt
Cubos NFC/RFID
   |
Telefono NFC o Arduino RFID
   |
GET /nfc?letra=...
   |
FastAPI
   |- buffer por bloques
   |- engine de misiones
   |- progreso persistente
   |- tienda
   |- WebSocket
   |
Pantallas HTML
   |- /       mision
   |- /aldea  tienda/progreso
```

## Backend

Entrada principal:

- `arduino/sila_server.py`

Modulos del juego:

- `arduino/game/buffer.py`: conserva la secuencia fisica de cubos.
- `arduino/game/engine.py`: procesa inputs, comandos y validacion de misiones.
- `arduino/game/missions.py`: define las misiones del MVP.
- `arduino/game/progress.py`: lee/escribe progreso local.
- `arduino/game/shop.py`: inventario y reglas de compra.

## Rutas disponibles

### Pantallas

- `GET /`: pantalla de mision actual.
- `GET /aldea`: aldea y tienda.

### Estado

- `GET /health`
- `GET /buffer`
- `GET /progress`
- `GET /shop`
- `WebSocket /ws`

### Input y comandos

- `GET /nfc?letra=<valor>`
- `POST /nfc`
- `DELETE /buffer`

Comandos soportados:

- `BORRAR`
- `DELETE`
- `BACKSPACE`
- `RESET`
- `RESET_TODO`
- `ENTER`
- `SIGUIENTE`
- `ANTERIOR`

## Misiones del MVP

| ID | Palabra | Bloques | Prompt | Restauracion | Recompensa |
| --- | --- | --- | --- | --- | --- |
| `m001` | MAMA/MAMA acentuado | `MA`, `MA acentuado` | Ayuda a Lumo a encender el farol perdido. | Farol del Bosque | 10 Lumenes |
| `m002` | PAPA/PAPA acentuado | `PA`, `PA acentuado` | Ayuda a Lumo a abrir el camino de madera. | Camino de Madera | 10 Lumenes |
| `m003` | CASA | `CA`, `SA` | Ayuda a Lumo a devolver una senal al pueblo. | Senal del Pueblo | 12 Lumenes + 1 Fragmento por hito |
| `m004` | MESA | `ME`, `SA` | Ayuda a Lumo a restaurar la mesa de la plaza. | Mesa de la Plaza | 12 Lumenes |
| `m005` | BOTA | `B`, `O`, `T`, `A` | Ayuda a Lumo a completar la primera ruta. | Ruta del Explorador | 14 Lumenes + 1 Fragmento por hito |

Nota: en codigo existen formas acentuadas para `MAMÁ` y `PAPÁ`. En esta tabla se
evita depender de render especial para que sea facil leerla en consola.

## Eventos visuales

Al completar una mision, el backend emite:

- `mission_completed`
- `reward_granted`
- `scene_restored`

Al comprar en tienda, el backend emite:

- `item_purchased`
- `village_restored`
- `zone_unlocked`, si la compra desbloquea zona.

Estos eventos ya se devuelven en las respuestas JSON. Phaser deberia consumir
estos mismos eventos cuando se migre el frontend.

## Progreso persistente

Archivo:

```txt
arduino/game_state.json
```

Campos:

- `lumens`
- `fragments`
- `completed_missions`
- `purchased_items`
- `unlocked_zones`
- `restored_items`

Estado inicial:

```json
{
  "lumens": 0,
  "fragments": 0,
  "completed_missions": [],
  "purchased_items": [],
  "unlocked_zones": ["forest"],
  "restored_items": []
}
```

## Tienda de la aldea

Inventario actual:

| ID | Nombre | Costo | Efecto |
| --- | --- | --- | --- |
| `small_lantern` | Farol pequeno | 8 Lumenes | Restaura luz en la aldea |
| `glowing_tree` | Arbol luminoso | 10 Lumenes | Restaura vegetacion luminosa |
| `restored_sign` | Senal restaurada | 12 Lumenes | Restaura una senal |
| `decorated_house` | Casa decorada | 15 Lumenes | Decora una casa |
| `path_to_village` | Abrir camino al Pueblo | 1 Fragmento | Desbloquea `village` |
| `restored_bridge` | Restaurar puente | 2 Fragmentos | Desbloquea `bridge_path` |

La aldea HTML actual:

- muestra recursos reales;
- muestra items comprados;
- muestra items bloqueados por recursos;
- permite comprar desde botones;
- actualiza visualmente objetos restaurados;
- escucha WebSocket para refrescar estado.

## Input fisico

### NFC por telefono

El flujo mas estable sigue siendo:

```txt
http://<PC_LOCAL_IP>:5000/nfc?letra=<VALOR>
```

### RFID con Arduino

El sketch `arduino/sketch_may1a/sketch_may1a.ino` lee UIDs por Serial. El puente
`arduino/rfid_bridge.py` traduce UID a bloque/comando usando:

```txt
arduino/rfid_uid_map.json
```

Mapeo actual en el repo:

| UID | Valor |
| --- | --- |
| `DAE9C103` | `B` |
| `9EE9C103` | `A` |
| `E200C203` | `O` |
| `C496C003` | `T` |

Importante: el backend acepta cualquier valor normal que llegue por
`/nfc?letra=...`, pero el puente RFID solo puede enviar UIDs que esten mapeados
en `rfid_uid_map.json`.

## Frontend actual

Archivos:

- `arduino/templates/index.html`
- `arduino/templates/aldea.html`
- `arduino/static/app.js`
- `arduino/static/village.js`
- `arduino/static/styles.css`

Pantalla de mision:

- Bosque de las Silabas.
- Lumo.
- farol;
- niebla;
- cubos escaneados como piezas fisicas;
- feedback positivo.

Pantalla de aldea:

- recursos;
- restauraciones;
- tienda;
- compras persistentes.

## Verificacion actual

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Ultima verificacion ejecutada durante esta iteracion:

```txt
37 passed
```

## Limitaciones conocidas

- La pantalla actual todavia no usa Phaser; es HTML/CSS/JS.
- Las animaciones de mision aun dependen principalmente del estado y CSS; Phaser
  deberia consumir los eventos visuales de forma mas rica.
- `game_state.json` es suficiente para MVP, pero SQLite sera mejor si se agregan
  perfiles, historial de sesiones o muchas escrituras.
- El arte sigue siendo placeholder/codigo CSS; faltan assets 2D finales.
- La aldea funciona, pero necesita pulido visual y mejores estados de feedback.
