# Plan frontend y loop de juego: Phaser 4 + TypeScript + Vite

Estado actual de esta iteracion: `frontend/` es la demo oficial del juego.
Debe correr sin hardware, sin NFC real y sin backend obligatorio. FastAPI,
`arduino/templates/` y `frontend-pixi/` quedan como legacy/alternativos.

## 1. Objetivo

Consolidar SilaBlocks como experiencia de juego 2D en `frontend/` con React,
Phaser 4, TypeScript y Vite. El backend FastAPI y el contrato NFC se conservan
como integracion futura, pero no son obligatorios para correr la demo oficial.

El objetivo del MVP no es construir una plataforma completa. Es cerrar un loop
jugable y demostrable:

```txt
Inicio / Mapa -> Mision -> Recompensa -> Aldea -> Siguiente mision
```

En la demo inicial puede simplificarse a:

- vista Mision dentro de `frontend/`.
- vista Aldea dentro de `frontend/`.
- debug visible, pero secundario.

## 2. Stack objetivo

- Motor visual: Phaser 4.
- Lenguaje frontend: TypeScript.
- Build/dev server: Vite.
- Backend: FastAPI + WebSocket opcional/legacy.
- Contrato NFC estable: `GET /nfc?letra=<valor>` para integracion futura.
- Animaciones especiales: spritesheets primero; Rive despues para Lumo u otras
  microinteracciones complejas.
- Diseno/prototipo: Figma.
- Arte 2D: Krita, Photoshop, Affinity Designer o Illustrator.
- Optimizacion de assets: TexturePacker.
- Audio: Audacity y sonidos con licencia revisada.

Decision para MVP: usar spritesheets/atlases y placeholders visuales antes que
Rive. Rive no debe bloquear la primera version jugable.

## 3. Separacion de responsabilidades

Para esta iteracion, `frontend/` debe funcionar como demo independiente:

- simula cubos desde botones en pantalla;
- mantiene buffer por bloques en modo local;
- valida misiones dentro del estado local de demo;
- genera eventos pedagogicos y visuales;
- permite probar aldea y compras sin servidor.

FastAPI puede volver a ser fuente de verdad cuando se retome hardware o
persistencia real, pero no debe bloquear la demo React/Phaser.

Phaser no valida respuestas. Phaser interpreta estado y eventos para animar:

- escenas;
- cubos escaneados;
- objetos restaurados;
- recompensas;
- aldea/tienda;
- transiciones.

Arquitectura objetivo:

```txt
Botones de cubos en frontend/
   |
localDemoState
   |- buffer por bloques
   |- engine local de demo
   |- progreso local en memoria
   |- tienda local
   |- eventos
   |
Frontend Phaser
   |- PhaserStage
   |- createStorybookGame
   |- StorybookScene
   |- sceneBus
```

## 4. Contrato backend legacy que no se debe romper

Mantener:

- `GET /health`
- `GET /buffer`
- `GET /nfc?letra=<valor>`
- `POST /nfc`
- `DELETE /buffer`
- `WebSocket /ws`

El input normal agrega bloques. `BORRAR`, `DELETE` y `BACKSPACE` eliminan el
ultimo bloque. `RESET` limpia el estado de la mision actual. `ENTER` valida o
confirma la accion actual.

Decision vigente del MVP: los bloques principales son letras individuales. La
arquitectura permite silabas o palabras completas mas adelante, pero el primer
frontend Phaser debe asumir letras para `target_blocks` y `current_blocks`.

`available_blocks` debe seguir siendo guia visual. No conviene volver a filtrar
duro los inputs del backend porque el hardware real puede enviar cubos distintos
durante pruebas.

## 5. Persistencia local

Agregar persistencia simple en:

```txt
arduino/game_state.json
```

Debe guardar:

- Lumenes disponibles;
- Fragmentos disponibles;
- misiones completadas;
- compras realizadas;
- zonas desbloqueadas;
- elementos restaurados.

No se necesita base de datos todavia. Para el MVP basta un archivo JSON local
con lectura/escritura explicita y tests de persistencia.

Estructura sugerida:

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
decoraciones y aldea sin bloquear la demo por falta de recursos.

## 6. Eventos visuales de mision

El engine no debe devolver solo `success` o `try_again`. Debe emitir eventos que
Phaser pueda animar sin mezclar logica visual con logica pedagogica.

Eventos base:

- `block_scanned`
- `partial_progress`
- `wrong_block`
- `mission_completed`
- `reward_granted`
- `scene_restored`

Ejemplo de payload:

```json
{
  "status": "success",
  "feedback": "Encontraste la palabra.",
  "events": [
    { "type": "block_scanned", "value": "A" },
    { "type": "mission_completed", "mission_id": "forest_lantern" },
    { "type": "reward_granted", "lumens": 8, "fragments": 0 },
    { "type": "scene_restored", "item": "small_lantern" }
  ]
}
```

Regla clave: el estado de juego decide que paso; Phaser decide como se ve. En
esta iteracion ese estado puede ser local en `frontend/` o venir de FastAPI si
se levanta como integracion opcional.

## 7. Bosque de las Silabas como primera zona

La primera escena jugable debe ser una zona concreta, no una pantalla generica.

Zona 1:

```txt
Bosque de las Silabas
```

La mision no debe verse como:

```txt
Mision 1: arma MAMA
```

Debe presentarse como:

```txt
Ayuda a Lumo a encender el farol perdido.
```

Elementos visuales:

- fondo del bosque;
- camino con niebla;
- farol apagado;
- Lumo o un guia;
- fragmentos/letras flotando;
- cubos escaneados apareciendo como piezas fisicas;
- animacion al acertar: luz, color y niebla desapareciendo.

Misiones iniciales:

| Palabra | Accion visual |
| --- | --- |
| MAMA | Enciende farol |
| PAPA | Abre camino |
| CASA | Aparece una casita |
| MESA | Se restaura una plaza |
| BOTA | Se abre ruta nueva |

En datos de mision, cada entrada deberia incluir:

- `mission_id`
- `zone_id`
- `prompt`
- `target_blocks`
- `target_text`
- `available_blocks`
- `restored_item`
- `reward_lumens`
- `reward_fragments`
- `visual_scene`

## 8. Aldea como tienda/progreso real

La aldea debe dejar de ser una vitrina. Debe permitir gastar recompensas y hacer
visible el progreso del mundo.

Acciones:

- gastar Lumenes en faroles, plantas, decoraciones, colores, mascota o efectos;
- gastar Fragmentos en abrir zonas, caminos o estructuras grandes;
- mostrar elementos bloqueados y su costo;
- reflejar compras persistentes;
- mostrar que objetos ya fueron restaurados.

Compras MVP:

| Item | Costo |
| --- | --- |
| Farol pequeno | 8 Lumenes |
| Arbol luminoso | 10 Lumenes |
| Senal restaurada | 12 Lumenes |
| Casa decorada | 15 Lumenes |
| Abrir camino al Pueblo | 1 Fragmento |
| Restaurar puente | 2 Fragmentos |

Endpoints sugeridos:

- `GET /progress`: devuelve recursos, compras, zonas y elementos restaurados.
- `GET /shop`: devuelve inventario, costos, estado bloqueado/comprado.
- `POST /buy`: compra un item si hay recursos suficientes.

`POST /buy` deberia recibir:

```json
{
  "item_id": "small_lantern"
}
```

Y responder con:

```json
{
  "ok": true,
  "progress": {
    "lumens": 2,
    "fragments": 1,
    "purchased_items": ["small_lantern"]
  },
  "events": [
    { "type": "item_purchased", "item": "small_lantern" },
    { "type": "village_restored", "item": "small_lantern" }
  ]
}
```

## 9. Estructura frontend sugerida

Crear una carpeta nueva en la raiz:

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

Durante desarrollo oficial:

```txt
Vite:    http://localhost:5173
```

Para demo empaquetada:

1. Ejecutar `npm run build` en `frontend/`.
2. Ejecutar `npm run preview` en `frontend/`.
3. Abrir `http://localhost:4173`.

Si FastAPI esta levantado, Vite puede proxificar `/nfc`, `/buffer`, `/ws`,
`/progress`, `/shop` y `/buy`. Si no esta levantado, el frontend debe seguir en
modo local.

## 10. Flujo Phaser oficial

`PhaserStage` es el unico componente que crea `Phaser.Game`.

```txt
main.tsx -> App -> MissionView -> PhaserStage -> createStorybookGame -> StorybookScene
```

### StorybookScene

- Renderiza Bosque de las Silabas.
- Recibe estado desde React mediante `sceneBus`.
- Convierte eventos del estado de juego en animaciones.
- Dibuja cubos segun `current_blocks`.
- Deja UI, controles, debug y aldea a React.

El stack anterior `BootScene/MissionScene/RewardScene/VillageScene/DebugOverlay`
esta conservado en `src/deprecated/phaser-scenes/` y no debe recibir trabajo
nuevo.

### Debug React

Debe estar disponible para demo, pero no dominar la pantalla.

Mostrar:

- WebSocket conectado/desconectado;
- ultimo input recibido;
- bloques actuales;
- texto unido;
- mision;
- estado;
- eventos recientes;
- recursos actuales;
- botones manuales para cubos y comandos.

## 11. Orden ideal de implementacion adaptado al stack

### Fase 1: Demo local en frontend/

- Mantener estado local en memoria.
- Crear inventario de recompensas/compras para la demo.
- Permitir completar misiones sin backend.
- Permitir comprar en la aldea sin backend.
- Mantener FastAPI solo como integracion opcional.

Criterio de aceptacion:

- Completar una mision suma recompensas.
- Comprar descuenta Lumenes o Fragmentos.
- Una compra se ve en la aldea durante la sesion.
- `npm run build` pasa en `frontend/`.

### Fase 2: Eventos visuales en el engine

- Agregar lista `events` al estado de mision.
- Emitir `block_scanned`, `partial_progress`, `wrong_block`,
  `mission_completed`, `reward_granted` y `scene_restored`.
- Mantener `status` y `feedback` por compatibilidad.
- Agregar tests de eventos por input.

Criterio de aceptacion:

- El estado de juego comunica que paso sin depender de texto libre.
- El frontend puede animar cada cambio desde eventos.

### Fase 3: Scaffold Phaser + Vite + TypeScript

- Crear `frontend/`.
- Agregar Phaser 4, TypeScript y Vite.
- Crear `BackendClient`.
- Conectar `/buffer`, `/progress`, `/shop` y `/ws`.
- Renderizar una escena simple con estado real.

Criterio de aceptacion:

- Vite muestra una escena Phaser.
- La escena recibe cambios al usar cubos en pantalla.
- El debug muestra estado de juego real.

### Fase 4: StorybookScene del Bosque de las Silabas

- Reemplazar pantalla generica por escena Phaser.
- Agregar bosque, camino, niebla, farol, Lumo, fragmentos flotantes y cubos.
- Conectar eventos visuales a animaciones.

Criterio de aceptacion:

- Al escanear `M`, aparece un cubo fisico `M`.
- Al completar la palabra, hay luz, color y baja la niebla.
- La mision se siente como "ayudar a Lumo", no como un formulario.

### Fase 5: Efectos de recompensa

- Mostrar recompensas tras completar mision dentro del flujo oficial.
- Mostrar objeto restaurado.
- Dar salida clara hacia aldea o siguiente mision desde React.

Criterio de aceptacion:

- El nino entiende que completo una accion y gano recursos.

### Fase 6: Aldea React/Phaser como tienda real

- Convertir la vista Aldea de `frontend/` en aldea interactiva.
- Mostrar costos, bloqueos y compras realizadas.
- Usar modo local o backend opcional para comprar.
- Reflejar cambios de la sesion.

Criterio de aceptacion:

- La aldea permite gastar Lumenes/Fragmentos.
- Las compras cambian visualmente la aldea.
- En modo local, el progreso se mantiene mientras la pagina este abierta.

### Fase 7: Arte, audio y animaciones finales

- Reemplazar placeholders por arte 2D.
- Pasar sprites a TexturePacker.
- Agregar sonidos suaves.
- Evaluar Rive para Lumo.
- Pulir performance y transiciones.

## 12. Proximo cambio recomendado

El siguiente cambio practico deberia ser:

```txt
Pulir la aldea de frontend/ como lugar donde realmente se gastan Lumenes y Fragmentos.
```

Motivo: cierra el loop motivacional antes de invertir mas en arte:

```txt
mision -> recompensa -> gasto -> mundo cambia -> nueva mision
```

Implementacion concreta del siguiente PR/cambio:

- agregar `arduino/game_state.json`;
- agregar inventario de compras;
- completar el estado local de progreso, tienda y compras;
- conectar recompensas de misiones con la aldea local;
- mantener la UI HTML de FastAPI como legacy;
- agregar pruebas frontend cuando se incorpore un runner.

El scaffold Phaser ya existe en `frontend/`; el foco ahora es consolidarlo.

## 13. Riesgos

- Migrar visuales antes de persistir progreso puede dejar una aldea bonita pero
  sin loop de juego.
- Volver a presentar la UI embebida como fallback oficial crea ambiguedad. Debe
  quedar como legacy mientras `frontend/` avanza.
- Rive puede agregar complejidad temprana. Usar spritesheets primero.
- Assets finales pueden retrasar avances. Partir con placeholders y reemplazar
  despues.
- WebSocket puede fallar durante demo. Mantener carga inicial via `/buffer` y
  reconexion automatica.

## 14. No objetivos de esta etapa

- No agregar cuentas de usuario.
- No agregar nube.
- No agregar base de datos remota.
- No cambiar `/nfc?letra=...`.
- No crear rankings competitivos.
- No agregar cajas aleatorias ni mecanicas de presion.
- No bloquear la mision por arte final.

## 15. Referencias tecnicas

- Phaser 4:
  https://phaser.io/phaser4
- Phaser 3 vs Phaser 4:
  https://phaser.io/news/2026/05/phaser-3-vs-phaser-4
- Vite guide:
  https://vite.dev/guide/
- Rive runtimes:
  https://rive.app/docs/runtimes
- Phaser textures/spritesheets:
  https://docs.phaser.io/phaser/concepts/textures
