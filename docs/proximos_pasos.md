# Proximos pasos cercanos

Actualizado: 2026-05-23.

## Objetivo de la siguiente etapa

Consolidar `frontend/` como la demo oficial React + Phaser. La decision vigente
para esta iteracion es trabajar solo en software del juego: sin hardware, sin NFC
real y sin backend obligatorio.

```txt
Abrir frontend -> elegir cubos en pantalla -> completar mision -> ver feedback -> entrar a aldea
```

FastAPI puede seguir existiendo como integracion legacy/opcional, pero no debe
ser el camino recomendado para correr la demo.

## Paso 1: Consolidar demo React/Phaser

### Implementar

- Mantener `frontend/` como unico camino oficial.
- Mantener comandos oficiales en README raiz y `frontend/README.md`.
- Verificar que `npm run build` pase dentro de `frontend/`.
- Mantener modo local sin backend obligatorio.

### Criterio de aceptacion

- `cd frontend && npm run dev` abre la demo oficial.
- La demo corre sin FastAPI, telefono, NFC Tools, Arduino ni RFID.
- PixiJS y UI embebida aparecen solo como legacy/alternativos.

## Paso 2: Pulir loop de mision en frontend/

### Implementar

- Mejorar el modo local de `frontend/src/game/state/localDemoState.ts`.
- Alinear los eventos locales con los eventos que ya emite FastAPI.
- Mantener Phaser como capa visual, sin mover validacion pedagogica a la escena.

### Criterio de aceptacion

- Al completar `MAMA` con botones en pantalla, Phaser actualiza la escena.
- Al no existir backend, la app no queda bloqueada cargando.
- `npm run build` sigue pasando.

## Paso 3: Pulir aldea React

### Implementar

- Mejorar mensajes de compra en `frontend/src/components/VillageView.tsx`:
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
- En modo local, el estado dura mientras la pagina siga abierta.

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

## Paso 5: Scaffold Phaser 4 + TypeScript + Vite

Estado: app híbrida creada en `frontend/`. React/HTML/CSS maneja UI compleja y
Phaser 4 queda limitado a la escena jugable.

### Implementado

- Crear `frontend/`.
- Instalar Phaser 4, TypeScript y Vite.
- Definir el flujo oficial `MissionView -> PhaserStage -> createStorybookGame
  -> StorybookScene`.
- Mover el stack anterior `BootScene/MissionScene/VillageScene/RewardScene` a
  `frontend/src/deprecated/phaser-scenes/`.
- Crear `BackendClient` para backend opcional y modo local:
  - `/buffer`
  - `/progress`
  - `/shop`
  - `/buy`
  - `/ws`

### Criterio de aceptacion

- `npm run dev` levanta Vite.
- Phaser lee estado local sin backend obligatorio.
- La escena oficial muestra bloques actuales y responde al estado React.
- Si FastAPI corre en `localhost:5000`, el frontend puede usarlo como integracion
  opcional.

Nota: el HTML servido por FastAPI en `/` y `/aldea` queda como UI embebida
legacy. No es fallback oficial para esta iteracion.

## Paso 6: Consolidar StorybookScene del Bosque de las Silabas

Estado: Phaser en `frontend/` es el camino oficial. `frontend-pixi/` queda como
alternativa experimental no oficial.

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

- Leer progreso y tienda desde modo local o backend opcional.
- Renderizar compras como objetos de la aldea.
- Animar `item_purchased`, `village_restored` y `zone_unlocked`.

### Criterio de aceptacion

- La aldea React/Phaser no depende de `/aldea` HTML.
- Las compras funcionan en modo local sin servidor.

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

1. Demo oficial en `frontend/`.
2. Modo local sin backend obligatorio.
3. Pulido de aldea React.
4. Documento de contrato de eventos.
5. Scaffold Phaser 4.
6. StorybookScene Phaser.
7. Aldea React con posibles efectos Phaser puntuales.
8. Arte/audio.

## Riesgos a cuidar

- No presentar `frontend-pixi/` ni `arduino/templates/` como camino oficial.
- No hacer obligatorio FastAPI para probar `frontend/`.
- No mover validacion pedagogica al frontend.
- No hacer que Phaser dependa de estructuras internas de Python.
- No invertir en arte final antes de asegurar estabilidad de demo.

## Definicion de listo para esta iteracion

Para cerrar esta iteracion, deberian cumplirse estos puntos:

- `frontend/` esta documentado como demo oficial.
- `npm run build` pasa dentro de `frontend/`.
- La app corre sin backend obligatorio.
- Backend FastAPI, UI embebida y PixiJS quedan documentados como
  legacy/alternativos.
