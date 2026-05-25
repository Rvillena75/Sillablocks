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
  missionRestoration: document.getElementById("missionRestoration"),
  restorationName: document.getElementById("restorationName"),
  restorationMeter: document.getElementById("restorationMeter"),
  lumoLine: document.getElementById("lumoLine"),
  speakBtn: document.getElementById("speakBtn"),
  arcadeBtn: document.getElementById("arcadeBtn"),
  debugReceived: document.getElementById("debugReceived"),
  debugInput: document.getElementById("debugInput"),
  debugSlots: document.getElementById("debugSlots"),
  debugBlocks: document.getElementById("debugBlocks"),
  debugText: document.getElementById("debugText"),
  debugMission: document.getElementById("debugMission"),
  debugStatus: document.getElementById("debugStatus"),
  debugNext: document.getElementById("debugNext"),
  debugSocket: document.getElementById("debugSocket")
};

let previousStatus = "idle";
let previousRepairLevel = 0;
let lastSpokenMissionId = "";
const restorationByMission = {
  m001: {
    artifact: "lantern",
    name: "Farol perdido",
    idleLine: "Ese farol está apagado... vamos a devolverle su palabra.",
    progressLine: "Muy bien, ya vuelve un poco de luz.",
    successLine: "Buen trabajo. Mira cómo volvió la luz."
  },
  m002: {
    artifact: "path",
    name: "Camino dormido",
    idleLine: "El camino necesita recordar sus pasos.",
    progressLine: "El camino se está despejando.",
    successLine: "El camino volvió a abrirse."
  },
  m003: {
    artifact: "sign",
    name: "Señal sin voz",
    idleLine: "Esta señal perdió lo que quería decir.",
    progressLine: "La señal empieza a entenderse.",
    successLine: "La señal ya muestra el camino."
  },
  m004: {
    artifact: "house",
    name: "Casa de la plaza",
    idleLine: "Esta casa necesita una palabra para abrirse.",
    progressLine: "La casa se está arreglando.",
    successLine: "La plaza ya tiene su casa encendida."
  },
  m005: {
    artifact: "bridge",
    name: "Puente de la ruta",
    idleLine: "El puente está incompleto. Reparemos la ruta.",
    progressLine: "El puente gana nuevas tablas.",
    successLine: "La ruta quedó lista para explorar."
  }
};
const speechSupported =
  "speechSynthesis" in window &&
  "SpeechSynthesisUtterance" in window;

function setSpeechButtonState(state) {
  ids.speakBtn.classList.toggle("speaking", state === "speaking");
  ids.speakBtn.classList.toggle("speech-error", state === "error");
  ids.speakBtn.disabled = state === "unsupported";

  if (state === "unsupported") {
    ids.speakBtn.title = "Este navegador no tiene voz disponible";
    ids.speakBtn.setAttribute("aria-label", "Voz no disponible");
    return;
  }

  ids.speakBtn.title = "Escuchar instrucción";
  ids.speakBtn.setAttribute("aria-label", "Escuchar instrucción");
}

function getSpanishVoice() {
  if (!speechSupported) return null;
  const voices = window.speechSynthesis.getVoices();
  const es = voices.filter((v) => v.lang.toLowerCase().startsWith("es"));

  // Prioridad: voces online (Google/Microsoft Natural) > voces locales
  return (
    es.find((v) => /natural/i.test(v.name)) ||          // Edge Natural
    es.find((v) => /google/i.test(v.name)) ||            // Chrome Google
    es.find((v) => /online/i.test(v.name)) ||            // cualquier online
    es.find((v) => !v.localService) ||                   // no-local = online
    es.find((v) => v.lang.toLowerCase().startsWith("es-cl")) ||
    es.find((v) => v.lang.toLowerCase().startsWith("es-")) ||
    voices[0] ||
    null
  );
}

function speak(text) {
  const message = text.trim();
  if (!message || !speechSupported) {
    setSpeechButtonState("unsupported");
    return;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  const voice = getSpanishVoice();
  if (voice) {
    utterance.voice = voice;
    utterance.lang = voice.lang;
  } else {
    utterance.lang = "es-CL";
  }
  utterance.rate = 0.85;
  utterance.pitch = 1.1;
  utterance.onstart = () => setSpeechButtonState("speaking");
  utterance.onend = () => setSpeechButtonState("ready");
  utterance.onerror = () => setSpeechButtonState("error");

  window.speechSynthesis.cancel();
  window.speechSynthesis.resume();
  window.setTimeout(() => window.speechSynthesis.speak(utterance), 40);
}

if (new URLSearchParams(window.location.search).has("debug")) {
  document.body.classList.add("debug-visible");
}

const requestedMissionId = new URLSearchParams(window.location.search).get("mission");

ids.speakBtn.addEventListener("click", () => {
  const prompt = ids.prompt.textContent;
  const target = ids.targetText.textContent;
  speak(target ? `${prompt} La palabra es ${target}` : prompt);
});

ids.arcadeBtn.addEventListener("click", async () => {
  ids.arcadeBtn.classList.add("pressed");
  window.setTimeout(() => ids.arcadeBtn.classList.remove("pressed"), 180);
  const response = await fetch("/arcade");
  const payload = await response.json();
  render(payload);
});

// Spacebar also triggers the arcade button (testing / accessibility)
document.addEventListener("keydown", (e) => {
  if (e.code === "Space" && e.target === document.body) {
    e.preventDefault();
    ids.arcadeBtn.click();
  }
});

if (!speechSupported) {
  setSpeechButtonState("unsupported");
} else if (window.speechSynthesis.onvoiceschanged !== undefined) {
  window.speechSynthesis.onvoiceschanged = () => setSpeechButtonState("ready");
}

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

function renderSlots(payload) {
  const slots = payload.slots || ["", "", "", ""];
  const slotTargets = payload.slot_targets || ["", "", "", ""];
  ids.blockTray.replaceChildren();

  slots.forEach((letter, index) => {
    const slot = document.createElement("div");
    const filled = letter.trim() !== "";
    const target = slotTargets[index] || "";
    slot.className = `letter-slot ${filled ? "filled" : "empty"}`;
    slot.dataset.target = target;
    slot.style.setProperty("--slot-index", index);

    const num = document.createElement("span");
    num.className = "slot-number";
    num.textContent = index + 1;

    const letterEl = document.createElement("span");
    letterEl.className = "slot-letter";
    letterEl.textContent = filled ? letter : target;

    slot.appendChild(num);
    slot.appendChild(letterEl);
    ids.blockTray.appendChild(slot);
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
  ids.zoneLabel.textContent = payload.zone || "Bosque de las Sílabas";
  ids.body.dataset.status = payload.status || "idle";
  ids.missionScene.dataset.status = payload.status || "idle";
  ids.missionScene.classList.toggle("has-blocks", (payload.current_blocks || []).length > 0);

  if ((payload.status === "success" || payload.status === "demo_complete") && previousStatus !== payload.status) {
    ids.missionScene.classList.remove("celebrate");
    window.requestAnimationFrame(() => ids.missionScene.classList.add("celebrate"));
  }
  previousStatus = payload.status || "idle";
}

function repairLevel(payload) {
  if (payload.status === "success" || payload.status === "demo_complete") {
    return 3;
  }

  const total = Math.max(payload.target_block_count || 1, 1);
  const correct = payload.correct_prefix_count || 0;
  if (correct <= 0) {
    return 0;
  }
  return Math.min(2, Math.ceil((correct / total) * 2));
}

function renderRestorationTarget(payload) {
  const restoration = restorationByMission[payload.mission_id] || restorationByMission.m001;
  const level = repairLevel(payload);

  ids.missionRestoration.dataset.artifact = restoration.artifact;
  ids.missionRestoration.dataset.repairLevel = String(level);
  ids.restorationName.textContent = restoration.name;
  ids.restorationMeter.style.width = `${Math.round((level / 3) * 100)}%`;

  if (level > previousRepairLevel) {
    ids.missionRestoration.classList.remove("repair-pulse");
    void ids.missionRestoration.offsetWidth;
    ids.missionRestoration.classList.add("repair-pulse");
  }
  previousRepairLevel = level;

  if (payload.status === "success" || payload.status === "demo_complete") {
    ids.lumoLine.textContent = restoration.successLine;
  } else if (level > 0) {
    ids.lumoLine.textContent = restoration.progressLine;
  } else {
    ids.lumoLine.textContent = restoration.idleLine;
  }
}

function renderDebug(payload) {
  const blocks = payload.current_blocks || [];
  ids.debugReceived.textContent = payload.last_received_input || "-";
  ids.debugInput.textContent = payload.last_input || "-";
  ids.debugSlots.textContent = JSON.stringify(payload.slots || []);
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

  const missionId = payload.mission_id || "";
  if (missionId && missionId !== lastSpokenMissionId) {
    lastSpokenMissionId = missionId;
    const prompt = payload.prompt || "";
    const target = payload.target_text || "";
    const fullText = target ? `${prompt} La palabra es ${target}` : prompt;
    window.setTimeout(() => speak(fullText), 600);
  }

  renderSlots(payload);
  renderButtons(payload.available_blocks || []);
  renderFloatingLetters(payload);
  renderScene(payload);
  renderRestorationTarget(payload);
  renderDebug(payload);
}

async function sendNfc(value) {
  const response = await fetch(`/nfc?letra=${encodeURIComponent(value)}`);
  const payload = await response.json();
  render(payload);
}

async function loadInitialState() {
  if (requestedMissionId) {
    await fetch("/mission/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mission_id: requestedMissionId })
    });
  }

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
