class MapScene extends Phaser.Scene {
  constructor() {
    super("MapScene");
  }

  create() {
    const bg = this.add.image(
      this.scale.width / 2,
      this.scale.height / 2,
      "map"
    );
    console.log("map texture size:", bg.width, bg.height);
    bg.setDisplaySize(this.scale.width, this.scale.height);
 
 
    //creates level sprites
    const levels = [
    { key: "Level1Scene", spriteKey: "level1Sprite", unlocked: true, x: 770, y: 425},
    { key: "Level2Scene", spriteKey: "level2Sprite", unlocked: false, x: 150, y: 270 },
    { key: "Level3Scene", spriteKey: "level3Sprite", unlocked: false, x: 620, y: 130 },
    { key: "Level4Scene", spriteKey: "level4Sprite", unlocked: false, x: 1140, y: 250 },
    { key: "Level5Scene", spriteKey: "level5Sprite", unlocked: false, x: 1100, y: 550 },

     { key: "shopScene", spriteKey: "shopSprite", unlocked: true, x: 770, y: 630 }
  ];

  levels.forEach((level) => {
    const sprite = this.add.sprite(level.x, level.y, level.spriteKey);

    if (!level.unlocked) {
      sprite.setTint(0x555555);
      sprite.setAlpha(0.7);
      sprite.disableInteractive();
      return;
    } 
    
    sprite.setInteractive({ useHandCursor: true });
    sprite.on("pointerdown", () => {
        if (level.spriteKey === "level1Sprite"){
            this.scene.start("BattleScene");
        } else{
            console.log("This level isn't implemented yet.");
        }
    });
      sprite.on("pointerover", () => sprite.setScale(1.1));
      sprite.on("pointerout", () => sprite.setScale(1));
    
  });

  //Play cloud curtain animation
    this.playCloudCurtains();
  }
    playCloudCurtains() {
  this.input.enabled = false;

  // ✅ YOU decide these start positions
  const leftStartX = 7;
  const leftStartY = 0;

  const rightStartX = 1473; // you can change this
  const rightStartY = 0;

  const left = this.add.image(leftStartX, leftStartY, "cloud1Sprite")
    .setOrigin(0, 0)
    .setDepth(9999);

  const right = this.add.image(rightStartX, rightStartY, "cloud2Sprite")
    .setOrigin(1, 0)
    .setDepth(9999);

  // ✅ YOU decide how far they move
  const leftEndX = leftStartX - 900;   // change this
  const rightEndX = rightStartX + 900; // change this

  this.tweens.add({
    targets: left,
    x: leftEndX,
    duration: 2500,
    ease: "Cubic.easeInOut"
  });

  this.tweens.add({
    targets: right,
    x: rightEndX,
    duration: 2500,
    ease: "Cubic.easeInOut",
    onComplete: () => {
      this.tweens.add({
        targets: [left, right],
        alpha: 0,
        duration: 2000,
        onComplete: () => {
          left.destroy();
          right.destroy();
          this.input.enabled = true;
        }
      });
    }
  });
}
}