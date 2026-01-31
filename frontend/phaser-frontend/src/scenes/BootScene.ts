import Phaser from "phaser";

export default class BootScene extends Phaser.Scene {
  constructor() {
    super("BootScene");
  }

  preload() {
    // load assets
  }

  create() {
    this.scene.start("MainMenuScene");
  }
}
