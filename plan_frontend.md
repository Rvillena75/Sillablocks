# Plan frontend y loop de juego: Phaser 4 + TypeScript + Vite

## 1. Objetivo

Evolucionar SilaBlocks desde el prototipo visual HTML/CSS hacia una experiencia
de juego 2D con Phaser 4, TypeScript y Vite, sin romper el backend FastAPI ni el
contrato NFC actual.

El objetivo del MVP no es construir una plataforma completa. Es cerrar un loop
jugable y demostrable:

```txt
Inicio / Mapa -> Mision -> Recompensa -> Aldea -> Siguiente mision
```

En la demo inicial puede simplificarse a:

- `/`: mision actual.
- `/aldea`: tienda/progreso.
- debug visible, pero secundario.

## 2. Stack objetivo

- Motor visual: Phaser 4.
- Lenguaje frontend: TypeScript.
- Build/dev server: Vite.
- Backend: FastAPI + WebSocket.
- Contrato NFC estable: `GET /nfc?letra=<valor>`.
- Animaciones especiales: spritesheets primero; Rive despues para Lumo u otras
  microinteracciones complejas.
- Diseno/prototipo: Figma.
- Arte 2D: Krita, Photoshop, Affinity Designer o Illustrator.
- Optimizacion de assets: TexturePacker.
- Audio: Audacity y sonidos con licencia revisada.

Decision para MVP: usar spritesheets/atlases y placeholders visuales antes que
Rive. Rive no debe bloquear la primera version jugable.

## 3. Separacion de responsabilidades

FastAPI sigue siendo la fuente de verdad:

- recibe NFC desde telefono o RFID;
- mantiene el buffer por bloques;
- valida misiones;
- genera eventos pedagogicos y visuales;
- administra recompensas;
- persiste progreso local;
- expone WebSocket y endpoints de estado.

Phaser no valida respuestas. Phaser interpreta estado y eventos para animar:

- escenas;
- cubos escaneados;
- objetos restaurados;
- recompensas;
- aldea/tienda;
- transiciones.

Arquitectura objetivo:

```txt
Cubos NFC/RFID
   |
Telefono o puente serial
   |
GET /nfc?letra=...
   |
FastAPI
   |- buffer por bloques
   |- engine de misiones
   |- progreso local
   |- tienda
   |- WebSocket /ws
   |
Frontend Phaser
   |- BootScene
   |- MapScene
   |- MissionScene
   |- RewardScene
   |- VillageScene
   |- DebugOverlay
```

## 4. Contrato backend que no se debe romper

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
  "lumens": 0,
  "fragments": 0,
  "completed_missions": [],
  "purchased_items": [],
  "unlocked_zones": ["forest"],
  "restored_items": []
}
```

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
    { "type": "block_scanned", "value": "MA" },
    { "type": "mission_completed", "mission_id": "forest_lantern" },
    { "type": "reward_granted", "lumens": 8, "fragments": 0 },
    { "type": "scene_restored", "item": "small_lantern" }
  ]
}
```

Regla clave: el backend decide que paso; Phaser decide como se ve.

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

Durante desarrollo:

```txt
FastAPI: http://localhost:5000
Vite:    http://localhost:5173
```

Para demo empaquetada:

1. Ejecutar `npm run build` en `frontend/`.
2. Servir `frontend/dist/` desde FastAPI.
3. Mantener `/nfc`, `/buffer`, `/ws`, `/progress`, `/shop` y `/buy` en el mismo
   origen.

## 10. Escenas Phaser

### BootScene

- Carga assets base.
- Inicializa `BackendClient`.
- Lee `/buffer` y `/progress`.
- Pasa a `MissionScene` o `MapScene`.

### MapScene

- Muestra zonas desbloqueadas.
- Permite entrar a la mision actual.
- Puede ser minimal para el MVP.

### MissionScene

- Renderiza Bosque de las Silabas.
- Escucha WebSocket.
- Convierte eventos del backend en animaciones.
- Dibuja cubos fisicos segun `current_blocks`.
- Mantiene debug secundario.

### RewardScene

- Muestra Lumenes/Fragmentos ganados.
- Muestra objeto restaurado.
- Permite ir a aldea o siguiente mision.

### VillageScene

- Consume `/progress` y `/shop`.
- Renderiza compras disponibles.
- Llama `POST /buy`.
- Actualiza la aldea segun compras persistidas.

### DebugOverlay

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

### Fase 1: Persistencia y tienda en FastAPI

- Crear `arduino/game_state.json`.
- Agregar modelo de progreso local.
- Crear inventario de recompensas/compras.
- Agregar `GET /progress`.
- Agregar `GET /shop`.
- Agregar `POST /buy`.
- Agregar tests de compra, gasto, persistencia y desbloqueo.

Criterio de aceptacion:

- Completar una mision suma recompensas.
- Comprar descuenta Lumenes o Fragmentos.
- Una compra queda guardada al reiniciar el servidor.
- `/nfc?letra=...` sigue funcionando igual.

### Fase 2: Eventos visuales en el engine

- Agregar lista `events` al estado de mision.
- Emitir `block_scanned`, `partial_progress`, `wrong_block`,
  `mission_completed`, `reward_granted` y `scene_restored`.
- Mantener `status` y `feedback` por compatibilidad.
- Agregar tests de eventos por input.

Criterio de aceptacion:

- El backend comunica que paso sin depender de texto libre.
- El frontend puede animar cada cambio desde eventos.

### Fase 3: Scaffold Phaser + Vite + TypeScript

- Crear `frontend/`.
- Agregar Phaser 4, TypeScript y Vite.
- Crear `BackendClient`.
- Conectar `/buffer`, `/progress`, `/shop` y `/ws`.
- Renderizar una escena simple con estado real.

Criterio de aceptacion:

- Vite muestra una escena Phaser.
- La escena recibe cambios al escanear cubos.
- El debug muestra estado backend real.

### Fase 4: MissionScene del Bosque de las Silabas

- Reemplazar pantalla generica por escena Phaser.
- Agregar bosque, camino, niebla, farol, Lumo, fragmentos flotantes y cubos.
- Conectar eventos visuales a animaciones.

Criterio de aceptacion:

- Al escanear `MA`, aparece un cubo fisico `MA`.
- Al completar la palabra, hay luz, color y baja la niebla.
- La mision se siente como "ayudar a Lumo", no como un formulario.

### Fase 5: RewardScene

- Mostrar recompensas tras completar mision.
- Mostrar objeto restaurado.
- Dar salida clara hacia aldea o siguiente mision.

Criterio de aceptacion:

- El nino entiende que completo una accion y gano recursos.

### Fase 6: VillageScene como tienda real

- Convertir `/aldea` en aldea interactiva.
- Mostrar costos, bloqueos y compras realizadas.
- Llamar `POST /buy`.
- Reflejar cambios persistentes.

Criterio de aceptacion:

- La aldea permite gastar Lumenes/Fragmentos.
- Las compras cambian visualmente la aldea.
- El progreso se mantiene al reiniciar.

### Fase 7: Arte, audio y animaciones finales

- Reemplazar placeholders por arte 2D.
- Pasar sprites a TexturePacker.
- Agregar sonidos suaves.
- Evaluar Rive para Lumo.
- Pulir performance y transiciones.

## 12. Proximo cambio recomendado

El siguiente cambio practico deberia ser:

```txt
Convertir la aldea en un lugar donde realmente se gastan Lumenes y Fragmentos.
```

Motivo: cierra el loop motivacional antes de invertir mas en arte:

```txt
mision -> recompensa -> gasto -> mundo cambia -> nueva mision
```

Implementacion concreta del siguiente PR/cambio:

- agregar `arduino/game_state.json`;
- agregar inventario de compras;
- agregar `/progress`, `/shop` y `/buy`;
- conectar recompensas de misiones con progreso persistente;
- actualizar `/aldea` actual para usar datos reales, aunque todavia sea HTML;
- agregar tests backend para compra, recursos insuficientes y persistencia.

Despues de eso conviene crear el scaffold Phaser.

## 13. Riesgos

- Migrar visuales antes de persistir progreso puede dejar una aldea bonita pero
  sin loop de juego.
- Migrar todo a Phaser de una vez puede romper la demo NFC. Mantener HTML actual
  como fallback hasta que Phaser sea estable.
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
