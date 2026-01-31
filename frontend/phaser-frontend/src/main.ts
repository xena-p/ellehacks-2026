import Phaser from "phaser";
import BootScene from "./scenes/BootScene.ts";
import MainMenuScene from "./scenes/MainMenuScene.ts";
import GameScene from "./scenes/GameScene.ts";

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: "game",
  backgroundColor: "#1e1e1e",
  scene: [BootScene, MainMenuScene, GameScene],
};

new Phaser.Game(config);
