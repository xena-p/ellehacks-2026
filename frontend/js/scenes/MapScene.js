class MapScene extends Phaser.Scene {
  constructor() {
    super("MapScene");
  }

  create() {
    // -----------------------------
    // REQUIRED STATE INITIALIZATION
    // -----------------------------
    this.shopOpen = false;
    this.shopUi = [];
    this.shopOverlay = null;
    this.shopPanel = null;
    this.shopTitle = null;
    this.closeShopBtn = null;
    this.closeShopBtnBottom = null;
    this.levelSprites = [];

    // Fetch player data then build the map
    this.fetchPlayerData().then(() => {
      this.buildMap();
    });
  }

  async fetchPlayerData() {
    try {
      const token = localStorage.getItem('authToken');

      if (token && token !== 'local-user-token') {
        // Fetch from backend API
        const response = await fetch('http://localhost:8000/api/player', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Player data from API:', data);

          // Update global gameData with backend values
          if (gameData.user) {
            gameData.user.level = data.level;
            gameData.user.max_hp = data.max_hp;
            gameData.user.coins = data.coins;
            gameData.user.wins = data.wins;
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch player data:', error);
    }

    // Set coins from gameData (either from API or local)
    this.coins = gameData.user ? gameData.user.coins : 50;
    this.playerLevel = gameData.user ? gameData.user.level : 1;
  }

  buildMap() {
    // -----------------------------
    // BACKGROUND
    // -----------------------------
    const bg = this.add.image(
      this.scale.width / 2,
      this.scale.height / 2,
      "map"
    );
    console.log("map texture size:", bg.width, bg.height);
    bg.setDisplaySize(this.scale.width, this.scale.height);

    // Optional HUD coins text (top-left)
    this.coinText = this.add.text(20, 20, `Coins: ${this.coins}`, {
      fontFamily: "Fredoka One",
      fontSize: "20px",
      color: "#ffffff"
    }).setDepth(100);

    // Player level display (top-left, below coins)
    this.levelText = this.add.text(20, 50, `Level: ${this.playerLevel}`, {
      fontFamily: "Fredoka One",
      fontSize: "20px",
      color: "#FFD700"
    }).setDepth(100);

    // -----------------------------
    // LEVEL + SHOP SPRITES
    // Levels unlock based on player level
    // -----------------------------
    const levels = [
      { key: "Level1Scene", spriteKey: "level1Sprite", levelRequired: 1, difficulty: "easy",   x: 770,  y: 425 },
      { key: "Level2Scene", spriteKey: "level2Sprite", levelRequired: 2, difficulty: "easy",   x: 150,  y: 270 },
      { key: "Level3Scene", spriteKey: "level3Sprite", levelRequired: 3, difficulty: "medium", x: 620,  y: 130 },
      { key: "Level4Scene", spriteKey: "level4Sprite", levelRequired: 4, difficulty: "medium", x: 1140, y: 250 },
      { key: "Level5Scene", spriteKey: "level5Sprite", levelRequired: 5, difficulty: "hard",   x: 1100, y: 550 },

      // Shop node on the map (always unlocked)
      { key: "ShopPanel", spriteKey: "shopSprite", levelRequired: 0, x: 770, y: 630 }
    ];

    // Store level sprites for later reference
    this.levelSprites = [];

    levels.forEach((level) => {
      const sprite = this.add.sprite(level.x, level.y, level.spriteKey);

      // Check if level is unlocked based on player level
      const isUnlocked = level.levelRequired <= this.playerLevel || level.spriteKey === "shopSprite";

      if (!isUnlocked) {
        sprite.setTint(0x555555);
        sprite.setAlpha(0.7);
        return;
      }

      // Store reference to interactive sprites
      this.levelSprites.push(sprite);

      sprite.setInteractive({ useHandCursor: true });

      sprite.on("pointerdown", () => {
        // If clouds are still animating, ignore clicks
        if (!this.input.enabled) return;

        // Don't allow clicking map nodes while shop modal is open
        if (this.shopOpen) return;

        if (level.spriteKey === "shopSprite") {
          this.openShopPanel();
          return;
        }

        // Start battle with appropriate difficulty
        this.scene.start("BattleScene", {
          difficulty: level.difficulty || "easy",
          area: level.key.replace("Scene", "")
        });
      });

      sprite.on("pointerover", () => sprite.setScale(1.1));
      sprite.on("pointerout", () => sprite.setScale(1));
    });

    // -----------------------------
    // CLOUD CURTAINS
    // -----------------------------
    this.playCloudCurtains();
  }

  // -----------------------------
  // SHOP PANEL (3 health options)
  // -----------------------------
  openShopPanel() {
    if (this.shopOpen) return;
    this.shopOpen = true;

    // reset tracked UI list each time shop opens
    this.shopUi = [];

    const cam = this.cameras.main;

    // IMPORTANT: shop depth must be ABOVE clouds (clouds use 9999)
    const D0 = 12000; // overlay
    const D1 = 12001; // panel
    const D2 = 12002; // headings/buttons
    const D3 = 12003; // rows/buttons

    // Dark overlay
    this.shopOverlay = this.add.graphics().setDepth(D0);
    this.shopOverlay.fillStyle(0x000000, 0.7);
    this.shopOverlay.fillRect(0, 0, cam.width, cam.height);

    // Panel position
    const panelW = 560;
    const panelH = 440;
    const panelX = cam.centerX - panelW / 2;
    const panelY = cam.centerY - panelH / 2;

    // Panel background
    this.shopPanel = this.add.graphics().setDepth(D1);
    this.shopPanel.fillStyle(0xF5E6C8, 1);
    this.shopPanel.fillRoundedRect(panelX, panelY, panelW, panelH, 16);
    this.shopPanel.lineStyle(4, 0xDCC9A3, 1);
    this.shopPanel.strokeRoundedRect(panelX, panelY, panelW, panelH, 16);

    // Title
    this.shopTitle = this.add.text(cam.centerX, panelY + 35, "Map Shop", {
      fontFamily: "Fredoka One",
      fontSize: "32px",
      color: "#3D3D3D"
    }).setOrigin(0.5).setDepth(D2);

    const subtitle = this.add.text(cam.centerX, panelY + 68, "Choose a health pack for your next battle", {
      fontFamily: "Nunito",
      fontSize: "14px",
      color: "#666666"
    }).setOrigin(0.5).setDepth(D2);

    // Close X button (top right)
    this.closeShopBtn = this.add.text(panelX + panelW - 20, panelY + 18, "X", {
      fontFamily: "Fredoka One",
      fontSize: "24px",
      color: "#666666"
    }).setOrigin(0.5).setDepth(D2).setInteractive({ useHandCursor: true });

    this.closeShopBtn.on("pointerover", () => this.closeShopBtn.setStyle({ color: "#DC143C" }));
    this.closeShopBtn.on("pointerout", () => this.closeShopBtn.setStyle({ color: "#666666" }));
    this.closeShopBtn.on("pointerdown", () => this.closeShopPanel());

    // Coin display inside panel
    const coinLabel = this.add.text(panelX + 20, panelY + 20, `Coins: ${this.coins}`, {
      fontFamily: "Fredoka One",
      fontSize: "18px",
      color: "#3D3D3D"
    }).setDepth(D2);

    // 3 options (tweak anytime)
    const packs = [
        {
            id: "small",
            label: "Small Heart",
            hp: 10,
            cost: 10,
            iconKey: "healthSmall"
        },
        {
            id: "medium",
            label: "Medium Heart",
            hp: 25,
            cost: 22,
            iconKey: "healthMedium"
        },
        {
            id: "large",
            label: "Large Heart",
            hp: 45,
            cost: 30,
            iconKey: "healthLarge"
        }
    ];

    const packStartY = panelY + 110;
    const rowH = 85;

    packs.forEach((pack, i) => {
      const y = packStartY + i * rowH;

      // Row background
      const rowBg = this.add.graphics().setDepth(D3);
      rowBg.fillStyle(0xDC143C, 0.10);
      rowBg.fillRoundedRect(panelX + 20, y, panelW - 40, 70, 12);
      rowBg.lineStyle(2, 0xDC143C, 1);
      rowBg.strokeRoundedRect(panelX + 20, y, panelW - 40, 70, 12);

      // Heart icon
      const icon = this.add.sprite(panelX + 55, y + 35, pack.iconKey)
        .setDepth(D3)
        .setScale(0.50);

      // Text
      const nameText = this.add.text(panelX + 95, y + 16, pack.label, {
        fontFamily: "Fredoka One",
        fontSize: "18px",
        color: "#3D3D3D"
      }).setDepth(D3);

      const descText = this.add.text(panelX + 95, y + 42, `+${pack.hp} health`, {
        fontFamily: "Nunito",
        fontSize: "14px",
        color: "#666666"
      }).setDepth(D3);

      // Buy button shows cost
      const buyBtn = this.add.text(panelX + panelW - 95, y + 35, `${pack.cost} coins`, {
        fontFamily: "Fredoka One",
        fontSize: "16px",
        color: "#ffffff",
        backgroundColor: "#4EC5F1",
        padding: { x: 12, y: 8 }
      }).setOrigin(0.5).setDepth(D3).setInteractive({ useHandCursor: true });

      buyBtn.on("pointerover", () => buyBtn.setStyle({ backgroundColor: "#3BA8D8" }));
      buyBtn.on("pointerout", () => buyBtn.setStyle({ backgroundColor: "#4EC5F1" }));

      buyBtn.on("pointerdown", () => {
        if (buyBtn._busy) return;
        buyBtn._busy = true;

        // Not enough coins feedback
        if (this.coins < pack.cost) {
          buyBtn.setText("NOT ENOUGH");
          buyBtn.setStyle({ backgroundColor: "#DC143C" });

          this.time.delayedCall(900, () => {
            buyBtn.setText(`${pack.cost} coins`);
            buyBtn.setStyle({ backgroundColor: "#4EC5F1" });
            buyBtn._busy = false;
          });
          return;
        }

        // Spend coins
        this.coins -= pack.cost;
        if (this.coinText) this.coinText.setText(`Coins: ${this.coins}`);
        coinLabel.setText(`Coins: ${this.coins}`);

        // Apply permanent HP upgrade to gameData
        if (gameData.user) {
          gameData.user.coins = this.coins;
          gameData.user.max_hp = (gameData.user.max_hp || 100) + pack.hp;
          console.log(`Bought ${pack.id}: +${pack.hp} HP. New max HP: ${gameData.user.max_hp}`);
        }

        // ADDED feedback then revert (repeatable)
        buyBtn.setText("ADDED");
        buyBtn.setStyle({ backgroundColor: "#2E8B57" });

        this.time.delayedCall(1200, () => {
          buyBtn.setText(`${pack.cost} coins`);
          buyBtn.setStyle({ backgroundColor: "#4EC5F1" });
          buyBtn._busy = false;
        });
      });

      // Track for cleanup
      this.shopUi.push(rowBg, icon, nameText, descText, buyBtn);
    });

    // Close button bottom
    this.closeShopBtnBottom = this.add.text(cam.centerX, panelY + panelH - 30, "CLOSE", {
      fontFamily: "Fredoka One",
      fontSize: "22px",
      color: "#ffffff",
      backgroundColor: "#666666",
      padding: { x: 30, y: 10 }
    }).setOrigin(0.5).setDepth(D2).setInteractive({ useHandCursor: true });

    this.closeShopBtnBottom.on("pointerover", () => this.closeShopBtnBottom.setStyle({ backgroundColor: "#444444" }));
    this.closeShopBtnBottom.on("pointerout", () => this.closeShopBtnBottom.setStyle({ backgroundColor: "#666666" }));
    this.closeShopBtnBottom.on("pointerdown", () => this.closeShopPanel());

    // Track top-level UI for cleanup too
    this.shopUi.push(subtitle, coinLabel, this.shopTitle, this.closeShopBtn, this.closeShopBtnBottom);

    // ESC closes shop
    this.input.keyboard.once("keydown-ESC", () => {
      if (this.shopOpen) this.closeShopPanel();
    });
  }

  closeShopPanel() {
    if (!this.shopOpen) return;
    this.shopOpen = false;

    // Destroy overlay and panel
    if (this.shopOverlay) {
      this.shopOverlay.destroy();
      this.shopOverlay = null;
    }
    if (this.shopPanel) {
      this.shopPanel.destroy();
      this.shopPanel = null;
    }

    // Destroy everything tracked in shopUi
    if (this.shopUi && this.shopUi.length) {
      this.shopUi.forEach(obj => {
        if (obj && obj.destroy) {
          obj.destroy();
        }
      });
      this.shopUi = [];
    }

    this.shopTitle = null;
    this.closeShopBtn = null;
    this.closeShopBtnBottom = null;

    // Re-enable level sprite interactivity (safety measure)
    if (this.levelSprites && this.levelSprites.length) {
      this.levelSprites.forEach(sprite => {
        if (sprite && sprite.setInteractive) {
          sprite.setInteractive({ useHandCursor: true });
        }
      });
    }
  }

  // -----------------------------
  // CLOUD CURTAINS
  // -----------------------------
  playCloudCurtains() {
    this.input.enabled = false;

    const leftStartX = 7;
    const leftStartY = 0;

    const rightStartX = 1473;
    const rightStartY = 0;

    const left = this.add.image(leftStartX, leftStartY, "cloud1Sprite")
      .setOrigin(0, 0)
      .setDepth(9999);

    const right = this.add.image(rightStartX, rightStartY, "cloud2Sprite")
      .setOrigin(1, 0)
      .setDepth(9999);

    const leftEndX = leftStartX - 900;
    const rightEndX = rightStartX + 900;

    this.tweens.add({
      targets: left,
      x: leftEndX,
      duration: 1900,
      ease: "Cubic.easeInOut"
    });

    this.tweens.add({
      targets: right,
      x: rightEndX,
      duration: 1900,
      ease: "Cubic.easeInOut",
      onComplete: () => {
        this.tweens.add({
          targets: [left, right],
          alpha: 0,
          duration: 10,
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