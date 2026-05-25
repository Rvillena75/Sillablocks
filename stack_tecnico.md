# Stack tecnico de SilaBlocks

## 1. Decision

El stack oficial para la demo del juego SilaBlocks en esta iteracion es:

```txt
Frontend de juego: React + Phaser 4 + TypeScript + Vite
Backend: opcional/legacy, FastAPI + WebSocket
Persistencia demo: estado local en memoria dentro de frontend/
Persistencia futura: backend local o SQLite
Input fisico: fuera de alcance para esta iteracion
Animaciones: spritesheets/TexturePacker primero, Rive despues
Arte: Figma + herramienta 2D dedicada
Audio: Audacity + sonidos con licencia revisada
```

Esta decision prioriza una demo software-only, estable y demostrable: el usuario
elige cubos en pantalla, la mision entrega feedback y la aldea refleja progreso
sin requerir telefono, Arduino, NFC real ni backend obligatorio.

`frontend/` es el camino oficial. `frontend-pixi/` queda como alternativa
experimental no oficial. `arduino/templates/` queda como UI embebida legacy.

## 2. Principios de arquitectura

### Frontend/ es la fuente de la demo

Para esta iteracion, `frontend/` debe poder decidir el flujo de demo en modo
local:

- que cubo simulado se eligio;
- como se actualiza el buffer por bloques;
- si la respuesta progresa, necesita ajuste o completa la mision;
- que recompensas se entregan en memoria;
- que compras se permiten durante la sesion.

FastAPI conserva valor como integracion futura y contrato legacy, pero no debe
ser obligatorio para correr la demo oficial.

### Phaser renderiza e interpreta eventos

Phaser recibe estado desde React/modo local o backend opcional, y lo convierte en
animaciones:

- aparicion de cubos fisicos;
- luz del farol;
- niebla que desaparece;
- Lumo reaccionando;
- objetos restaurados;
- compras visibles en la aldea.

Regla central:

```txt
El estado de juego decide que ocurrio.
Phaser decide como se ve.
```

## 3. Stack por capa

| Capa | Tecnologia | Uso |
| --- | --- | --- |
| Motor visual | Phaser 4 | Escenas 2D, sprites, filtros, luz, particulas, input y transiciones |
| Lenguaje frontend | TypeScript | Tipado de eventos, payloads, escenas y cliente API |
| Build frontend | Vite | Dev server rapido, HMR y build estatico |
| Backend | FastAPI opcional | Integracion legacy/futura, no obligatoria para frontend/ |
| Runtime backend | Python 3.11+ | Compatibilidad con el prototipo anterior |
| Realtime | WebSocket `/ws` opcional | Solo si se levanta FastAPI |
| Input telefono | `GET /nfc?letra=...` | Legacy/futuro, fuera del flujo oficial actual |
| Input RFID | Arduino Uno + RC522 + `rfid_bridge.py` | Legacy/futuro, no requerido |
| Persistencia demo | `frontend/src/game/state/localDemoState.ts` | Estado local en memoria |
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

- una escena jugable oficial (`StorybookScene`) y posibles escenas futuras;
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

## 5. Por que mantener FastAPI como legacy/opcional

FastAPI ya resuelve piezas utiles para integracion posterior:

- recibe eventos desde el telefono o el puente RFID;
- conserva el contrato `GET /nfc?letra=...`;
- expone WebSocket;
- puede servir la pantalla local;
- es simple para integrarse con Python, pyserial y archivos JSON;
- permite tests rapidos con `pytest`.

No conviene borrarlo, pero tampoco conviene hacerlo obligatorio para esta
iteracion. La necesidad actual es estabilizar la demo React/Phaser.

## 6. Contratos legacy que no se deben romper

El contrato de entrada principal debe mantenerse:

```txt
GET /nfc?letra=<valor>
```

Ejemplos:

```txt
/nfc?letra=M
/nfc?letra=CASA
/nfc?letra=BORRAR
/nfc?letra=RESET
/nfc?letra=ENTER
```

Reglas legacy:

- un valor normal se agrega al buffer como bloque;
- en el MVP actual, cada cubo de aprendizaje representa una letra individual;
- silabas y palabras completas siguen siendo compatibles a nivel tecnico, pero
  no son el contrato pedagogico principal del MVP;
- `BORRAR`, `DELETE` y `BACKSPACE` eliminan el ultimo bloque;
- `RESET` limpia la mision actual;
- `ENTER` valida o confirma la accion actual;
- `available_blocks` es guia visual, no filtro duro del backend;
- el RFID real solo puede enviar UIDs que existan en `arduino/rfid_uid_map.json`.

## 7. Endpoints backend opcionales

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
  "current_blocks": ["M", "A"],
  "current_text": "MA",
  "last_input": "A",
  "mission_id": "forest_lantern",
  "zone_id": "forest",
  "prompt": "Ayuda a Lumo a encender el farol perdido.",
  "target_text": "MAMA",
  "target_blocks": ["M", "A", "M", "A"],
  "available_blocks": ["M", "A", "P", "S"],
  "status": "in_progress",
  "feedback": "Falta una parte.",
  "progress_percent": 50,
  "lumens": 8,
  "fragments": 0,
  "events": [
    { "type": "block_scanned", "value": "A" },
    { "type": "partial_progress", "expected_next": "M" }
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
  "lumens": 99,
  "fragments": 99,
  "completed_missions": [],
  "purchased_items": [],
  "unlocked_zones": ["forest"],
  "restored_items": []
}
```

Durante el MVP se parte con 99 Lumenes y 99 Fragmentos para probar tienda,
decoraciones y aldea sin tener que completar todas las misiones antes.

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
    main.tsx
    App.tsx
    api/
      backendClient.ts
      types.ts
    components/
      PhaserStage.tsx
      MissionView.tsx
      VillageView.tsx
      DebugPanel.tsx
    game/
      bridge/
        sceneBus.ts
      data/
        storybookAssets.ts
      state/
        localDemoState.ts
      phaser/
        bootstrap/
          createStorybookGame.ts
        scenes/
          StorybookScene.ts
        systems/
        entities/
        fx/
    deprecated/
      phaser-scenes/
        createLegacyGame.ts
        scenes/
    systems/
      EventBus.ts
      MissionEventPlayer.ts
      ShopState.ts
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

## 11. Flujo Phaser oficial

El frontend oficial crea Phaser solo desde `components/PhaserStage.tsx`.

```txt
main.tsx -> App -> MissionView -> PhaserStage -> createStorybookGame -> StorybookScene
```

`StorybookScene` es la escena activa del Bosque de las Silabas.

Debe mostrar:

- fondo de bosque;
- camino con niebla;
- farol apagado;
- Lumo;
- fragmentos/letras flotando;
- cubos escaneados como piezas fisicas;
- animacion de exito con luz, color y niebla desapareciendo.

El stack anterior `BootScene/MissionScene/RewardScene/VillageScene/DebugOverlay`
queda en `src/deprecated/phaser-scenes/` solo como referencia.

### Debug React

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

### Frontend oficial

```powershell
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

Dev/preview:

```txt
http://localhost:5173
http://localhost:4173
```

### Backend legacy opcional

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r arduino\requirements.txt
python arduino\sila_server.py
```

Dev servers:

```txt
FastAPI: http://localhost:5000
Vite:    http://localhost:5173
```

`frontend/` puede usar proxy hacia FastAPI si el backend esta levantado. Si no
hay backend, cae a modo local en memoria.

Division vigente:

- React/HTML/CSS: header, panel de mision, bandeja de cubos, botones, aldea,
  tienda, recursos y debug.
- Phaser 4: bosque, Lumo, farol, camino, niebla, cubos escaneados, particulas y
  microanimaciones.

### Frontend PixiJS experimental no oficial

```powershell
cd frontend-pixi
npm install
npm run dev
npm run build
```

Dev server:

```txt
PixiJS: http://localhost:5174
```

Demo empaquetada:

```txt
frontend/dist/ servido por Vite preview o hosting estatico
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

Para `frontend/`, cubrir:

- `npm run build`;
- TypeScript sin errores;
- modo local sin backend;
- integracion opcional con `/buffer` y `/ws`;
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

Es muy buen renderer, pero no es el camino oficial de esta iteracion. Se mantiene
en `frontend-pixi/` solo como alternativa experimental.

### Three.js

No corresponde al MVP porque SilaBlocks es 2D. Three.js seria util solo si el
producto decide pasar a 3D real.

### React como frontend principal

React es parte oficial del shell de `frontend/`. Phaser sigue siendo la pieza
para la escena jugable y el timing visual.

## 17. Roadmap tecnico recomendado

1. Agregar `arduino/game_state.json`, progreso y tienda.
2. Agregar `/progress`, `/shop` y `/buy`.
3. Emitir eventos visuales desde el engine.
4. Crear `frontend/` con Phaser 4 + TypeScript + Vite.
5. Mantener `StorybookScene` como escena oficial del Bosque de las Silabas.
6. Agregar efectos de recompensa dentro del flujo React/Phaser oficial.
7. Mantener `VillageView` React como tienda real hasta decidir si requiere Phaser.
8. Reemplazar placeholders por arte y audio.
9. Evaluar Rive para Lumo.
10. Considerar SQLite si el progreso crece.

## 18. Criterio de exito del stack

El stack oficial esta funcionando si:

- la demo abre desde `frontend/`;
- no requiere hardware ni backend;
- Phaser muestra el cubo como objeto en escena;
- la mision valida el progreso;
- al completar, se entrega recompensa;
- la aldea permite gastar recompensa;
- la compra queda reflejada en memoria durante la sesion;
- todo corre localmente en un PC de demo sin depender de nube.

## 19. Referencias oficiales

- Phaser 4: https://phaser.io/phaser4
- Phaser 3 vs Phaser 4: https://phaser.io/news/2026/05/phaser-3-vs-phaser-4
- Vite guide: https://vite.dev/guide/
- FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
- Rive Web runtime: https://rive.app/docs/runtimes/web
- Godot web export: https://docs.godotengine.org/en/4.5/tutorials/export/exporting_for_web.html
