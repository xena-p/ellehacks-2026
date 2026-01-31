import Phaser from "phaser";

export default class MainMenuScene extends Phaser.Scene {
  constructor() {
    super("MainMenuScene");
  }

  create() {
    // Add a title in the middle of the screen
    this.add
      .text(this.cameras.main.centerX, 150, "My Game", {
        fontSize: "48px",
        color: "#ffffff",
      })
      .setOrigin(0.5);

    // Start button
    const startButton = this.add
      .text(this.cameras.main.centerX, 300, "Start", {
        fontSize: "32px",
        color: "#00ff00",
      })
      .setOrigin(0.5)
      .setInteractive({ useHandCursor: true });

    // When clicked, start the GameScene
    startButton.on("pointerdown", () => {
      this.scene.start("GameScene");
    });
}
}

    // Opt
