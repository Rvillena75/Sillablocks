const commands = ["BORRAR", "RESET", "ENTER", "SIGUIENTE", "ANTERIOR"];

const ids = {
  body: document.body,
  missionScene: document.getElementById("missionScene"),
  socketStatus: document.getElementById("socketStatus"),
  missionCounter: document.getElementById("missionCounter"),
  skillLabel: document.getElementById("skillLabel"),
  prompt: document.getElementById("prompt"),
  targetText: document.getElementById("targetText"),
  progressFill: document.getElementById("progressFill"),
  blockTray: document.getElementById("blockTray"),
  feedback: document.getElementById("feedback"),
  availableButtons: document.getElementById("availableButtons"),
  commandButtons: document.getElementById("commandButtons"),
  floatingLetters: document.getElementById("floatingLetters"),
  zoneLabel: document.getElementById("zoneLabel"),
  lumens: document.getElementById("lumens"),
  mapFragments: document.getElementById("mapFragments"),
  restoredCount: document.getElementById("restoredCount"),
  debugReceived: document.getElementById("debugReceived"),
  debugInput: document.getElementById("debugInput"),
  debugBlocks: document.getElementById("debugBlocks"),
  debugText: document.getElementById("debugText"),
  debugMission: document.getElementById("debugMission"),
  debugStatus: document.getElementById("debugStatus"),
  debugNext: document.getElementById("debugNext"),
  debugSocket: document.getElementById("debugSocket")
};

let previousStatus = "idle";

function setSocketStatus(value) {
  ids.socketStatus.textContent = value;
  ids.debugSocket.textContent = value.toLowerCase();
  ids.socketStatus.dataset.status = value.toLowerCase();
}

function createButton(value, variant = "block") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `control-button ${variant}`;
  button.textContent = value;
  button.addEventListener("click", () => sendNfc(value));
  return button;
}

function renderButtons(values) {
  ids.availableButtons.replaceChildren();
  values.forEach((value) => ids.availableButtons.appendChild(createButton(value)));

  ids.commandButtons.replaceChildren();
  commands.forEach((value) => {
    const variant = value === "SIGUIENTE" ? "command primary" : "command";
    ids.commandButtons.appendChild(createButton(value, variant));
  });
}

function renderBlocks(blocks) {
  ids.blockTray.replaceChildren();
  if (!blocks.length) {
    const empty = document.createElement("span");
    empty.className = "empty-block";
    empty.textContent = "Pon los cubos en el camino";
    ids.blockTray.appendChild(empty);
    return;
  }

  blocks.forEach((block, index) => {
    const chip = document.createElement("span");
    chip.className = "block-chip physical-cube";
    chip.style.setProperty("--cube-index", index);
    chip.textContent = block;
    ids.blockTray.appendChild(chip);
  });
}

function renderFloatingLetters(payload) {
  const letters = [...new Set([...(payload.target_blocks || []), ...(payload.available_blocks || [])])];
  ids.floatingLetters.replaceChildren();
  letters.slice(0, 6).forEach((value, index) => {
    const letter = document.createElement("span");
    letter.className = "floating-letter";
    letter.textContent = value;
    letter.style.setProperty("--float-index", index);
    ids.floatingLetters.appendChild(letter);
  });
}

function renderScene(payload) {
  const restored = payload.restored_items || [];
  ids.zoneLabel.textContent = payload.zone || "Bosque de las Sílabas";
  ids.lumens.textContent = payload.lumens ?? 0;
  ids.mapFragments.textContent = payload.map_fragments ?? 0;
  ids.restoredCount.textContent = restored.length;
  ids.body.dataset.status = payload.status || "idle";
  ids.missionScene.dataset.status = payload.status || "idle";
  ids.missionScene.classList.toggle("has-blocks", (payload.current_blocks || []).length > 0);

  if ((payload.status === "success" || payload.status === "demo_complete") && previousStatus !== payload.status) {
    ids.missionScene.classList.remove("celebrate");
    window.requestAnimationFrame(() => ids.missionScene.classList.add("celebrate"));
  }
  previousStatus = payload.status || "idle";
}

function renderDebug(payload) {
  const blocks = payload.current_blocks || [];
  ids.debugReceived.textContent = payload.last_received_input || "-";
  ids.debugInput.textContent = payload.last_input || "-";
  ids.debugBlocks.textContent = JSON.stringify(blocks);
  ids.debugText.textContent = payload.current_text || "-";
  ids.debugMission.textContent = payload.mission_id || "-";
  ids.debugStatus.textContent = payload.status || "-";
  ids.debugNext.textContent = payload.expected_next_block || "-";
}

function render(payload) {
  const blocks = payload.current_blocks || [];
  ids.missionCounter.textContent = `Misión ${payload.mission_number}/${payload.total_missions}`;
  ids.skillLabel.textContent = payload.skill || "habilidad lectora";
  ids.prompt.textContent = payload.prompt || "Escanea un cubo para comenzar.";
  ids.targetText.textContent = payload.target_text || "-";
  ids.progressFill.style.width = `${payload.progress_percent || 0}%`;
  ids.feedback.textContent = payload.feedback || "";
  ids.feedback.dataset.status = payload.status || "idle";

  renderBlocks(blocks);
  renderButtons(payload.available_blocks || []);
  renderFloatingLetters(payload);
  renderScene(payload);
  renderDebug(payload);
}

async function sendNfc(value) {
  const response = await fetch(`/nfc?letra=${encodeURIComponent(value)}`);
  const payload = await response.json();
  render(payload);
}

async function loadInitialState() {
  const response = await fetch("/buffer");
  const payload = await response.json();
  render(payload);
}

function connectSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.addEventListener("open", () => setSocketStatus("Conectado"));
  socket.addEventListener("message", (event) => render(JSON.parse(event.data)));
  socket.addEventListener("close", () => {
    setSocketStatus("Reconectando");
    window.setTimeout(connectSocket, 1200);
  });
  socket.addEventListener("error", () => setSocketStatus("Revisar"));
}

loadInitialState();
connectSocket();
