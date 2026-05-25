# Official Game Frontend Architecture

This directory is the only official Phaser architecture for the React demo.

Runtime flow:

```txt
src/main.tsx
  -> App
  -> MissionView
  -> PhaserStage
  -> game/phaser/bootstrap/createStorybookGame
  -> game/phaser/scenes/StorybookScene
```

Directory roles:

- `phaser/bootstrap/`: creates and configures the single Phaser.Game instance.
- `phaser/scenes/`: active Phaser scenes mounted from React.
- `phaser/systems/`, `phaser/entities/`, `phaser/fx/`: reserved for future Phaser-only modules.
- `bridge/`: event bridge between React state and Phaser scenes.
- `data/`: frontend game data and asset manifests.
- `state/`: local software-only demo state used when FastAPI is unavailable.

React owns application state, controls, navigation, shop, village UI, and debug
panels. Phaser renders the playable scene and reacts to state pushed through the
bridge. Do not instantiate Phaser outside `PhaserStage`.
