# SilaBlocks

SilaBlocks es un prototipo de juego educativo para lectura inicial. Para esta
iteracion, la demo oficial del software del juego vive en:

```txt
frontend/
```

Ese frontend usa React + Phaser 4 + TypeScript + Vite. Debe poder correr sin
hardware, sin NFC real y sin levantar el backend FastAPI. Cuando FastAPI esta
disponible, el frontend puede consumir sus endpoints; cuando no esta disponible,
usa un estado local de demo en memoria.

## Camino oficial

Usa estos comandos desde la raiz del repositorio:

```powershell
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

URLs:

```txt
Dev:     http://localhost:5173
Preview: http://localhost:4173
```

El flujo oficial para esta iteracion es software-only:

```txt
Abrir frontend -> elegir cubos en pantalla -> completar mision -> ver feedback -> entrar a aldea
```

No se requiere telefono, Arduino, lector RFID, NFC Tools ni servidor Python para
probar la demo React/Phaser.

## Que contiene frontend/

- React maneja header, paneles, bandeja de cubos, aldea, tienda y debug.
- Phaser renderiza la escena jugable del bosque dentro de `PhaserStage`.
- `frontend/src/game/state/localDemoState.ts` mantiene un estado local en memoria para
  que la demo corra sin backend.
- `frontend/src/api/backendClient.ts` intenta usar FastAPI si existe y cae al
  modo local si no hay backend.
- El flujo Phaser oficial es `MissionView -> PhaserStage -> createStorybookGame
  -> StorybookScene`; el stack anterior vive en
  `frontend/src/deprecated/phaser-scenes/` como referencia legacy.

Ver detalles especificos en [frontend/README.md](frontend/README.md).

## Legacy y alternativas

Estos caminos se conservan por compatibilidad, pruebas o referencia, pero no son
la demo oficial de esta iteracion:

- `arduino/sila_server.py`: backend FastAPI legacy/compatible para integracion
  futura con hardware y persistencia local.
- `arduino/templates/` y `arduino/static/`: UI embebida legacy servida por
  FastAPI en `/` y `/aldea`.
- `frontend-pixi/`: experimento visual alternativo con PixiJS. No es el camino
  oficial.
- `scripts/reset_demo.ps1`: utilidad legacy para resetear la demo FastAPI.

No borres esos caminos todavia; pueden servir para integracion posterior, pruebas
de contrato o comparacion visual.

## Backend opcional

Si se quiere probar la integracion legacy con FastAPI:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r arduino\requirements.txt
python arduino\sila_server.py
```

Servidor:

```txt
http://localhost:5000
```

Con el backend activo, `frontend/` usa el proxy de Vite para `/buffer`,
`/progress`, `/shop`, `/buy`, `/nfc`, `/mission`, `/decorations` y `/ws`.

## Verificacion

Frontend oficial:

```powershell
cd frontend
npm run build
```

Backend legacy, solo si se toca esa capa:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp C:\tmp\sillablocks-pytest
```

## Estructura relevante

```txt
.
├── frontend/                 # demo oficial React + Phaser
├── frontend-pixi/            # alternativa PixiJS, no oficial
├── arduino/                  # backend/UI embebida legacy + hardware futuro
│   ├── sila_server.py
│   ├── templates/
│   ├── static/
│   └── game/
├── docs/
├── scripts/
└── tests/
```

## Reglas de esta iteracion

- `frontend/` es la unica demo oficial.
- No implementar hardware, NFC real ni backend obligatorio.
- No redisenar visualmente todavia.
- Mantener backend, UI embebida y PixiJS como legacy/alternativos sin borrarlos.
- La prueba minima de cierre es `npm run build` dentro de `frontend/`.
