# Stack tecnico de SilaBlocks

## 1. Decision

El stack recomendado para SilaBlocks es:

```txt
Frontend de juego: Phaser 4 + TypeScript + Vite
Backend: FastAPI + WebSocket
Persistencia MVP: JSON local
Persistencia futura: SQLite
Input fisico: NFC telefono y/o Arduino RFID -> FastAPI
Animaciones: spritesheets/TexturePacker primero, Rive despues
Arte: Figma + herramienta 2D dedicada
Audio: Audacity + sonidos con licencia revisada
```

Esta decision prioriza un MVP local, estable y demostrable: el nino escanea
cubos fisicos, la pantalla reacciona en tiempo real, la mision entrega
recompensas y la aldea cambia de forma persistente.

## 2. Principios de arquitectura

### FastAPI es la fuente de verdad

El backend decide:

- que input NFC/RFID llego;
- como se actualiza el buffer por bloques;
- si la respuesta progresa, necesita ajuste o completa la mision;
- que recompensas se entregan;
- que progreso se guarda;
- que compras se permiten;
- que eventos visuales deben emitirse.

### Phaser renderiza e interpreta eventos

El frontend no debe validar palabras ni decidir recompensas. Phaser recibe estado
y eventos desde FastAPI, y los convierte en animaciones:

- aparicion de cubos fisicos;
- luz del farol;
- niebla que desaparece;
- Lumo reaccionando;
- objetos restaurados;
- compras visibles en la aldea.

Regla central:

```txt
El backend decide que ocurrio.
Phaser decide como se ve.
```

## 3. Stack por capa

| Capa | Tecnologia | Uso |
| --- | --- | --- |
| Motor visual | Phaser 4 | Escenas 2D, sprites, filtros, luz, particulas, input y transiciones |
| Lenguaje frontend | TypeScript | Tipado de eventos, payloads, escenas y cliente API |
| Build frontend | Vite | Dev server rapido, HMR y build estatico |
| Backend | FastAPI | API local, WebSocket, estado de juego, tienda y progreso |
| Runtime backend | Python 3.11+ | Compatibilidad con el prototipo actual |
| Realtime | WebSocket `/ws` | Actualizar pantalla al escanear cubos |
| Input telefono | `GET /nfc?letra=...` | Compatibilidad con NFC Tools y flujo WiFi |
| Input RFID | Arduino Uno + RC522 + `rfid_bridge.py` | Leer UID y traducirlo a bloque/comando |
| Persistencia MVP | `arduino/game_state.json` | Recursos, compras, misiones y zonas |
| Persistencia futura | SQLite | Historial, sesiones y perfiles si el MVP crece |
| Prototipo visual | Figma | Flujos, layout y componentes |
| Arte 2D | Krita, Photoshop, Affinity Designer o Illustrator | Fondos, Lumo, cubos, objetos y UI |
| Optimización arte | TexturePacker | Atlases/spritesheets para Phaser |
| Animacion especial | Rive opcional | Personajes o microinteracciones complejas |
| Audio | Audacity | Edicion de efectos y ambiente |
| Tests backend | pytest + FastAPI TestClient | API, engine, tienda y persistencia |
| Tests frontend | TypeScript build + Playwright futuro | Compilacion y regresion visual |

## 4. Por que Phaser 4

Phaser 4 es la mejor opcion para iniciar el frontend nuevo porque el proyecto
necesita una escena 2D viva, no una web tradicional:

- escenas como `MissionScene`, `RewardScene` y `VillageScene`;
- sprites y atlases para cubos, Lumo, faroles y objetos;
- particulas para luz, niebla y fragmentos;
- filtros y efectos visuales para restaurar zonas;
- input simple para botones de demo/debug;
- build web facil con Vite;
- integracion directa con WebSocket y HTTP del backend.

Phaser 3 era una opcion razonable, pero para un proyecto nuevo conviene partir
con Phaser 4.x. La documentacion actual de Phaser presenta Phaser 4 como la
version nueva para proyectos web 2D y destaca mejoras de renderer, filtros,
luces y rendimiento.

## 5. Por que mantener FastAPI

FastAPI ya resuelve lo mas sensible del proyecto:

- recibe eventos desde el telefono o el puente RFID;
- conserva el contrato `GET /nfc?letra=...`;
- expone WebSocket;
- puede servir la pantalla local;
- es simple para integrarse con Python, pyserial y archivos JSON;
- permite tests rapidos con `pytest`.

No conviene migrar el backend a Node, Firebase o un motor multiplayer para el
MVP. La necesidad actual no es multiplayer ni nube. Es estabilidad local y
control del hardware.

## 6. Contratos que no se pueden romper

El contrato de entrada principal debe mantenerse:

```txt
GET /nfc?letra=<valor>
```

Ejemplos:

```txt
/nfc?letra=MA
/nfc?letra=CASA
/nfc?letra=BORRAR
/nfc?letra=RESET
/nfc?letra=ENTER
```

Reglas:

- un valor normal se agrega al buffer como bloque;
- `BORRAR`, `DELETE` y `BACKSPACE` eliminan el ultimo bloque;
- `RESET` limpia la mision actual;
- `ENTER` valida o confirma la accion actual;
- `available_blocks` es guia visual, no filtro duro del backend;
- el RFID real solo puede enviar UIDs que existan en `arduino/rfid_uid_map.json`.

## 7. Endpoints backend

### Existentes que se deben conservar

- `GET /health`
- `GET /`
- `GET /buffer`
- `GET /nfc?letra=<valor>`
- `POST /nfc`
- `DELETE /buffer`
- `WebSocket /ws`

### Nuevos para cerrar el loop de juego

- `GET /progress`
- `GET /shop`
- `POST /buy`

### Payload de estado recomendado

```json
{
  "current_blocks": ["MA"],
  "current_text": "MA",
  "last_input": "MA",
  "mission_id": "forest_lantern",
  "zone_id": "forest",
  "prompt": "Ayuda a Lumo a encender el farol perdido.",
  "target_text": "MAMA",
  "target_blocks": ["MA", "MA"],
  "available_blocks": ["MA", "PA", "SA"],
  "status": "in_progress",
  "feedback": "Falta una parte.",
  "progress_percent": 50,
  "lumens": 8,
  "fragments": 0,
  "events": [
    { "type": "block_scanned", "value": "MA" },
    { "type": "partial_progress", "expected_next": "MA" }
  ]
}
```

## 8. Eventos visuales

El engine debe emitir eventos para que Phaser anime sin inferir desde strings.

Eventos base:

- `block_scanned`
- `partial_progress`
- `wrong_block`
- `mission_completed`
- `reward_granted`
- `scene_restored`
- `item_purchased`
- `village_restored`

Ejemplo:

```json
{
  "events": [
    { "type": "mission_completed", "mission_id": "forest_lantern" },
    { "type": "reward_granted", "lumens": 8, "fragments": 0 },
    { "type": "scene_restored", "item": "small_lantern" }
  ]
}
```

## 9. Persistencia local

Archivo MVP:

```txt
arduino/game_state.json
```

Contenido recomendado:

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

Reglas:

- no guardar datos personales de ninos;
- escribir JSON valido y legible;
- validar recursos antes de comprar;
- persistir despues de completar misiones y compras;
- tests deben poder usar un archivo temporal para no tocar el progreso real.

SQLite puede reemplazar este archivo cuando existan perfiles, historial de
sesiones, estadisticas o muchas escrituras concurrentes.

## 10. Estructura sugerida

### Backend

```txt
arduino/
  sila_server.py
  game/
    buffer.py
    engine.py
    missions.py
    progress.py
    shop.py
    models.py
  static/
  templates/
  requirements.txt
  game_state.json
  rfid_bridge.py
  rfid_uid_map.json
```

### Frontend

```txt
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  index.html
  src/
    main.ts
    game.ts
    api/
      backendClient.ts
      types.ts
    scenes/
      BootScene.ts
      MapScene.ts
      MissionScene.ts
      RewardScene.ts
      VillageScene.ts
      DebugOverlay.ts
    systems/
      EventBus.ts
      MissionEventPlayer.ts
      ShopState.ts
    ui/
      buttons.ts
      text.ts
    assets/
      manifest.ts
  public/
    assets/
      forest/
      village/
      lumo/
      cubes/
      ui/
      audio/
```

## 11. Escenas del juego

### `BootScene`

- Carga assets base.
- Inicializa cliente API.
- Lee `/buffer`, `/progress` y `/shop`.
- Pasa a mapa o mision.

### `MapScene`

- Muestra zonas desbloqueadas.
- Permite entrar a la mision actual.
- Puede ser minima en el MVP.

### `MissionScene`

Primera zona: Bosque de las Silabas.

Debe mostrar:

- fondo de bosque;
- camino con niebla;
- farol apagado;
- Lumo;
- fragmentos/letras flotando;
- cubos escaneados como piezas fisicas;
- animacion de exito con luz, color y niebla desapareciendo.

### `RewardScene`

- Muestra Lumenes/Fragmentos ganados.
- Muestra objeto restaurado.
- Permite ir a aldea o seguir.

### `VillageScene`

- Consume `/progress` y `/shop`.
- Permite gastar Lumenes y Fragmentos.
- Refleja compras persistentes.

### `DebugOverlay`

Debe ser visible para demo, pero secundario.

Debe mostrar:

- WebSocket conectado/desconectado;
- ultimo input;
- bloques actuales;
- texto unido;
- mision actual;
- eventos recientes;
- recursos actuales;
- botones manuales para debug.

## 12. Aldea y tienda MVP

Compras iniciales:

| Item | Costo | Efecto |
| --- | --- | --- |
| Farol pequeno | 8 Lumenes | Agrega luz en la aldea |
| Arbol luminoso | 10 Lumenes | Restaura vegetacion |
| Senal restaurada | 12 Lumenes | Mejora navegacion visual |
| Casa decorada | 15 Lumenes | Personaliza casa |
| Abrir camino al Pueblo | 1 Fragmento | Desbloquea camino |
| Restaurar puente | 2 Fragmentos | Desbloquea estructura mayor |

La compra debe fallar suavemente si no hay recursos suficientes. No debe usar
castigos ni lenguaje negativo.

## 13. Versiones y politica de dependencias

Recomendado:

- Python 3.11+.
- Node.js compatible con la version vigente de Vite. Al momento de definir este
  documento, Vite requiere Node.js 20.19+ o 22.12+.
- Phaser 4.x.
- TypeScript 5.x.
- Vite version actual estable.
- FastAPI y Uvicorn desde `arduino/requirements.txt`.

Reglas:

- usar `package-lock.json` cuando se cree `frontend/`;
- no depender de CDNs para la demo;
- fijar versiones mayores;
- actualizar dependencias solo con prueba de build y prueba manual del demo;
- mantener `arduino/requirements.txt` como fuente del backend Python.

## 14. Comandos de desarrollo

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r arduino\requirements.txt
python arduino\sila_server.py
```

Servidor esperado:

```txt
http://localhost:5000
```

Checks:

```powershell
Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod "http://localhost:5000/nfc?letra=MA"
Invoke-RestMethod http://localhost:5000/buffer
```

### Frontend futuro

```powershell
cd frontend
npm install
npm run dev
npm run build
```

Dev servers:

```txt
FastAPI: http://localhost:5000
Vite:    http://localhost:5173
```

Demo empaquetada:

```txt
frontend/dist/ servido por FastAPI
```

## 15. Testing minimo

### Backend

Usar:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Cubrir:

- `/health`;
- `/nfc`;
- `/buffer`;
- comandos `BORRAR`, `RESET`, `ENTER`;
- buffer por bloques;
- eventos visuales;
- recompensas;
- `/progress`;
- `/shop`;
- `/buy`;
- persistencia de `game_state.json`.

### Frontend

Al crear `frontend/`, cubrir:

- `npm run build`;
- TypeScript sin errores;
- conexion a `/buffer`;
- conexion a `/ws`;
- compra desde aldea;
- captura visual manual o Playwright para escenas clave.

## 16. Herramientas descartadas para el MVP

### Unity

No se recomienda ahora. Es pesado para una demo web/local con NFC y agrega
complejidad de WebGL, empaquetado e integracion.

### Godot

Es una alternativa seria si el proyecto se convierte en app de escritorio con
editor visual fuerte. Para el MVP web/local con FastAPI, WebSocket y navegador,
Phaser es mas directo.

### PixiJS

Es muy buen renderer, pero no es un motor de juego completo. Habria que armar
mas arquitectura propia para escenas, flujo, eventos y UI.

### Three.js

No corresponde al MVP porque SilaBlocks es 2D. Three.js seria util solo si el
producto decide pasar a 3D real.

### React como frontend principal

Puede servir para paneles o administracion, pero no debe ser el motor de la
experiencia jugable. La mision necesita escena 2D, animacion y timing visual.

## 17. Roadmap tecnico recomendado

1. Agregar `arduino/game_state.json`, progreso y tienda.
2. Agregar `/progress`, `/shop` y `/buy`.
3. Emitir eventos visuales desde el engine.
4. Crear `frontend/` con Phaser 4 + TypeScript + Vite.
5. Implementar `MissionScene` del Bosque de las Silabas.
6. Implementar `RewardScene`.
7. Implementar `VillageScene` como tienda real.
8. Reemplazar placeholders por arte y audio.
9. Evaluar Rive para Lumo.
10. Considerar SQLite si el progreso crece.

## 18. Criterio de exito del stack

El stack esta funcionando si:

- el nino escanea un cubo fisico;
- el backend recibe `/nfc?letra=...`;
- Phaser muestra el cubo como objeto en escena;
- la mision valida el progreso;
- al completar, se entrega recompensa;
- la aldea permite gastar recompensa;
- la compra queda persistida;
- todo corre localmente en un PC de demo sin depender de nube.

## 19. Referencias oficiales

- Phaser 4: https://phaser.io/phaser4
- Phaser 3 vs Phaser 4: https://phaser.io/news/2026/05/phaser-3-vs-phaser-4
- Vite guide: https://vite.dev/guide/
- FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
- Rive Web runtime: https://rive.app/docs/runtimes/web
- Godot web export: https://docs.godotengine.org/en/4.5/tutorials/export/exporting_for_web.html
