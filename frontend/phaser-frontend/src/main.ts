import Phaser from "phaser";
import BootScene from "./scenes/BootScene.ts";
import MainMenuScene from "./scenes/MainMenuScene.ts";
import GameScene from "./scenes/GameScene.ts";
import BattleScene from "./scenes/BattleScene.ts";

const speedDown = 300
const speedUp = 0

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 1480,
  height: 730,
  scale: {
  mode: Phaser.Scale.FIT,
  autoCenter: Phaser.Scale.CENTER_BOTH
},
  // scene: [BootScene, MainMenuScene, GameScene, BattleScene],
  scene: [BattleScene],
  parent: "game",
  backgroundColor: "#1e1e1e",
  physics: {
    default: "arcade",
    arcade:{
      gravity: {x: speedUp, y:speedDown},
      debug: true
    }
  },
};

const game = new Phaser.Game(config);
