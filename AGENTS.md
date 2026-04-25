# Repository Guidelines for SilaBlocks

## 1. Project Overview

SilaBlocks is a physical-digital educational game designed to support early literacy practice for children.

The system combines:

- Physical cubes with NFC tags.
- A phone that reads the NFC tags.
- WiFi communication from the phone to a local PC server.
- A PC screen that displays the game.
- A future game layer where children build letters, syllables and words through physical interaction.

The current repository combines product/design documentation with a small Python/FastAPI server for NFC input handling and screen display.

The current technical prototype already supports:

- Reading NFC cubes with a phone.
- Sending HTTP requests over WiFi to the PC.
- Receiving NFC input in a local FastAPI server.
- Maintaining a word/input buffer.
- Showing the buffer on a display page.
- Broadcasting updates through WebSockets.
- Handling special commands such as delete/backspace.

The next objective is to evolve this prototype into a first playable MVP.

---

## 2. Main Objective for Codex

Act as a senior software engineer and technical architect for this project.

Your main task is to help transform the current NFC/WiFi demo into a playable educational game prototype.

Prioritize:

1. Preserving the current working NFC flow.
2. Making the system stable for live demos.
3. Creating a first game loop.
4. Keeping the code simple and modular.
5. Making future iteration easy.

Do not treat this as a generic web app. This is a hybrid physical-digital EdTech prototype.

---

## 3. Current Repository Structure

The repository currently contains product/design documentation and an Arduino/NFC integration server.

Expected structure:

```txt
.
├── AGENTS.md
├── *.md
├── arduino/
│   ├── sila_server.py
│   ├── requirements.txt
│   └── sila_server.log
└── ...
````

### Root markdown files

Root `*.md` files contain product, theme, engagement, game design, narrative, reward-economy and project planning notes.

Do not rewrite these documents while changing server behavior unless the user explicitly asks for documentation updates.

### `arduino/sila_server.py`

This is the current FastAPI application.

It is responsible for:

- Receiving NFC events.
    
- Maintaining the current word/input buffer.
    
- Serving the display page.
    
- Exposing WebSocket updates.
    
- Supporting manual/debug interaction.
    

Do not break this file without a clear reason.

### `arduino/requirements.txt`

Lists Python runtime dependencies.

### `arduino/sila_server.log`

Generated runtime output.

Do not treat this file as source code. Do not commit or depend on it.

---

## 4. Development Commands

Run commands from the repository root unless noted.

### Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r arduino\requirements.txt
```

### Run the current server

```powershell
python arduino\sila_server.py
```

The local SilaBlocks NFC server should start on:

```txt
http://0.0.0.0:5000
```

### Run with Uvicorn reload for development

```powershell
uvicorn arduino.sila_server:app --host 0.0.0.0 --port 5000 --reload
```

### Basic manual checks

```powershell
Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod "http://localhost:5000/nfc?letra=A"
Invoke-RestMethod http://localhost:5000/buffer
```

The phone should call the PC using the local network IP, for example:

```txt
http://192.168.x.x:5000/nfc?letra=A
```

---

## 5. Existing NFC API Contract

Maintain compatibility with the current NFC route:

```txt
GET /nfc?letra=<valor>
```

Examples:

```txt
/nfc?letra=A
/nfc?letra=MA
/nfc?letra=CASA
/nfc?letra=BORRAR
/nfc?letra=DELETE
/nfc?letra=BACKSPACE
/nfc?letra=RESET
/nfc?letra=ENTER
```

The system should accept both letters and syllables.

Special commands:

- `BORRAR`
    
- `DELETE`
    
- `BACKSPACE`
    
- `RESET`
    
- `ENTER`
    

Expected behavior:

- A normal NFC value appends to the current buffer.
    
- `BORRAR`, `DELETE` or `BACKSPACE` remove the last input block.
    
- `RESET` clears the buffer.
    
- `ENTER` validates the current answer or triggers the current game action.
    

Do not remove or rename existing routes unless explicitly requested.

---

## 6. Buffer Rules

The buffer represents what the child has built using physical cubes.

Important rule:

The buffer should conceptually preserve blocks, not only raw text.

For example, if the child scans:

```txt
MA
PA
```

The conceptual buffer should be:

```json
["MA", "PA"]
```

not only:

```txt
MAPA
```

This matters because deleting should remove the last scanned cube/block, not just the last character.

When displaying the answer, the system may join the blocks visually as:

```txt
MAPA
```

but internally it should preserve block-level structure when possible.

---

## 7. MVP Goal

The first playable MVP should allow a child to:

1. Start a simple mission.
    
2. Scan physical NFC cubes.
    
3. See the scanned blocks appear on screen.
    
4. Build a target word.
    
5. Receive immediate visual feedback.
    
6. Use delete/reset commands.
    
7. Complete the mission when the word is correct.
    

The MVP should be demo-ready, not production-ready.

Prioritize a stable, understandable live demo over complex features.

---

## 8. Recommended First Game Loop

The first mission should be simple:

```txt
Mission: Build the word MAMÁ
Available blocks: MA, MÁ, PA, SA
Correct answer: MAMÁ
```

Flow:

1. The screen shows a prompt.
    
2. The child scans a cube.
    
3. The block appears on the screen.
    
4. The child scans another cube.
    
5. The system compares the current buffer with the target.
    
6. If correct, the game shows success feedback.
    
7. If incomplete, the game encourages continuation.
    
8. If incorrect after validation, the game gives a soft hint.
    
9. The child can delete or reset without punishment.
    

---

## 9. Game Concept Direction

Use this as the default narrative direction:

```txt
El Mundo de las Palabras Perdidas
```

Premise:

The world has lost its words. Letters and syllables are scattered in physical cubes. The child helps restore the world by rebuilding words.

Each completed word can restore something visible:

- A house.
    
- A tree.
    
- A bridge.
    
- A character.
    
- A path.
    
- A light.
    
- A map fragment.
    

The narrative should support the learning goal. Do not overcomplicate the story before the core game loop works.

---

## 10. Educational Design Principles

This project is for children learning to read.

Follow these principles:

- Use positive reinforcement.
    
- Avoid punishment-heavy mechanics.
    
- Avoid shame, failure language or aggressive correction.
    
- Use simple instructions.
    
- Use large, readable text.
    
- Use clear contrast.
    
- Give immediate feedback.
    
- Allow retries.
    
- Avoid pressure timers in the MVP.
    
- Make the physical action meaningful.
    
- Make progress visible.
    

Preferred feedback:

```txt
Muy bien.
Casi.
Falta una parte.
Probemos otra vez.
Mira la primera sílaba.
Encontraste la palabra.
```

Avoid:

```txt
Fallaste.
Incorrecto otra vez.
Mal.
Te equivocaste.
Perdiste.
```

---

## 11. Ethical Engagement Rules

The game should motivate children without using manipulative engagement patterns.

Allowed:

- Progress maps.
    
- Visual restoration.
    
- Collectible badges.
    
- Gentle missions.
    
- Character encouragement.
    
- Optional replay.
    
- Clear goals.
    
- Short sessions.
    
- Parent/teacher-visible progress.
    

Avoid:

- Loot boxes.
    
- Gambling-like randomness.
    
- Streaks that punish absence.
    
- Infinite engagement loops.
    
- Competitive rankings between children.
    
- Scarcity pressure.
    
- “Come back or lose progress” mechanics.
    
- Dark patterns.
    

The goal is sustained educational motivation, not addiction.

---

## 12. Recommended Software Architecture

Preserve the current FastAPI server but gradually separate responsibilities.

Target architecture:

```txt
NFC cubes
   ↓
Phone NFC reader
   ↓ HTTP over WiFi
FastAPI server
   ↓
NFC input adapter
   ↓
Game engine
   ↓
Frontend/display page
   ↓
Feedback + progress log
```

Suggested modules over time:

```txt
arduino/
├── sila_server.py
├── game/
│   ├── engine.py
│   ├── missions.py
│   ├── buffer.py
│   └── models.py
├── static/
│   ├── styles.css
│   └── app.js
├── templates/
│   └── index.html
└── requirements.txt
```

Do not force this structure immediately if it causes unnecessary risk. Migrate incrementally.

---

## 13. Suggested Modules

### NFC Input Adapter

Responsibility:

- Receive `/nfc?letra=...`.
    
- Normalize input.
    
- Detect commands.
    
- Convert raw NFC input into internal game events.
    
- Forward clean events to the game engine.
    

It should not contain mission logic.

### Buffer Manager

Responsibility:

- Maintain block-level buffer.
    
- Append blocks.
    
- Delete last block.
    
- Reset buffer.
    
- Return both block list and joined text.
    

### Game Engine

Responsibility:

- Maintain current mission state.
    
- Process game events.
    
- Validate answers.
    
- Generate feedback.
    
- Move between mission states.
    
- Provide state to the frontend.
    

### Mission System

Responsibility:

- Store mission definitions.
    
- Support mission types.
    
- Allow easy addition of new missions.
    

Mission types for future use:

- Recognize a letter.
    
- Build a syllable.
    
- Build a word.
    
- Complete a missing syllable.
    
- Separate a word into syllables.
    
- Match initial sound.
    
- Form the heard word.
    

### Frontend Display

Responsibility:

- Show current mission.
    
- Show scanned blocks.
    
- Show feedback.
    
- Show progress.
    
- Show debug panel for development.
    
- Update in real time through WebSocket or polling.
    

### Progress Logger

Responsibility:

- Log session events locally.
    
- Track scanned inputs.
    
- Track correct/incorrect attempts.
    
- Track mission completion.
    
- Avoid storing real personal data from children.
    

For now, JSON or JSONL is enough.

---

## 14. Frontend Requirements for MVP

The display page should include:

1. Mission prompt.
    
2. Target word or visual clue.
    
3. Current scanned blocks.
    
4. Feedback message.
    
5. Progress indicator.
    
6. Debug panel.
    
7. Reset button.
    
8. Optional manual input buttons for testing.
    

The interface should be suitable for a live university demo.

Keep the UI simple, clean and readable.

---

## 15. Developer/Debug Mode

Include or preserve a visible developer/debug section.

It should show:

- Last NFC input received.
    
- Current buffer as blocks.
    
- Current joined buffer.
    
- Current mission ID.
    
- Current mission target.
    
- Current validation status.
    
- WebSocket connection status if applicable.
    
- Buttons to simulate inputs manually.
    
- Reset mission/session button.
    

This is important for debugging during live demos.

---

## 16. Coding Style

Use Python 3.11+ style.

Guidelines:

- Use type hints where practical.
    
- Use 4-space indentation.
    
- Use descriptive `snake_case` names for variables and functions.
    
- Use `PascalCase` for Pydantic models/classes.
    
- Use `UPPER_SNAKE_CASE` for module-level constants.
    
- Keep Spanish user-facing messages consistent with the current app.
    
- Keep internal code names in English or Spanish consistently; avoid random mixing.
    
- Prefer small functions.
    
- Avoid large rewrites.
    
- Avoid hidden global state when possible.
    
- Use explicit error handling.
    

No formatter or linter config is currently committed.

If adding one, prefer `pyproject.toml` and document the command here.

---

## 17. Testing Guidelines

No automated test suite is currently present.

When adding tests:

- Place them under `tests/`.
    
- Name files `test_*.py`.
    
- Use `pytest`.
    
- Use FastAPI `TestClient` for API tests.
    

Minimum future coverage:

- `/health`
    
- `/nfc`
    
- `/buffer`
    
- delete commands
    
- reset command
    
- validation failures
    
- buffer behavior
    
- game engine answer validation
    
- WebSocket broadcast behavior where feasible
    

Recommended future command:

```powershell
pytest
```

Manual testing is acceptable for the current MVP stage, but every major change should include clear manual test steps.

---

## 18. Manual Testing Checklist

After changing NFC, buffer or game behavior, test:

```powershell
Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod "http://localhost:5000/nfc?letra=MA"
Invoke-RestMethod "http://localhost:5000/nfc?letra=MA"
Invoke-RestMethod "http://localhost:5000/nfc?letra=BORRAR"
Invoke-RestMethod "http://localhost:5000/nfc?letra=RESET"
Invoke-RestMethod http://localhost:5000/buffer
```

Also test in browser:

```txt
http://localhost:5000
```

Then test from the phone using the PC local IP:

```txt
http://<PC_LOCAL_IP>:5000/nfc?letra=MA
```

---

## 19. Commit and Pull Request Guidelines

This checkout may not include Git history, so no repository-specific commit convention can be inferred.

Use short, imperative commit subjects:

```txt
Add game engine
Add NFC buffer tests
Update display page
Add first word mission
Improve delete command handling
```

Pull requests should include:

- Concise summary.
    
- Files or areas changed.
    
- Manual test results.
    
- Screenshots when the display UI changes.
    
- Related planning notes if relevant.
    

Avoid committing:

- Generated logs.
    
- Virtual environments.
    
- Cache folders.
    
- Local machine artifacts.
    
- Temporary debug files.
    

---

## 20. Agent-Specific Instructions

When working in this repository:

1. Keep edits scoped.
    
2. Do not rewrite planning documents unless asked.
    
3. Do not break the current NFC flow.
    
4. Preserve `/nfc?letra=...`.
    
5. Prefer incremental refactors.
    
6. Explain architectural changes before making large rewrites.
    
7. Add useful logs for debugging.
    
8. Keep the project easy to run on Windows.
    
9. Maintain compatibility with phone-to-PC local network testing.
    
10. Prioritize a working demo over a perfect architecture.
    

Before modifying code, inspect:

- Repository tree.
    
- `arduino/sila_server.py`
    
- `arduino/requirements.txt`
    
- Existing routes.
    
- Existing WebSocket logic.
    
- Existing HTML/display behavior.
    
- Existing buffer logic.
    

---

## 21. Response Format for Codex

When responding to development tasks, use this structure:

1. What I understood.
    
2. Current architecture found.
    
3. Implementation plan.
    
4. Files to change.
    
5. Changes made.
    
6. How to test.
    
7. Risks or pending items.
    
8. Recommended next step.
    

For very small changes, a shorter response is acceptable.

---

## 22. First Recommended Task

The first implementation task should be:

```txt
Inspect the repository and convert the current NFC/WiFi prototype into a first playable MVP. Preserve the existing /nfc?letra=... route. Add or refactor only what is necessary to support a simple game mission where the child builds the word MAMÁ using NFC blocks. Show the current blocks on screen, validate the answer, support BORRAR and RESET, provide positive feedback, and include a debug panel showing the current game state.
```

Do not start by building a full platform.

Do not add user accounts.

Do not add cloud infrastructure.

Do not add a database unless strictly needed.

---

## 23. Roadmap

### Stage 1: Stabilize NFC input

- Preserve current server behavior.
    
- Normalize NFC input.
    
- Improve command handling.
    
- Preserve block-level buffer.
    
- Improve logs.
    

### Stage 2: Add game state

- Add current mission.
    
- Add target answer.
    
- Add validation.
    
- Add feedback states.
    
- Add reset and next mission behavior.
    

### Stage 3: Improve display page

- Show mission prompt.
    
- Show scanned blocks.
    
- Show feedback.
    
- Add visual progress.
    
- Add debug panel.
    
- Make it presentable.
    

### Stage 4: Add narrative layer

- Introduce “El Mundo de las Palabras Perdidas”.
    
- Restore visual objects after correct words.
    
- Add simple character guide.
    
- Add mission progression.
    

### Stage 5: Add progress tracking

- Log attempts.
    
- Log completed missions.
    
- Log errors.
    
- Summarize session progress.
    
- Keep all data local and non-sensitive.
    

### Stage 6: Prepare demo mode

- Add predefined missions.
    
- Add reset-all command.
    
- Add manual simulation buttons.
    
- Add clear setup instructions.
    
- Make the prototype robust for presentation.
    

---

## 24. Highest Priority

The highest priority is a stable, playable, demonstrable MVP.

The child should be able to:

1. Scan a cube.
    
2. See it appear.
    
3. Build a word.
    
4. Receive feedback.
    
5. Complete a mission.
    

Everything else is secondary.
