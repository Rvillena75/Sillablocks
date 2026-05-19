const ids = {
  status: document.getElementById("villageStatus"),
  achievementList: document.getElementById("achievementList"),
  achievementSummary: document.getElementById("achievementSummary"),
  shopList: document.getElementById("shopList"),
  shopSummary: document.getElementById("shopSummary"),
  shopMessage: document.getElementById("shopMessage"),
  resourceLumens: document.getElementById("resourceLumens"),
  resourceFragments: document.getElementById("resourceFragments"),
  refreshShop: document.getElementById("refreshShop"),
  editVillageMode: document.getElementById("editVillageMode"),
  decorationInventoryTray: document.getElementById("decorationInventoryTray"),
  villageScene: document.querySelector(".village-scene"),
  placedDecorationsLayer: document.getElementById("placedDecorationsLayer"),
  decorationPreview: document.getElementById("decorationPreview"),
  houseOne: document.getElementById("houseOne"),
  houseTwo: document.getElementById("houseTwo"),
  tower: document.getElementById("tower"),
  bridge: document.getElementById("bridge"),
  signpost: document.getElementById("signpost"),
  smallLantern: document.getElementById("smallLantern"),
  glowingTree: document.getElementById("glowingTree"),
  pathToVillage: document.getElementById("pathToVillage"),
  villageMist: document.getElementById("villageMist"),
  villageLumo: document.getElementById("villageLumo"),
  villageLumoLine: document.getElementById("villageLumoLine"),
  missionCard: document.getElementById("villageMissionCard"),
  missionCardState: document.getElementById("missionCardState"),
  missionCardTitle: document.getElementById("missionCardTitle"),
  missionCardText: document.getElementById("missionCardText"),
  missionCardObjective: document.getElementById("missionCardObjective"),
  missionCardReward: document.getElementById("missionCardReward"),
  missionCardAction: document.getElementById("missionCardAction")
};

const TOTAL_MISSIONS = 5;
const villageTabs = Array.from(document.querySelectorAll("[data-tab-target]"));
const villageTabPanels = Array.from(document.querySelectorAll(".village-tab-panel"));
const itemNames = new Map();
const shopItemsById = new Map();
const functionalVillageObjects = [
  {
    id: "lantern_01",
    elementKey: "smallLantern",
    missionId: "m001",
    name: "Farol perdido",
    description: "Este farol olvidó su palabra. Devuélvele la luz con tus cubos.",
    restoredDescription: "El farol vuelve a iluminar la entrada del bosque.",
    lockedDescription: "El farol espera al inicio de la aventura.",
    guideLine: "Ese farol está apagado... ¿lo restauramos?",
    guideLook: "right",
    guidePosition: { lumoLeft: "25%", lumoTop: "255px", lineLeft: "31%", lineTop: "232px" },
    objective: "Forma la palabra MAMA",
    rewardLabel: "+10 Lúmenes",
    restorationKeys: ["Farol del Bosque"]
  },
  {
    id: "path_01",
    elementKey: "pathToVillage",
    missionId: "m002",
    name: "Camino dormido",
    description: "El camino de madera perdió sus pasos. Ayuda a Lumo a abrirlo.",
    restoredDescription: "El camino ya deja avanzar a Lumo por la aldea.",
    lockedDescription: "Primero enciende el farol para ver por dónde avanzar.",
    guideLine: "Creo que este camino necesita ayuda.",
    guideLook: "right",
    guidePosition: { lumoLeft: "22%", lumoTop: "394px", lineLeft: "29%", lineTop: "368px" },
    objective: "Forma la palabra PAPA",
    rewardLabel: "+10 Lúmenes",
    restorationKeys: ["Camino de Madera"]
  },
  {
    id: "sign_01",
    elementKey: "signpost",
    missionId: "m003",
    name: "Señal sin voz",
    description: "La señal quedó rota y no recuerda qué lugar indica.",
    restoredDescription: "La señal vuelve a mostrar el camino hacia el pueblo.",
    lockedDescription: "El camino debe despertar antes de llegar a esta señal.",
    guideLine: "Creo que esta señal necesita ayuda.",
    guideLook: "right",
    guidePosition: { lumoLeft: "42%", lumoTop: "238px", lineLeft: "49%", lineTop: "215px" },
    objective: "Forma la palabra CASA",
    rewardLabel: "+12 Lúmenes",
    restorationKeys: ["Señal del Pueblo"]
  },
  {
    id: "house_01",
    elementKey: "houseOne",
    missionId: "m004",
    name: "Casa de la plaza",
    description: "La casa cerró sus ventanas porque la plaza perdió su palabra.",
    restoredDescription: "La plaza vuelve a tener un rincón donde reunirse.",
    lockedDescription: "La señal del pueblo debe quedar lista antes de abrir esta casa.",
    guideLine: "Creo que esta casa necesita ayuda.",
    guideLook: "left",
    guidePosition: { lumoLeft: "29%", lumoTop: "350px", lineLeft: "8%", lineTop: "328px" },
    objective: "Forma la palabra MESA",
    rewardLabel: "+12 Lúmenes",
    restorationKeys: ["Mesa de la Plaza"]
  },
  {
    id: "bridge_01",
    elementKey: "bridge",
    missionId: "m005",
    name: "Puente de la ruta",
    description: "El puente perdió sus primeras pisadas y la ruta quedó incompleta.",
    restoredDescription: "El puente abre la primera ruta de exploración.",
    lockedDescription: "La plaza debe volver a brillar antes de cruzar este puente.",
    guideLine: "Ese puente está roto... ¿lo restauramos?",
    guideLook: "right",
    guidePosition: { lumoLeft: "34%", lumoTop: "396px", lineLeft: "41%", lineTop: "372px" },
    objective: "Forma la palabra BOTA",
    rewardLabel: "+14 Lúmenes",
    restorationKeys: ["Ruta del Explorador"]
  },
  {
    id: "tree_01",
    elementKey: "glowingTree",
    missionId: null,
    name: "Árbol luminoso seco",
    description: "Sus hojas guardan una misión para una próxima aventura.",
    restoredDescription: "El árbol aún espera su propia palabra.",
    lockedDescription: "Este rincón se abrirá después de restaurar la primera ruta.",
    guideLine: "Este árbol guarda una sorpresa para después.",
    guideLook: "left",
    guidePosition: { lumoLeft: "17%", lumoTop: "220px", lineLeft: "23%", lineTop: "196px" },
    objective: "Próxima aventura",
    rewardLabel: "Nueva luz",
    restorationKeys: ["glowing_tree"]
  },
  {
    id: "tower_01",
    elementKey: "tower",
    missionId: null,
    name: "Torre entre niebla",
    description: "La torre todavía no puede contar su historia.",
    restoredDescription: "La torre vigila la ruta restaurada.",
    lockedDescription: "La niebla se levantará en una etapa futura.",
    guideLine: "Esa torre espera otra aventura.",
    guideLook: "right",
    guidePosition: { lumoLeft: "47%", lumoTop: "260px", lineLeft: "54%", lineTop: "236px" },
    objective: "Próxima aventura",
    rewardLabel: "Nuevo camino",
    restorationKeys: ["bridge_path"]
  }
];
let refreshTimer = null;
let currentProgressSnapshot = null;
let currentGameSnapshot = null;
let selectedObjectId = null;
let knownRestoredObjectIds = null;
let placementMode = null;
let editMode = false;
let activeDragPointerId = null;
let suppressDecorationClick = false;

const lumoRestorationLines = {
  m001: "El farol volvió a brillar.",
  m002: "El camino ya se ve mucho mejor.",
  m003: "La señal recuperó su voz.",
  m004: "La casa de la plaza despertó.",
  m005: "El puente abrió la primera ruta."
};

function setStatus(value) {
  ids.status.textContent = value;
  ids.status.dataset.status = value.toLowerCase();
}

function setMessage(value, tone = "info") {
  ids.shopMessage.textContent = value;
  ids.shopMessage.dataset.tone = tone;
}

function formatCost(item) {
  const cost = item.cost || {};
  const parts = [];
  if (cost.lumens) {
    parts.push(`${cost.lumens} Lúmenes`);
  }
  if (cost.fragments) {
    parts.push(`${cost.fragments} Fragmentos`);
  }
  return parts.join(" + ") || "Sin costo";
}

function itemDisplayName(value) {
  return itemNames.get(value) || value;
}

function shopItemIcon(item) {
  const itemId = typeof item === "string" ? item : item.item_id;
  const icons = {
    small_lantern: "✦",
    glowing_tree: "✿",
    restored_sign: "▸",
    decorated_house: "▰",
    path_to_village: "╋",
    restored_bridge: "◌"
  };
  return icons[itemId] || "✦";
}

function buildAchievements(progress) {
  const completed = progress.completed_missions || [];
  const restored = progress.restored_items || [];
  const purchased = progress.purchased_items || [];
  const unlocked = progress.unlocked_zones || [];
  const fragments = progress.fragments ?? progress.map_fragments ?? 0;
  const lumens = progress.lumens ?? 0;

  return [
    {
      title: "Chispa del Bosque",
      description: "Recupera tu primera palabra perdida.",
      icon: "🏆",
      unlocked: completed.length >= 1,
      detail: completed.length >= 1 ? "Misión inicial completada" : "Falta completar una misión"
    },
    {
      title: "Explorador de Cinco Rutas",
      description: "Completa todas las misiones de la primera aventura.",
      icon: "🏅",
      unlocked: completed.length >= TOTAL_MISSIONS,
      detail: `${completed.length}/${TOTAL_MISSIONS} misiones`
    },
    {
      title: "Guardián de Lúmenes",
      description: "Reúne luz para ayudar a la aldea.",
      icon: "⭐",
      unlocked: lumens >= 10 || completed.length >= 1,
      detail: `${lumens} lúmenes disponibles`
    },
    {
      title: "Cartógrafo Pequeño",
      description: "Encuentra un fragmento de mapa.",
      icon: "💎",
      unlocked: fragments >= 1 || completed.length >= 3 || purchased.includes("path_to_village"),
      detail: `${fragments} fragmentos`
    },
    {
      title: "Manos Constructoras",
      description: "Agrega tu primera decoración a la aldea.",
      icon: "🛠",
      unlocked: purchased.length >= 1,
      detail: purchased.length ? itemDisplayName(purchased[0]) : "Sin compras todavía"
    },
    {
      title: "Llave del Camino",
      description: "Abre una ruta hacia una nueva zona.",
      icon: "🗝",
      unlocked: unlocked.some((zone) => zone !== "forest"),
      detail: unlocked.length > 1 ? `${unlocked.length} zonas` : "Solo bosque inicial"
    },
    {
      title: "Corazón de la Aldea",
      description: "Activa tres elementos visibles del mundo.",
      icon: "🏡",
      unlocked: restored.length >= 3,
      detail: `${restored.length} elementos activos`
    }
  ];
}

function renderAchievements(progress) {
  const achievements = buildAchievements(progress);
  const unlockedCount = achievements.filter((achievement) => achievement.unlocked).length;
  ids.achievementSummary.textContent = `${unlockedCount}/${achievements.length} desbloqueados`;
  ids.achievementList.replaceChildren();

  achievements.forEach((achievement) => {
    const item = document.createElement("li");
    item.className = "achievement-item";
    item.dataset.unlocked = achievement.unlocked ? "true" : "false";

    const trophy = document.createElement("div");
    trophy.className = "achievement-trophy";
    trophy.setAttribute("aria-hidden", "true");
    trophy.textContent = achievement.icon;

    const content = document.createElement("div");
    content.className = "achievement-copy";

    const title = document.createElement("strong");
    title.textContent = achievement.title;

    const description = document.createElement("span");
    description.textContent = achievement.description;

    const detail = document.createElement("small");
    detail.textContent = achievement.detail;

    content.append(title, description, detail);
    item.append(trophy, content);
    ids.achievementList.appendChild(item);
  });
}

function hasAny(source, values) {
  return values.some((value) => source.has(value));
}

function addValues(target, values) {
  (values || []).forEach((value) => target.add(value));
}

function setRestored(element, enabled) {
  if (element) {
    element.classList.toggle("restored", enabled);
  }
}

function progressMissions(progress = {}, gameState = {}) {
  const completed = new Set();
  addValues(completed, progress.completed_missions);
  addValues(completed, gameState.completed_mission_ids);
  return completed;
}

function progressRestorations(progress = {}, gameState = {}) {
  const restored = new Set();
  addValues(restored, progress.restored_items);
  addValues(restored, gameState.restored_items);
  return restored;
}

function nextMissionId(progress = {}, gameState = {}) {
  const completed = progressMissions(progress, gameState);
  const currentMissionId = gameState.mission_id;

  if (currentMissionId && !completed.has(currentMissionId)) {
    return currentMissionId;
  }

  const nextObject = functionalVillageObjects.find((object) => (
    object.missionId && !completed.has(object.missionId)
  ));
  return nextObject ? nextObject.missionId : null;
}

function nextMissionObject(progress = {}, gameState = {}) {
  const missionId = nextMissionId(progress, gameState);
  if (!missionId) {
    return null;
  }
  return functionalVillageObjects.find((object) => object.missionId === missionId) || null;
}

function objectState(object, progress = {}, gameState = {}) {
  if (!object.missionId) {
    return "locked";
  }

  const completed = progressMissions(progress, gameState);
  const restored = progressRestorations(progress, gameState);
  if (completed.has(object.missionId) || hasAny(restored, object.restorationKeys)) {
    return "restored";
  }

  return nextMissionId(progress, gameState) === object.missionId ? "damaged" : "locked";
}

function objectStateLabel(state) {
  const labels = {
    locked: "Bloqueado",
    damaged: "Necesita ayuda",
    restored: "Restaurado"
  };
  return labels[state] || "Objeto";
}

function restoredObjectIds(progress = {}, gameState = {}) {
  return functionalVillageObjects
    .filter((object) => objectState(object, progress, gameState) === "restored")
    .map((object) => object.id);
}

function selectedVillageObject(progress = {}, gameState = {}) {
  if (selectedObjectId) {
    const selected = functionalVillageObjects.find((object) => object.id === selectedObjectId);
    if (selected) {
      return selected;
    }
  }

  return functionalVillageObjects.find((object) => objectState(object, progress, gameState) === "damaged")
    || functionalVillageObjects.find((object) => objectState(object, progress, gameState) === "restored")
    || functionalVillageObjects[0];
}

function syncSelectedObjectClass() {
  functionalVillageObjects.forEach((object) => {
    const element = ids[object.elementKey];
    if (element) {
      element.classList.toggle("is-selected", selectedObjectId === object.id);
    }
  });
}

function objectElement(object) {
  return object ? ids[object.elementKey] : null;
}

function triggerVillageCelebration(object, message) {
  const element = objectElement(object);
  if (element) {
    element.classList.remove("village-pulse");
    void element.offsetWidth;
    element.classList.add("village-pulse");
  }

  ids.villageLumo.classList.remove("react", "celebrate");
  void ids.villageLumo.offsetWidth;
  ids.villageLumo.classList.add("celebrate");
  ids.villageLumoLine.textContent = message || "¡Buen trabajo! Mira cómo cambió la aldea.";
}

function lumoLineForObject(object, state, guidingObject) {
  if (!guidingObject) {
    return "¡Buen trabajo! Mira cómo cambió la aldea.";
  }

  if (!object || object.id === guidingObject.id) {
    return guidingObject.guideLine || "Creo que este lugar necesita ayuda.";
  }

  if (state === "restored") {
    return "Ese lugar ya cambió. Sigamos por acá.";
  }

  return `Faltan partes para restaurar ese lugar. Partamos por ${guidingObject.name}.`;
}

function placeLumoNearObject(object) {
  const defaultPosition = {
    lumoLeft: "18px",
    lumoTop: "20px",
    lineLeft: "88px",
    lineTop: "24px"
  };
  const position = object?.guidePosition
    ? object.guidePosition
    : defaultPosition;

  ids.villageLumo.style.setProperty("--village-lumo-left", position.lumoLeft);
  ids.villageLumo.style.setProperty("--village-lumo-top", position.lumoTop);
  ids.villageLumoLine.style.setProperty("--village-lumo-line-left", position.lineLeft);
  ids.villageLumoLine.style.setProperty("--village-lumo-line-top", position.lineTop);
}

function updateLumoGuide(object, state, progress = {}, gameState = {}) {
  const guidingObject = nextMissionObject(progress, gameState);
  placeLumoNearObject(guidingObject);
  ids.villageLumo.dataset.look = guidingObject?.guideLook || "right";
  ids.villageLumo.dataset.objectState = guidingObject ? "damaged" : "complete";
  ids.villageLumoLine.textContent = lumoLineForObject(object, state, guidingObject);

  ids.villageLumo.classList.remove("react", "celebrate");
  void ids.villageLumo.offsetWidth;
  ids.villageLumo.classList.add("react");
}

function renderMissionCard(object, progress = {}, gameState = {}) {
  if (!object || !ids.missionCard) {
    return;
  }

  const state = objectState(object, progress, gameState);
  selectedObjectId = object.id;
  syncSelectedObjectClass();
  updateLumoGuide(object, state, progress, gameState);
  ids.missionCard.hidden = false;
  ids.missionCard.dataset.objectState = state;
  ids.missionCardState.textContent = objectStateLabel(state);
  ids.missionCardTitle.textContent = object.name;
  ids.missionCardText.textContent = state === "restored"
    ? object.restoredDescription
    : state === "locked"
      ? object.lockedDescription
      : object.description;
  ids.missionCardObjective.textContent = object.objective;
  ids.missionCardReward.textContent = object.rewardLabel;
  ids.missionCardAction.textContent = "Comenzar";
  ids.missionCardAction.disabled = state !== "damaged" || !object.missionId;
  ids.missionCardAction.dataset.objectId = object.id;
}

function renderFunctionalObjects(progress = {}, gameState = {}) {
  functionalVillageObjects.forEach((object) => {
    const element = ids[object.elementKey];
    if (!element) {
      return;
    }

    const state = objectState(object, progress, gameState);
    element.classList.add("functional-object");
    element.classList.toggle("is-selected", selectedObjectId === object.id);
    element.dataset.objectId = object.id;
    element.dataset.objectState = state;
    element.dataset.missionId = object.missionId || "";
    element.setAttribute("role", "button");
    element.setAttribute("aria-label", `${object.name}: ${objectStateLabel(state)}`);
    element.setAttribute("aria-disabled", state === "locked" ? "true" : "false");
    element.tabIndex = 0;
    setRestored(element, state === "restored");
  });

  const restored = progressRestorations(progress, gameState);
  const completed = progressMissions(progress, gameState);
  const mistCleared = completed.has("m005") || restored.has("Ruta del Explorador");
  ids.villageMist.classList.toggle("restored", mistCleared);

  const currentRestored = restoredObjectIds(progress, gameState);
  if (knownRestoredObjectIds !== null) {
    currentRestored.forEach((objectId) => {
      if (knownRestoredObjectIds.has(objectId)) {
        return;
      }
      const object = functionalVillageObjects.find((item) => item.id === objectId);
      triggerVillageCelebration(object, lumoRestorationLines[object?.missionId]);
    });
  }
  knownRestoredObjectIds = new Set(currentRestored);

  renderMissionCard(selectedVillageObject(progress, gameState), progress, gameState);
}

function applyVillageScene(progress = {}, gameState = {}) {
  renderFunctionalObjects(progress, gameState);
}

function renderResources(progress = {}) {
  ids.resourceLumens.textContent = String(progress.lumens ?? 0);
  ids.resourceFragments.textContent = String(progress.fragments ?? progress.map_fragments ?? 0);
}

function placedDecorationForItem(progress = {}, itemId) {
  return (progress.placed_decorations || []).find((decoration) => decoration.item_id === itemId) || null;
}

function decorationLabel(itemId) {
  return itemNames.get(itemId) || shopItemsById.get(itemId)?.name || "Decoración";
}

function itemInventoryLabel(item) {
  const owned = item.owned_count ?? (item.purchased ? 1 : 0);
  const placed = item.placed_count ?? (item.placed ? 1 : 0);
  if (!owned) {
    return "Sin comprar";
  }
  return `${placed}/${owned} colocadas`;
}

function inventoryCounts(progress = {}, itemId) {
  const owned = (progress.purchased_items || []).filter((value) => value === itemId).length;
  const placed = (progress.placed_decorations || []).filter(
    (decoration) => decoration.item_id === itemId
  ).length;
  return {
    owned,
    placed,
    available: Math.max(owned - placed, 0)
  };
}

function renderDecorationInventory(progress = {}) {
  ids.decorationInventoryTray.replaceChildren();
  ids.decorationInventoryTray.hidden = !editMode;
  if (!editMode) {
    return;
  }

  const ownedItemIds = Array.from(new Set(progress.purchased_items || []));
  const availableItems = ownedItemIds
    .map((itemId) => ({ itemId, ...inventoryCounts(progress, itemId) }))
    .filter((item) => item.available > 0);

  if (!availableItems.length) {
    const empty = document.createElement("p");
    empty.className = "decoration-inventory-empty";
    empty.textContent = "No hay decoraciones guardadas para colocar.";
    ids.decorationInventoryTray.appendChild(empty);
    return;
  }

  availableItems.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "decoration-inventory-item";
    button.dataset.itemId = item.itemId;

    const art = document.createElement("span");
    art.className = "decoration-inventory-art";
    art.setAttribute("aria-hidden", "true");
    art.textContent = shopItemIcon(item.itemId);

    const copy = document.createElement("span");
    copy.className = "decoration-inventory-copy";
    copy.textContent = decorationLabel(item.itemId);

    const count = document.createElement("strong");
    count.textContent = `x${item.available}`;

    button.append(art, copy, count);
    button.addEventListener("click", () => startPlacement(item.itemId, { fromInventory: true }));
    ids.decorationInventoryTray.appendChild(button);
  });
}

function setEditMode(enabled) {
  editMode = enabled;
  ids.villageScene.classList.toggle("is-editing", editMode);
  ids.editVillageMode.classList.toggle("is-active", editMode);
  ids.editVillageMode.textContent = editMode ? "Salir de edición" : "Modo edición";
  ids.editVillageMode.setAttribute("aria-pressed", editMode ? "true" : "false");
  if (!editMode) {
    stopPlacement();
    setMessage("Modo edición cerrado.", "info");
  } else {
    setMessage("Modo edición: coloca, mueve o guarda tus decoraciones.", "info");
  }
  renderPlacedDecorations(currentProgressSnapshot || {});
  renderDecorationInventory(currentProgressSnapshot || {});
}

function renderPlacedDecorations(progress = {}) {
  ids.placedDecorationsLayer.replaceChildren();
  (progress.placed_decorations || []).forEach((decoration) => {
    const position = decoration.position || {};
    const itemId = decoration.item_id;

    const marker = document.createElement("div");
    marker.className = "village-decoration";
    marker.dataset.itemId = itemId;
    marker.dataset.decorationId = decoration.id;
    marker.style.left = `${position.x ?? 50}%`;
    marker.style.top = `${position.y ?? 70}%`;
    marker.setAttribute("role", "button");
    marker.setAttribute("tabindex", "0");
    marker.setAttribute("aria-label", `${decorationLabel(itemId)} colocada`);

    const art = document.createElement("span");
    art.className = "decoration-art";
    art.textContent = shopItemIcon(itemId);

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "decoration-remove";
    remove.textContent = "x";
    remove.setAttribute("aria-label", `Guardar ${decorationLabel(itemId)} en inventario`);
    remove.addEventListener("click", (event) => {
      event.stopPropagation();
      if (!editMode) {
        return;
      }
      removePlacedDecoration(decoration.id);
    });

    marker.addEventListener("pointerdown", (event) => {
      if (!editMode || event.target.closest(".decoration-remove")) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      activeDragPointerId = event.pointerId;
      suppressDecorationClick = true;
      marker.classList.add("is-dragging");
      marker.setPointerCapture(event.pointerId);
      startPlacement(itemId, { decorationId: decoration.id, drag: true });
      const position = scenePositionFromEvent(event);
      updateDecorationPreview(position, isPlacementValid(position));
      setMessage(`Arrastra ${decorationLabel(itemId)} y suelta para guardar.`, "info");
    });
    marker.addEventListener("click", (event) => {
      event.stopPropagation();
      if (suppressDecorationClick) {
        suppressDecorationClick = false;
        return;
      }
      if (editMode) {
        startPlacement(itemId, { decorationId: decoration.id });
      }
    });
    marker.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        if (editMode) {
          startPlacement(itemId, { decorationId: decoration.id });
        }
      }
    });

    marker.append(art, remove);
    ids.placedDecorationsLayer.appendChild(marker);
  });
}

function scenePositionFromEvent(event) {
  const rect = ids.villageScene.getBoundingClientRect();
  return {
    x: Math.min(100, Math.max(0, ((event.clientX - rect.left) / rect.width) * 100)),
    y: Math.min(100, Math.max(0, ((event.clientY - rect.top) / rect.height) * 100)),
    clientX: event.clientX,
    clientY: event.clientY
  };
}

function pointOverFunctionalObject(clientX, clientY) {
  return functionalVillageObjects.some((object) => {
    const element = ids[object.elementKey];
    if (!element) {
      return false;
    }
    const rect = element.getBoundingClientRect();
    const margin = 18;
    return clientX >= rect.left - margin
      && clientX <= rect.right + margin
      && clientY >= rect.top - margin
      && clientY <= rect.bottom + margin;
  });
}

function overlapsPlacedDecoration(position) {
  return (currentProgressSnapshot?.placed_decorations || []).some((decoration) => {
    if (decoration.id === placementMode?.decorationId) {
      return false;
    }
    const other = decoration.position || {};
    return Math.abs((other.x ?? 0) - position.x) < 8
      && Math.abs((other.y ?? 0) - position.y) < 8;
  });
}

function isPlacementValid(position) {
  if (position.y < 42 || position.y > 94) {
    return false;
  }
  if (pointOverFunctionalObject(position.clientX, position.clientY)) {
    return false;
  }
  return !overlapsPlacedDecoration(position);
}

function updateDecorationPreview(position, valid) {
  if (!placementMode) {
    return;
  }
  ids.decorationPreview.hidden = false;
  ids.decorationPreview.textContent = shopItemIcon(placementMode.itemId);
  ids.decorationPreview.style.left = `${position.x}%`;
  ids.decorationPreview.style.top = `${position.y}%`;
  ids.decorationPreview.dataset.valid = valid ? "true" : "false";
}

function startPlacement(itemId, options = {}) {
  if (options.fromInventory) {
    setEditMode(true);
  }
  const existing = options.decorationId
    ? (currentProgressSnapshot?.placed_decorations || []).find(
      (decoration) => decoration.id === options.decorationId
    )
    : null;
  const initial = existing?.position || { x: 50, y: 72 };

  placementMode = {
    itemId,
    decorationId: options.decorationId || null
  };
  ids.villageScene.classList.add("is-placing");
  updateDecorationPreview(
    { x: initial.x, y: initial.y, clientX: -9999, clientY: -9999 },
    true
  );
  setMessage(
    options.decorationId
      ? `Mueve ${decorationLabel(itemId)} y toca la aldea para reubicar.`
      : `Toca la aldea para colocar ${decorationLabel(itemId)}.`,
    "info"
  );
}

function stopPlacement() {
  placementMode = null;
  activeDragPointerId = null;
  suppressDecorationClick = false;
  ids.villageScene.classList.remove("is-placing");
  ids.decorationPreview.hidden = true;
  ids.decorationPreview.textContent = "";
  ids.decorationPreview.removeAttribute("data-valid");
  document.querySelectorAll(".village-decoration.is-dragging").forEach((element) => {
    element.classList.remove("is-dragging");
  });
}

async function savePlacement(position) {
  if (!placementMode) {
    return;
  }

  const isMove = Boolean(placementMode.decorationId);
  const endpoint = isMove
    ? `/decorations/${encodeURIComponent(placementMode.decorationId)}`
    : "/decorations/place";
  const method = isMove ? "PATCH" : "POST";
  const body = isMove
    ? { x: position.x, y: position.y }
    : { item_id: placementMode.itemId, x: position.x, y: position.y };

  try {
    const response = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setMessage(payload.message || "No se pudo colocar esa decoración.", "warn");
      await loadVillage({ silent: true });
      return;
    }

    stopPlacement();
    setMessage(payload.message || "Decoración colocada.", "ok");
    handleVillageEvents(payload.events);
    await loadVillage({ silent: true });
    if (editMode) {
      renderDecorationInventory(currentProgressSnapshot || {});
    }
  } catch (error) {
    setMessage("No se pudo guardar la decoración. Revisa el servidor.", "error");
  }
}

async function removePlacedDecoration(decorationId) {
  try {
    const response = await fetch(`/decorations/${encodeURIComponent(decorationId)}`, {
      method: "DELETE"
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setMessage(payload.message || "No se pudo guardar esa decoración.", "warn");
      return;
    }
    stopPlacement();
    setMessage(payload.message || "Decoración guardada en inventario.", "ok");
    await loadVillage({ silent: true });
    if (editMode) {
      renderDecorationInventory(currentProgressSnapshot || {});
    }
  } catch (error) {
    setMessage("No se pudo guardar esa decoración. Revisa el servidor.", "error");
  }
}

function renderProgress(progress = {}, gameState = {}) {
  renderResources(progress);
  renderPlacedDecorations(progress);
  renderDecorationInventory(progress);
  renderAchievements(progress);
  applyVillageScene(progress, gameState);
}

function createShopControls(item) {
  const controls = document.createElement("div");
  controls.className = "shop-actions";

  const availableToPlace = item.available_to_place ?? (item.purchased && !item.placed ? 1 : 0);

  if (availableToPlace > 0) {
    const place = document.createElement("button");
    place.type = "button";
    place.className = "control-button shop-buy";
    place.dataset.itemId = item.item_id;
    place.textContent = "Colocar";
    place.addEventListener("click", () => startPlacement(item.item_id));
    controls.appendChild(place);
  }

  const buy = document.createElement("button");
  buy.type = "button";
  buy.className = "control-button shop-buy";
  buy.dataset.itemId = item.item_id;
  if (!item.affordable) {
    buy.textContent = "Reunir recursos";
    buy.disabled = true;
  } else {
    buy.textContent = item.purchased ? "Comprar más" : "Comprar";
    buy.addEventListener("click", () => buyItem(item.item_id));
  }
  controls.appendChild(buy);

  return controls;
}

function renderShop(shop) {
  ids.shopList.replaceChildren();
  shopItemsById.clear();
  const items = shop.items || [];
  const inventoryCount = items.reduce((total, item) => total + (item.owned_count || 0), 0);
  const storedCount = items.reduce((total, item) => total + (item.available_to_place || 0), 0);
  ids.shopSummary.textContent = `${storedCount} guardadas · ${inventoryCount} compradas`;

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "shop-empty";
    empty.textContent = "No hay decoraciones disponibles por ahora.";
    ids.shopList.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    itemNames.set(item.item_id, item.name);
    shopItemsById.set(item.item_id, item);

    const card = document.createElement("article");
    card.className = "shop-item";
    card.dataset.itemId = item.item_id;
    card.dataset.category = item.category;
    card.dataset.worldKind = "decoration";
    card.dataset.purchased = item.purchased ? "true" : "false";
    card.dataset.affordable = item.affordable ? "true" : "false";

    const art = document.createElement("div");
    art.className = "shop-item-art";
    art.setAttribute("aria-hidden", "true");
    art.textContent = shopItemIcon(item);

    const copy = document.createElement("div");
    copy.className = "shop-item-copy";

    const title = document.createElement("h3");
    title.textContent = item.name;

    const description = document.createElement("p");
    description.textContent = item.description;

    const meta = document.createElement("div");
    meta.className = "shop-meta";

    const cost = document.createElement("span");
    cost.className = "shop-cost";
    cost.textContent = formatCost(item);

    const status = document.createElement("span");
    status.className = "shop-status";
    status.textContent = item.purchased
      ? itemInventoryLabel(item)
      : item.affordable
        ? "Decoración opcional"
        : "Bloqueado por recursos";

    copy.append(title, description, meta);
    meta.append(cost, status);
    card.append(art, copy, createShopControls(item));
    ids.shopList.appendChild(card);
  });
}

async function loadVillage(options = {}) {
  try {
    if (!options.silent) {
      setStatus("Actualizando");
    }
    const [progressResponse, shopResponse, gameResponse] = await Promise.all([
      fetch("/progress"),
      fetch("/shop"),
      fetch("/buffer")
    ]);
    if (!progressResponse.ok || !shopResponse.ok || !gameResponse.ok) {
      throw new Error("No se pudo cargar la aldea.");
    }

    const progress = await progressResponse.json();
    const shop = await shopResponse.json();
    const gameState = await gameResponse.json();
    currentProgressSnapshot = progress;
    currentGameSnapshot = gameState;
    renderShop(shop);
    renderProgress(progress, gameState);
    setStatus("Conectado");
    if (!options.silent) {
      setMessage("La aldea está lista.", "ok");
    }
  } catch (error) {
    setStatus("Revisar");
    setMessage("No se pudo actualizar la aldea. Revisa el servidor.", "error");
  }
}

function scheduleRefresh() {
  window.clearTimeout(refreshTimer);
  refreshTimer = window.setTimeout(() => loadVillage({ silent: true }), 120);
}

function pulseRestoredElements(events) {
  const elementByItem = {
    small_lantern: ids.smallLantern,
    "Farol del Bosque": ids.smallLantern,
    glowing_tree: ids.glowingTree,
    restored_sign: ids.signpost,
    "Señal del Pueblo": ids.signpost,
    decorated_house: ids.houseTwo,
    "Mesa de la Plaza": ids.houseOne,
    path_to_village: ids.pathToVillage,
    "Camino de Madera": ids.pathToVillage,
    restored_bridge: ids.bridge,
    "Ruta del Explorador": ids.bridge,
    village: ids.pathToVillage,
    bridge_path: ids.bridge
  };

  (events || []).forEach((event) => {
    const key = event.item || event.item_id || event.zone_id;
    const element = elementByItem[key];
    if (!element) {
      return;
    }
    element.classList.remove("village-pulse");
    void element.offsetWidth;
    element.classList.add("village-pulse");
  });
}

function handleVillageEvents(events) {
  pulseRestoredElements(events);
  (events || []).forEach((event) => {
    if (event.type !== "scene_restored" && event.type !== "mission_completed") {
      return;
    }

    const object = functionalVillageObjects.find((item) => item.missionId === event.mission_id);
    triggerVillageCelebration(object, lumoRestorationLines[event.mission_id]);
  });
}

async function buyItem(itemId) {
  setMessage("Agregando decoración al inventario.", "info");
  try {
    const response = await fetch("/buy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId })
    });
    const payload = await response.json();
    if (payload.progress) {
      currentProgressSnapshot = payload.progress;
      renderProgress(payload.progress, currentGameSnapshot || {});
    }

    if (!response.ok || !payload.ok) {
      setMessage(payload.message || "Aún faltan recursos para esa decoración.", "warn");
      await loadVillage({ silent: true });
      return;
    }

    setMessage(payload.message || "Decoración agregada al inventario. Usa Colocar cuando quieras ponerla.", "ok");
    handleVillageEvents(payload.events);
    await loadVillage({ silent: true });
  } catch (error) {
    setMessage("No se pudo completar la compra. Revisa el servidor.", "error");
  }
}

function connectSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.addEventListener("open", () => setStatus("Conectado"));
  socket.addEventListener("message", (event) => {
    try {
      const payload = JSON.parse(event.data);
      handleVillageEvents(payload.events || []);
    } catch (error) {
      // Ignore malformed socket frames and keep polling state.
    }
    scheduleRefresh();
  });
  socket.addEventListener("close", () => {
    setStatus("Reconectando");
    window.setTimeout(connectSocket, 1200);
  });
  socket.addEventListener("error", () => setStatus("Revisar"));
}

function selectVillageTab(panelId) {
  villageTabs.forEach((tab) => {
    const active = tab.dataset.tabTarget === panelId;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", active ? "true" : "false");
  });

  villageTabPanels.forEach((panel) => {
    const active = panel.id === panelId;
    panel.classList.toggle("is-active", active);
    panel.hidden = !active;
  });
}

function selectFunctionalObject(object) {
  selectedObjectId = object.id;
  renderFunctionalObjects(currentProgressSnapshot || {}, currentGameSnapshot || {});
}

function objectFromButton(button) {
  return functionalVillageObjects.find((item) => item.id === button.dataset.objectId);
}

async function selectMission(object) {
  const response = await fetch("/mission/select", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mission_id: object.missionId })
  });
  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    setMessage(payload.message || "No se pudo abrir esa misión.", "warn");
    return false;
  }

  currentGameSnapshot = payload;
  return true;
}

async function openMissionInGame(object) {
  if (!object || !object.missionId) {
    return;
  }

  setMessage(`Preparando ${object.name}.`, "info");
  const selected = await selectMission(object);
  if (!selected) {
    await loadVillage({ silent: true });
    return;
  }

  const params = new URLSearchParams({
    from: "aldea",
    mission: object.missionId
  });
  window.location.href = `/?${params.toString()}`;
}

function bindFunctionalObjects() {
  functionalVillageObjects.forEach((object) => {
    const element = ids[object.elementKey];
    if (!element) {
      return;
    }

    element.addEventListener("mouseenter", () => selectFunctionalObject(object));
    element.addEventListener("focus", () => selectFunctionalObject(object));
    element.addEventListener("click", () => selectFunctionalObject(object));
  });
}

villageTabs.forEach((tab) => {
  tab.addEventListener("click", () => selectVillageTab(tab.dataset.tabTarget));
});

ids.missionCardAction.addEventListener("click", () => {
  openMissionInGame(objectFromButton(ids.missionCardAction));
});

ids.refreshShop.addEventListener("click", () => loadVillage());
ids.editVillageMode.addEventListener("click", () => setEditMode(!editMode));
ids.villageScene.addEventListener("pointermove", (event) => {
  if (!placementMode) {
    return;
  }
  if (activeDragPointerId !== null && event.pointerId !== activeDragPointerId) {
    return;
  }
  const position = scenePositionFromEvent(event);
  updateDecorationPreview(position, isPlacementValid(position));
});
ids.villageScene.addEventListener("pointerdown", (event) => {
  if (!placementMode || activeDragPointerId !== null) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();
  const position = scenePositionFromEvent(event);
  if (!isPlacementValid(position)) {
    activeDragPointerId = null;
    updateDecorationPreview(position, false);
    document.querySelectorAll(".village-decoration.is-dragging").forEach((element) => {
      element.classList.remove("is-dragging");
    });
    setMessage("Busca un espacio libre sin tapar edificios importantes.", "warn");
    return;
  }
  savePlacement(position);
}, true);
ids.villageScene.addEventListener("pointerup", (event) => {
  if (!placementMode || activeDragPointerId !== event.pointerId) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();
  const position = scenePositionFromEvent(event);
  if (!isPlacementValid(position)) {
    updateDecorationPreview(position, false);
    setMessage("Busca un espacio libre sin tapar edificios importantes.", "warn");
    return;
  }
  savePlacement(position);
}, true);
ids.villageScene.addEventListener("pointercancel", (event) => {
  if (activeDragPointerId === event.pointerId) {
    stopPlacement();
  }
}, true);
bindFunctionalObjects();
loadVillage();
connectSocket();
