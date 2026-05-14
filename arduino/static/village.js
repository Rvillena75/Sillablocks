const ids = {
  status: document.getElementById("villageStatus"),
  completedMissions: document.getElementById("completedMissions"),
  lumens: document.getElementById("villageLumens"),
  fragments: document.getElementById("villageFragments"),
  restoredList: document.getElementById("restoredList"),
  shopList: document.getElementById("shopList"),
  shopMessage: document.getElementById("shopMessage"),
  refreshShop: document.getElementById("refreshShop"),
  houseOne: document.getElementById("houseOne"),
  houseTwo: document.getElementById("houseTwo"),
  tower: document.getElementById("tower"),
  bridge: document.getElementById("bridge"),
  signpost: document.getElementById("signpost"),
  smallLantern: document.getElementById("smallLantern"),
  glowingTree: document.getElementById("glowingTree"),
  pathToVillage: document.getElementById("pathToVillage")
};

const TOTAL_MISSIONS = 5;
const itemNames = new Map();
let refreshTimer = null;

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

function renderRestoredList(items) {
  ids.restoredList.replaceChildren();
  if (!items.length) {
    const item = document.createElement("li");
    item.textContent = "Aún no hay restauraciones.";
    ids.restoredList.appendChild(item);
    return;
  }

  items.forEach((value) => {
    const item = document.createElement("li");
    item.textContent = itemDisplayName(value);
    ids.restoredList.appendChild(item);
  });
}

function hasAny(source, values) {
  return values.some((value) => source.has(value));
}

function setRestored(element, enabled) {
  if (element) {
    element.classList.toggle("restored", enabled);
  }
}

function applyVillageScene(progress) {
  const restored = new Set(progress.restored_items || []);
  const purchased = new Set(progress.purchased_items || []);
  const unlocked = new Set(progress.unlocked_zones || []);

  setRestored(
    ids.smallLantern,
    hasAny(restored, ["small_lantern", "Farol del Bosque"]) || purchased.has("small_lantern")
  );
  setRestored(ids.glowingTree, restored.has("glowing_tree") || purchased.has("glowing_tree"));
  setRestored(
    ids.signpost,
    hasAny(restored, ["restored_sign", "Señal del Pueblo"]) || purchased.has("restored_sign")
  );
  setRestored(ids.houseTwo, restored.has("decorated_house") || purchased.has("decorated_house"));
  setRestored(ids.bridge, restored.has("restored_bridge") || purchased.has("restored_bridge"));
  setRestored(
    ids.pathToVillage,
    hasAny(restored, ["path_to_village", "Camino de Madera"])
      || purchased.has("path_to_village")
      || unlocked.has("village")
  );
  setRestored(
    ids.houseOne,
    hasAny(restored, ["Casa decorada", "Mesa de la Plaza", "decorated_house"])
      || purchased.has("decorated_house")
  );
  setRestored(
    ids.tower,
    hasAny(restored, ["Ruta del Explorador", "restored_bridge"])
      || unlocked.has("bridge_path")
  );
}

function renderProgress(progress) {
  const restored = progress.restored_items || [];
  const completed = progress.completed_missions || [];
  ids.completedMissions.textContent = `${completed.length}/${TOTAL_MISSIONS}`;
  ids.lumens.textContent = progress.lumens ?? 0;
  ids.fragments.textContent = progress.fragments ?? progress.map_fragments ?? 0;
  renderRestoredList(restored);
  applyVillageScene(progress);
}

function createShopButton(item) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "control-button shop-buy";
  button.dataset.itemId = item.item_id;

  if (item.purchased) {
    button.textContent = "Agregado";
    button.disabled = true;
  } else if (!item.affordable) {
    button.textContent = "Reunir recursos";
    button.disabled = true;
  } else {
    button.textContent = "Agregar";
    button.addEventListener("click", () => buyItem(item.item_id));
  }

  return button;
}

function renderShop(shop) {
  ids.shopList.replaceChildren();
  const items = shop.items || [];
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "shop-empty";
    empty.textContent = "No hay mejoras disponibles por ahora.";
    ids.shopList.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    itemNames.set(item.item_id, item.name);

    const card = document.createElement("article");
    card.className = "shop-item";
    card.dataset.itemId = item.item_id;
    card.dataset.category = item.category;
    card.dataset.purchased = item.purchased ? "true" : "false";
    card.dataset.affordable = item.affordable ? "true" : "false";

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
      ? "En la aldea"
      : item.affordable
        ? "Disponible"
        : "Bloqueado por recursos";

    meta.append(cost, status);
    card.append(title, description, meta, createShopButton(item));
    ids.shopList.appendChild(card);
  });
}

async function loadVillage(options = {}) {
  try {
    if (!options.silent) {
      setStatus("Actualizando");
    }
    const [progressResponse, shopResponse] = await Promise.all([
      fetch("/progress"),
      fetch("/shop")
    ]);
    if (!progressResponse.ok || !shopResponse.ok) {
      throw new Error("No se pudo cargar la aldea.");
    }

    const progress = await progressResponse.json();
    const shop = await shopResponse.json();
    renderProgress(progress);
    renderShop(shop);
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
    glowing_tree: ids.glowingTree,
    restored_sign: ids.signpost,
    decorated_house: ids.houseTwo,
    path_to_village: ids.pathToVillage,
    restored_bridge: ids.bridge,
    village: ids.pathToVillage,
    bridge_path: ids.bridge
  };

  (events || []).forEach((event) => {
    const key = event.item_id || event.zone_id;
    const element = elementByItem[key];
    if (!element) {
      return;
    }
    element.classList.remove("village-pulse");
    void element.offsetWidth;
    element.classList.add("village-pulse");
  });
}

async function buyItem(itemId) {
  setMessage("Agregando mejora a la aldea.", "info");
  try {
    const response = await fetch("/buy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId })
    });
    const payload = await response.json();
    if (payload.progress) {
      renderProgress(payload.progress);
    }

    if (!response.ok || !payload.ok) {
      setMessage(payload.message || "Aún faltan recursos para esa mejora.", "warn");
      await loadVillage({ silent: true });
      return;
    }

    setMessage(payload.message || "Mejora agregada a la aldea.", "ok");
    pulseRestoredElements(payload.events);
    await loadVillage({ silent: true });
  } catch (error) {
    setMessage("No se pudo completar la compra. Revisa el servidor.", "error");
  }
}

function connectSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.addEventListener("open", () => setStatus("Conectado"));
  socket.addEventListener("message", () => scheduleRefresh());
  socket.addEventListener("close", () => {
    setStatus("Reconectando");
    window.setTimeout(connectSocket, 1200);
  });
  socket.addEventListener("error", () => setStatus("Revisar"));
}

ids.refreshShop.addEventListener("click", () => loadVillage());
loadVillage();
connectSocket();
