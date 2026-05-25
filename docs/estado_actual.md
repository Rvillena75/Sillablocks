# Estado actual de SilaBlocks

Actualizado: 2026-05-23.

## Resumen

SilaBlocks esta en una iteracion software-only. La demo oficial del juego es
`frontend/`, una app React + Phaser 4 + TypeScript + Vite. Debe correr sin
hardware, sin NFC real y sin backend obligatorio.

El backend FastAPI, la UI embebida de `arduino/templates/` y el prototipo
`frontend-pixi/` se mantienen en el repo, pero quedan marcados como
legacy/alternativos. No son la ruta recomendada para presentar ni seguir esta
iteracion.

## Arquitectura actual

```txt
frontend/
   |- React: shell, paneles, cubos, aldea, tienda, debug
   |- game/phaser: escena jugable oficial del bosque
   |- game/bridge: puente React -> Phaser
   |- game/state/localDemoState: estado local en memoria
   |- BackendClient: FastAPI opcional con fallback local

legacy/alternativos:
   |- arduino/sila_server.py
   |- arduino/templates/
   |- arduino/static/
   |- frontend-pixi/
   |- frontend/src/deprecated/phaser-scenes/
```

## Backend

Estado: legacy/compatible, no obligatorio para la demo oficial.

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
| `m001` | MAMA | `M`, `A`, `M`, `A` | Ayuda a Lumo a encender el farol perdido. | Farol del Bosque | 10 Lumenes |
| `m002` | PAPA | `P`, `A`, `P`, `A` | Ayuda a Lumo a abrir el camino de madera. | Camino de Madera | 10 Lumenes |
| `m003` | CASA | `C`, `A`, `S`, `A` | Ayuda a Lumo a devolver una senal al pueblo. | Senal del Pueblo | 12 Lumenes + 1 Fragmento por hito |
| `m004` | MESA | `M`, `E`, `S`, `A` | Ayuda a Lumo a restaurar la mesa de la plaza. | Mesa de la Plaza | 12 Lumenes |
| `m005` | BOTA | `B`, `O`, `T`, `A` | Ayuda a Lumo a completar la primera ruta. | Ruta del Explorador | 14 Lumenes + 1 Fragmento por hito |

Nota: el prototipo se mantiene sin tildes en el contrato tecnico para que el
flujo RFID/NFC y las pruebas por consola sean simples y estables.

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
  "lumens": 99,
  "fragments": 99,
  "completed_missions": [],
  "purchased_items": [],
  "unlocked_zones": ["forest"],
  "restored_items": []
}
```

Nota: se parte con 99 Lumenes y 99 Fragmentos a proposito durante el MVP para
probar compras, decoraciones y aldea sin bloquear la demo por falta de recursos.

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

## Input fisico legacy

### NFC por telefono

El flujo por telefono sigue existiendo para integracion posterior, pero no es
requerido por la demo oficial React/Phaser:

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

## Frontend oficial

Ruta oficial:

- `frontend/`

Responsabilidades:

- React: header, panel de mision, bandeja de cubos, aldea, tienda y debug.
- Phaser: escena visual del bosque, Lumo, farol, niebla, cubos y feedback.
- Flujo Phaser oficial: `MissionView -> PhaserStage -> createStorybookGame -> StorybookScene`.
- Estado local: `frontend/src/game/state/localDemoState.ts`.
- Backend opcional: `frontend/src/api/backendClient.ts`.

Caminos no oficiales:

- `frontend/src/deprecated/phaser-scenes/`: stack Phaser anterior
  `BootScene/MissionScene/RewardScene/VillageScene`, no conectado a `npm run dev`.
- `arduino/templates/index.html` y `arduino/templates/aldea.html`: UI embebida
  legacy.
- `frontend-pixi/`: alternativa experimental PixiJS.

## Verificacion actual

Frontend oficial:

```powershell
cd frontend
npm run build
```

Backend legacy, solo si se modifica esa capa:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp C:\tmp\sillablocks-pytest
```

## Limitaciones conocidas

- El modo local de `frontend/` usa estado en memoria; al recargar se reinicia.
- FastAPI sigue disponible, pero no debe ser obligatorio para probar software.
- `game_state.json` es suficiente para MVP, pero SQLite sera mejor si se agregan
  perfiles, historial de sesiones o muchas escrituras.
- El arte sigue siendo placeholder/codigo CSS; faltan assets 2D finales.
- La aldea necesita pulido visual y mejores estados de feedback en una iteracion
  posterior.
