# Contrato de eventos para Phaser

Actualizado: 2026-05-19.

## Objetivo

Este contrato define la frontera entre el backend FastAPI y el frontend Phaser.

Regla principal:

```txt
FastAPI decide que ocurrio.
Phaser decide como se ve.
```

Phaser no debe validar respuestas, calcular recompensas ni decidir compras.
Debe leer estado desde los endpoints existentes, escuchar `WebSocket /ws` y
convertir eventos en animaciones.

## Estado base de mision

Fuente principal:

```txt
GET /buffer
WebSocket /ws
```

Campos que Phaser puede consumir:

```json
{
  "ok": true,
  "current_blocks": ["M", "A"],
  "current_text": "MA",
  "last_input": "A",
  "last_received_input": "A",
  "last_ignored_input": null,
  "action": "append",
  "mission_id": "m001",
  "mission_number": 1,
  "total_missions": 5,
  "completed_mission_ids": [],
  "prompt": "Ayuda a Lumo a encender el farol perdido.",
  "target_text": "MAMA",
  "target_blocks": ["M", "A", "M", "A"],
  "available_blocks": ["M", "A", "P", "S"],
  "status": "in_progress",
  "feedback": "Vas bien. Falta una parte.",
  "progress_percent": 50,
  "expected_next_block": "M",
  "zone": "Bosque de las Sílabas",
  "skill": "letras individuales",
  "restoration": "Farol del Bosque",
  "lumens": 99,
  "map_fragments": 99,
  "events": []
}
```

## Decisiones vigentes del MVP

- El MVP usa cubos de letras individuales.
- `current_blocks` y `target_blocks` deben interpretarse como bloques fisicos,
  no como caracteres derivados del texto.
- El backend puede aceptar valores normales fuera de `available_blocks`.
- `available_blocks` es guia visual, no filtro duro.
- El progreso de demo parte con 99 Lumenes y 99 Fragmentos para probar tienda y
  decoraciones.

## Estados de mision

| Estado | Significado visual sugerido |
| --- | --- |
| `idle` | Esperando primer cubo. |
| `in_progress` | Avance correcto parcial. |
| `try_again` | La combinacion necesita ajuste. |
| `success` | Mision completada. |
| `demo_complete` | Todas las misiones del MVP completadas. |

## Eventos de mision

### `mission_completed`

Se emite cuando una mision queda completada por primera vez.

```json
{
  "type": "mission_completed",
  "mission_id": "m001",
  "target_text": "MAMA"
}
```

Uso en Phaser:

- activar celebracion breve;
- bloquear nuevos cubos visuales hasta `SIGUIENTE`;
- mostrar salida hacia recompensa o aldea.

### `reward_granted`

Se emite cuando el backend entrega recursos por completar una mision.

```json
{
  "type": "reward_granted",
  "mission_id": "m001",
  "lumens": 10,
  "fragments": 0
}
```

Uso en Phaser:

- animar contador de Lumenes/Fragmentos;
- mostrar micro-recompensa;
- preparar `RewardScene`.

### `scene_restored`

Se emite cuando una mision restaura un objeto funcional del mundo.

```json
{
  "type": "scene_restored",
  "mission_id": "m001",
  "item": "Farol del Bosque"
}
```

Uso en Phaser:

- encender farol;
- despejar niebla;
- activar objeto restaurado en mapa o aldea.

## Eventos de tienda y aldea

Fuente principal:

```txt
POST /buy
WebSocket /ws
```

### `item_purchased`

```json
{
  "type": "item_purchased",
  "item_id": "small_lantern",
  "name": "Farol de luciernagas",
  "spent": {
    "lumens": 6,
    "fragments": 0
  }
}
```

Uso en Phaser:

- agregar item al inventario visual;
- animar gasto de recursos;
- refrescar `/progress` y `/shop`.

### `decoration_placed`

```json
{
  "type": "decoration_placed",
  "decoration": {
    "id": "decor_001",
    "item_id": "small_lantern",
    "position": { "x": 46, "y": 74 },
    "rotation": 0,
    "scale": 1
  }
}
```

Uso en Phaser:

- crear decoracion en la aldea;
- persistir la posicion visual desde `/progress`.

### `decoration_moved`

```json
{
  "type": "decoration_moved",
  "decoration": {
    "id": "decor_001",
    "item_id": "small_lantern",
    "position": { "x": 62, "y": 81 },
    "rotation": 0,
    "scale": 1
  }
}
```

### `decoration_removed`

```json
{
  "type": "decoration_removed",
  "decoration": {
    "id": "decor_001",
    "item_id": "small_lantern",
    "position": { "x": 62, "y": 81 },
    "rotation": 0,
    "scale": 1
  }
}
```

## Endpoints que Phaser debe usar

| Endpoint | Uso |
| --- | --- |
| `GET /health` | Verificar backend. |
| `GET /buffer` | Cargar estado de mision inicial o fallback si falla WebSocket. |
| `GET /progress` | Recursos, misiones completadas, compras y decoraciones. |
| `GET /shop` | Inventario y disponibilidad de compra. |
| `GET /nfc?letra=<valor>` | Simulacion manual de cubos/comandos en debug. |
| `POST /buy` | Comprar decoraciones desde aldea. |
| `POST /mission/select` | Abrir una mision desde la aldea. |
| `WebSocket /ws` | Actualizaciones en tiempo real. |

## Reglas para el frontend Phaser

- No duplicar reglas pedagogicas.
- No inferir recompensas desde texto libre.
- No mutar progreso localmente; refrescar desde `/progress`.
- No asumir que `available_blocks` limita lo que puede llegar desde hardware.
- Mantener reconexion WebSocket.
- Mantener un fallback por polling o recarga de `/buffer`.
- Mantener visible un debug overlay durante el MVP.
- Mantener el HTML actual de FastAPI como fallback de demo hasta que Phaser
  alcance paridad funcional.

