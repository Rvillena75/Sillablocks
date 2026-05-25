# SilaBlocks React/Phaser Demo

Esta carpeta contiene la demo oficial del juego SilaBlocks para esta iteracion.
Corre como una app web React + Phaser 4 + TypeScript + Vite.

## Comandos oficiales

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

## Alcance

- No requiere hardware.
- No requiere telefono, NFC Tools, Arduino ni lector RFID.
- No requiere levantar FastAPI para probar la demo.
- Usa botones en pantalla para simular cubos.
- Usa estado local en memoria cuando no hay backend.

## Arquitectura local

- `src/App.tsx`: shell React, cambio entre mision y aldea, conexion de acciones.
- `src/components/`: UI React para mision, aldea, tienda, cubos y debug.
- `src/game/phaser/`: escena Phaser oficial montada dentro de React.
- `src/game/bridge/`: puente de eventos entre React y Phaser.
- `src/game/state/localDemoState.ts`: estado local standalone para correr sin backend.
- `src/deprecated/phaser-scenes/`: stack Phaser anterior, conservado como referencia.
- `src/api/backendClient.ts`: cliente que usa FastAPI si existe y cae a demo local.
- `public/assets/storybook/`: assets SVG temporales de la escena.

Flujo Phaser oficial:

```txt
main.tsx -> App -> MissionView -> PhaserStage -> createStorybookGame -> StorybookScene
```

`PhaserStage` es el unico lugar que debe crear una instancia de `Phaser.Game`.
Al desmontarse, destruye esa instancia con `destroy(true)`.

## Backend opcional

Si FastAPI esta corriendo en `http://localhost:5000`, Vite proxifica las rutas
`/buffer`, `/progress`, `/shop`, `/buy`, `/nfc`, `/mission`, `/decorations` y
`/ws`. Si no hay backend, la app sigue funcionando en modo local.

## Verificacion

```powershell
npm run build
```

No hay lint, Vitest ni Playwright configurados todavia. Para esta etapa, el build
TypeScript/Vite es el chequeo oficial.
