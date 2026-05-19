# Proximos pasos cercanos

Actualizado: 2026-05-14.

## Objetivo de la siguiente etapa

Consolidar el MVP actual antes de migrar a Phaser. La decision vigente es que
el MVP use cubos de letras individuales; silabas y otros tipos de bloque quedan
para iteraciones posteriores:

```txt
Mision -> recompensa -> progreso persistente -> aldea -> compra -> mundo cambia
```

El backend ya soporta este loop. Ahora conviene mejorar la experiencia visual,
automatizar chequeos de demo y preparar la migracion a Phaser 4 sin romper el
flujo NFC.

## Paso 1: Endurecer demo y setup

### Implementar

- Agregar un script de demo/reset, por ejemplo `scripts/reset_demo.ps1`.
- Agregar checklist de demo local.
- Documentar como encontrar la IP local del PC.
- Documentar flujo con telefono y flujo con RFID.
- Revisar que `RESET_TODO` sea suficiente para limpiar progreso antes de una
  presentacion.

### Criterio de aceptacion

- Se puede dejar la demo en estado inicial en un comando.
- Se puede correr healthcheck, mision, progreso y tienda desde PowerShell.
- La documentacion explica claramente que URL debe usar el telefono.

## Paso 2: Usar eventos visuales en la pantalla de mision actual

### Implementar

- Actualizar `arduino/static/app.js` para reaccionar explicitamente a:
  - `mission_completed`
  - `reward_granted`
  - `scene_restored`
- Mostrar una micro-recompensa cuando llega `reward_granted`.
- Hacer que el farol/niebla/restauracion dependan del evento, no solo de
  `status`.
- Mantener compatibilidad con el estado actual por si el evento viene vacio.

### Criterio de aceptacion

- Al completar `MAMA` con `M`, `A`, `M`, `A`, la respuesta JSON trae eventos y la pantalla anima la
  restauracion.
- Si llega una compra o restauracion por WebSocket, la UI no se desordena.
- Los tests backend siguen pasando.

## Paso 3: Pulir aldea HTML antes de Phaser

### Implementar

- Mejorar mensajes de compra:
  - compra realizada;
  - ya comprado;
  - faltan recursos;
  - item desconocido.
- Mostrar diferencias claras entre:
  - comprado;
  - disponible;
  - bloqueado por recursos.
- Agregar feedback visual mas claro cuando se restaura un objeto.
- Validar responsive en pantalla chica y pantalla de demo.

### Criterio de aceptacion

- Un usuario puede entender que necesita ganar recursos antes de comprar.
- Una compra cambia la aldea sin recargar manualmente.
- El estado persiste tras reiniciar servidor.

## Paso 4: Separar contrato de eventos para Phaser

Estado: implementado en `docs/contrato_eventos.md`.

### Implementado

- Crear documento breve `docs/contrato_eventos.md`.
- Definir estructura estable:

```json
{
  "type": "reward_granted",
  "mission_id": "m001",
  "lumens": 10,
  "fragments": 0
}
```

- Listar eventos de mision y tienda.
- Indicar que Phaser solo renderiza, no valida pedagogia.

### Criterio de aceptacion

- El frontend Phaser puede implementarse sin leer internals del backend.
- Los eventos tienen nombres estables.

## Paso 5: Crear scaffold Phaser 4 + TypeScript + Vite

Estado: app híbrida creada en `frontend/`. React/HTML/CSS maneja UI compleja y
Phaser 4 queda limitado a la escena jugable.

### Implementado

- Crear `frontend/`.
- Instalar Phaser 4, TypeScript y Vite.
- Crear:
  - `BootScene`
  - `MissionScene`
  - `VillageScene`
  - `RewardScene`
  - `DebugOverlay`
- Crear `BackendClient` para:
  - `/buffer`
  - `/progress`
  - `/shop`
  - `/buy`
  - `/ws`

### Criterio de aceptacion

- `npm run dev` levanta Vite.
- Phaser lee estado real del backend.
- La escena muestra al menos bloques actuales, recursos y eventos recientes.
- El backend FastAPI sigue funcionando en `localhost:5000`.

Nota: el HTML actual servido por FastAPI en `/` y `/aldea` se mantiene como
fallback de demo hasta que Phaser alcance paridad funcional.

## Paso 6: Migrar MissionScene al Bosque de las Silabas

Estado: en evaluacion. Existe un primer prototipo PixiJS en `frontend-pixi/`
para comparar contra Phaser antes de cerrar motor visual.

### Implementar

- Fondo de bosque.
- Camino con niebla.
- Lumo.
- Farol.
- Letras flotantes.
- Cubos fisicos escaneados.
- Animacion de exito desde eventos.

### Criterio de aceptacion

- Al escanear `M`, aparece un cubo fisico.
- Al completar la mision, se enciende el farol y baja la niebla.
- La escena se siente como "Ayuda a Lumo a encender el farol perdido", no como
  formulario de texto.

## Paso 7: Migrar aldea a Phaser

### Implementar

- Leer `/progress` y `/shop`.
- Renderizar compras como objetos de la aldea.
- Llamar `POST /buy`.
- Animar `item_purchased`, `village_restored` y `zone_unlocked`.

### Criterio de aceptacion

- La aldea Phaser mantiene paridad funcional con `/aldea` HTML.
- Las compras siguen persistiendo en `game_state.json`.

## Paso 8: Assets y audio

### Implementar

- Reemplazar placeholders por arte 2D.
- Ordenar assets por zona:
  - `forest`
  - `village`
  - `lumo`
  - `cubes`
  - `ui`
  - `audio`
- Usar TexturePacker cuando existan suficientes sprites.
- Agregar efectos suaves:
  - escaneo;
  - acierto;
  - farol;
  - compra;
  - ambiente.

### Criterio de aceptacion

- El MVP no depende de arte temporal para una presentacion.
- El audio tiene licencia revisada.

## Orden recomendado de implementacion

1. Script/checklist de demo.
2. Pantalla de mision consumiendo eventos visuales.
3. Pulido de aldea HTML.
4. Documento de contrato de eventos.
5. Scaffold Phaser 4.
6. MissionScene Phaser.
7. VillageScene Phaser.
8. Arte/audio.

## Riesgos a cuidar

- No cambiar `GET /nfc?letra=...`.
- No volver a filtrar inputs normales por `available_blocks`.
- No mover validacion pedagogica al frontend.
- No hacer que Phaser dependa de estructuras internas de Python.
- No invertir en arte final antes de asegurar estabilidad de demo.

## Definicion de listo para pasar a Phaser

Antes de migrar visualmente, deberian cumplirse estos puntos:

- Tests backend pasan.
- `/` completa al menos la primera mision.
- `/progress` persiste recompensas.
- `/shop` lista inventario real.
- `/buy` descuenta recursos y persiste compra.
- `/aldea` muestra cambios reales.
- Eventos de mision y tienda existen y estan documentados.
