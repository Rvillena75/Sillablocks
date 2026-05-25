# Deprecated Phaser Scene Stack

This folder preserves the older standalone Phaser scene stack:

- `createLegacyGame.ts`
- `scenes/BootScene.ts`
- `scenes/MissionScene.ts`
- `scenes/RewardScene.ts`
- `scenes/VillageScene.ts`
- `scenes/DebugOverlay.ts`
- `ui/`

These files are not part of the official demo flow. They are kept only as
reference while the React-mounted Storybook scene becomes the maintained path.

Do not wire new work through this folder. The official flow starts in
`components/PhaserStage.tsx` and creates `game/phaser/scenes/StorybookScene`.
