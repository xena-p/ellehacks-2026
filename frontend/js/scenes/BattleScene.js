class BattleScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BattleScene' });

        // Battle configuration
        this.PLAYER_DAMAGE = 25;
        this.ENEMIES = {
            easy: [
                { name: 'Penny Pincher', hp: 50, attack: 10, coins: 10, color: 0x8B4513 },
                { name: 'Piggy Bank Bandit', hp: 50, attack: 10, coins: 10, color: 0xFFB6C1 },
                { name: 'Coin Gremlin', hp: 50, attack: 10, coins: 10, color: 0x228B22 }
            ],
            medium: [
                { name: 'Debt Monster', hp: 80, attack: 15, coins: 20, color: 0x800080 },
                { name: 'Budget Breaker', hp: 80, attack: 15, coins: 20, color: 0xFF4500 },
                { name: 'Impulse Imp', hp: 80, attack: 15, coins: 20, color: 0xDC143C }
            ],
            hard: [
                { name: 'Credit Card Crook', hp: 120, attack: 20, coins: 35, color: 0x2F4F4F },
                { name: 'Scam Sorcerer', hp: 120, attack: 20, coins: 35, color: 0x4B0082 },
                { name: 'Interest Ogre', hp: 120, attack: 20, coins: 35, color: 0x8B0000 }
            ]
        };

        this.SPELLS = {
            heal: { name: 'Healing Potion', cost: 5, effect: 'heal', value: 25, color: 0xFF69B4 },
            power: { name: 'Power Strike', cost: 8, effect: 'doubleDamage', color: 0xFF6600 },
            shield: { name: 'Magic Shield', cost: 10, effect: 'blockAttack', color: 0x4169E1 }
        };
    }

    init(data) {
        // Receive data from MapScene
        this.difficulty = data.difficulty || 'easy';
        this.areaName = data.area || "King's Court";

        // Reset battle state
        this.battleState = 'shop'; // shop, battle, ended
        this.playerHP = 0;
        this.playerMaxHP = 0;
        this.enemyHP = 0;
        this.enemyMaxHP = 0;
        this.currentEnemy = null;
        this.purchasedSpells = [];
        this.usedSpells = [];
        this.hasShield = false;
        this.hasPowerStrike = false;
        this.currentQuestion = null;
        this.playerCoins = 0;
        this.questionVisible = false;
    }

    preload() {
        // For now, we'll use Phaser graphics for placeholders
        // Later, load actual sprites here:
        // this.load.spritesheet('player', 'frontend/assets/images/player/player.png', { frameWidth: 64, frameHeight: 64 });
        // this.load.spritesheet('enemy', 'frontend/assets/images/enemies/enemy.png', { frameWidth: 64, frameHeight: 64 });
        // this.load.image('battle-bg', 'frontend/assets/images/backgrounds/battle-bg.png');
    }

    create() {
        // Get player data from global gameData
        this.playerMaxHP = gameData.user ? (100 + (gameData.user.level - 1) * 20) : 100;
        this.playerHP = this.playerMaxHP;
        this.playerCoins = gameData.user ? (gameData.user.coins || 50) : 50; // Default 50 coins for testing

        // Select random enemy based on difficulty
        const enemyList = this.ENEMIES[this.difficulty];
        this.currentEnemy = enemyList[Math.floor(Math.random() * enemyList.length)];
        this.enemyMaxHP = this.currentEnemy.hp;
        this.enemyHP = this.enemyMaxHP;

        // Create scene elements
        this.createBackground();
        this.createCharacters();
        this.createHealthBars();
        this.createSpellBar();
        this.createCoinDisplay();
        this.createShopIcon();
        this.createQuestionIcon();

        // Start battle with first question
        this.battleState = 'battle';
        this.showQuestion();
    }

    createShopIcon() {
        // Shop icon background (top-right, next to enemy health bar)
        const iconX = this.cameras.main.width - 320;
        const iconY = 25;

        this.shopIconBg = this.add.graphics();
        this.shopIconBg.fillStyle(0xFFD700, 1);
        this.shopIconBg.fillRoundedRect(iconX, iconY, 45, 45, 8);
        this.shopIconBg.lineStyle(3, 0xDAA520, 1);
        this.shopIconBg.strokeRoundedRect(iconX, iconY, 45, 45, 8);

        // Shopping bag icon (simple representation)
        this.shopIcon = this.add.graphics();
        this.shopIcon.fillStyle(0x8B4513, 1);
        // Bag body
        this.shopIcon.fillRoundedRect(iconX + 10, iconY + 18, 25, 20, 4);
        // Bag handle
        this.shopIcon.lineStyle(3, 0x8B4513, 1);
        this.shopIcon.beginPath();
        this.shopIcon.arc(iconX + 22, iconY + 18, 8, Math.PI, 0, false);
        this.shopIcon.strokePath();

        // "SHOP" text below icon
        this.shopLabel = this.add.text(iconX + 22, iconY + 50, 'SHOP', {
            fontFamily: 'Fredoka One',
            fontSize: '12px',
            color: '#FFD700',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);

        // Make clickable area
        this.shopHitArea = this.add.rectangle(iconX + 22, iconY + 22, 50, 50, 0x000000, 0)
            .setInteractive({ useHandCursor: true });

        this.shopHitArea.on('pointerover', () => {
            this.shopIconBg.clear();
            this.shopIconBg.fillStyle(0xFFA500, 1);
            this.shopIconBg.fillRoundedRect(iconX, iconY, 45, 45, 8);
            this.shopIconBg.lineStyle(3, 0xFF8C00, 1);
            this.shopIconBg.strokeRoundedRect(iconX, iconY, 45, 45, 8);
        });

        this.shopHitArea.on('pointerout', () => {
            this.shopIconBg.clear();
            this.shopIconBg.fillStyle(0xFFD700, 1);
            this.shopIconBg.fillRoundedRect(iconX, iconY, 45, 45, 8);
            this.shopIconBg.lineStyle(3, 0xDAA520, 1);
            this.shopIconBg.strokeRoundedRect(iconX, iconY, 45, 45, 8);
        });

        this.shopHitArea.on('pointerdown', () => {
            if (!this.shopOpen) {
                this.openShop();
            }
        });

        this.shopOpen = false;
    }

    createQuestionIcon() {
        // Question icon (next to shop icon)
        const iconX = this.cameras.main.width - 385;
        const iconY = 25;

        this.questionIconBg = this.add.graphics();
        this.questionIconBg.fillStyle(0x9C27B0, 1); // Purple
        this.questionIconBg.fillRoundedRect(iconX, iconY, 45, 45, 8);
        this.questionIconBg.lineStyle(3, 0x7B1FA2, 1);
        this.questionIconBg.strokeRoundedRect(iconX, iconY, 45, 45, 8);

        // Question mark icon
        this.questionIcon = this.add.text(iconX + 22, iconY + 22, '?', {
            fontFamily: 'Fredoka One',
            fontSize: '28px',
            color: '#ffffff'
        }).setOrigin(0.5);

        // "QUESTION" text below icon
        this.questionLabel = this.add.text(iconX + 22, iconY + 50, 'QUESTION', {
            fontFamily: 'Fredoka One',
            fontSize: '10px',
            color: '#9C27B0',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);

        // Make clickable area
        this.questionHitArea = this.add.rectangle(iconX + 22, iconY + 22, 50, 50, 0x000000, 0)
            .setInteractive({ useHandCursor: true });

        this.questionHitArea.on('pointerover', () => {
            this.questionIconBg.clear();
            this.questionIconBg.fillStyle(0xAB47BC, 1);
            this.questionIconBg.fillRoundedRect(iconX, iconY, 45, 45, 8);
            this.questionIconBg.lineStyle(3, 0x8E24AA, 1);
            this.questionIconBg.strokeRoundedRect(iconX, iconY, 45, 45, 8);
        });

        this.questionHitArea.on('pointerout', () => {
            this.questionIconBg.clear();
            this.questionIconBg.fillStyle(0x9C27B0, 1);
            this.questionIconBg.fillRoundedRect(iconX, iconY, 45, 45, 8);
            this.questionIconBg.lineStyle(3, 0x7B1FA2, 1);
            this.questionIconBg.strokeRoundedRect(iconX, iconY, 45, 45, 8);
        });

        this.questionHitArea.on('pointerdown', () => {
            if (!this.questionVisible && !this.shopOpen && this.battleState === 'battle') {
                this.showQuestionModal();
            }
        });

        // Initially hidden until first question loads
        this.setQuestionIconVisible(false);
    }

    setQuestionIconVisible(visible) {
        if (this.questionIconBg) this.questionIconBg.setVisible(visible);
        if (this.questionIcon) this.questionIcon.setVisible(visible);
        if (this.questionLabel) this.questionLabel.setVisible(visible);
        if (this.questionHitArea) {
            this.questionHitArea.setVisible(visible);
            if (visible) {
                this.questionHitArea.setInteractive({ useHandCursor: true });
            } else {
                this.questionHitArea.removeInteractive();
            }
        }
    }

    createBackground() {

       // background image (already preloaded)
    this.add.image(0, 0, "kingscourts_bg")
        .setOrigin(0, 0);

    // area name text stays
    this.add.text(this.cameras.main.centerX, 30, this.areaName, {
        fontFamily: 'Fredoka One',
        fontSize: '28px',
        color: '#ffffff',
        stroke: '#000000',
        strokeThickness: 4
    }).setOrigin(0.5);
    }

    createCharacters() {
        const centerY = this.cameras.main.centerY + 50;

        // Player (left side) - placeholder rectangle
        this.playerSprite = this.add.graphics();
        this.playerSprite.fillStyle(0x4169E1, 1); // Royal blue
        this.playerSprite.fillRoundedRect(150, centerY - 60, 80, 120, 8);
        this.playerSprite.lineStyle(3, 0x1E90FF, 1);
        this.playerSprite.strokeRoundedRect(150, centerY - 60, 80, 120, 8);

        // Player label
        this.add.text(190, centerY + 80, gameData.user?.username || 'Player', {
            fontFamily: 'Nunito',
            fontSize: '16px',
            color: '#ffffff',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);

        // Pet (near player) - small bouncing circle
        this.petSprite = this.add.graphics();
        this.petSprite.fillStyle(0xFFD700, 1); // Gold
        this.petSprite.fillCircle(280, centerY + 20, 20);
        this.petSprite.lineStyle(2, 0xFFA500, 1);
        this.petSprite.strokeCircle(280, centerY + 20, 20);

        // Pet bounce animation
        this.tweens.add({
            targets: this.petSprite,
            y: -10,
            duration: 500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Enemy (right side) - placeholder rectangle
        this.enemySprite = this.add.graphics();
        this.enemySprite.fillStyle(this.currentEnemy.color, 1);
        this.enemySprite.fillRoundedRect(this.cameras.main.width - 230, centerY - 70, 100, 140, 8);
        this.enemySprite.lineStyle(3, 0x000000, 0.5);
        this.enemySprite.strokeRoundedRect(this.cameras.main.width - 230, centerY - 70, 100, 140, 8);

        // Enemy label
        this.add.text(this.cameras.main.width - 180, centerY + 90, this.currentEnemy.name, {
            fontFamily: 'Nunito',
            fontSize: '16px',
            color: '#ffffff',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);

        // Enemy idle animation (slight wobble)
        this.tweens.add({
            targets: this.enemySprite,
            scaleX: 1.05,
            scaleY: 0.95,
            duration: 800,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }

    createHealthBars() {
        // Player health bar (top-left)
        this.playerHealthBg = this.add.graphics();
        this.playerHealthBg.fillStyle(0x333333, 1);
        this.playerHealthBg.fillRoundedRect(20, 70, 250, 30, 6);

        this.playerHealthBar = this.add.graphics();
        this.updateHealthBar(this.playerHealthBar, 20, 70, 250, 30, this.playerHP, this.playerMaxHP, 0x4EC5F1);

        this.playerHealthText = this.add.text(145, 85, `${this.playerHP}/${this.playerMaxHP}`, {
            fontFamily: 'Nunito',
            fontSize: '14px',
            color: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        this.add.text(20, 50, 'Your HP', {
            fontFamily: 'Fredoka One',
            fontSize: '18px',
            color: '#ffffff',
            stroke: '#000000',
            strokeThickness: 2
        });

        // Enemy health bar (top-right)
        const enemyBarX = this.cameras.main.width - 270;

        this.enemyHealthBg = this.add.graphics();
        this.enemyHealthBg.fillStyle(0x333333, 1);
        this.enemyHealthBg.fillRoundedRect(enemyBarX, 70, 250, 30, 6);

        this.enemyHealthBar = this.add.graphics();
        this.updateHealthBar(this.enemyHealthBar, enemyBarX, 70, 250, 30, this.enemyHP, this.enemyMaxHP, 0xDC143C);

        this.enemyHealthText = this.add.text(enemyBarX + 125, 85, `${this.enemyHP}/${this.enemyMaxHP}`, {
            fontFamily: 'Nunito',
            fontSize: '14px',
            color: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        this.add.text(enemyBarX, 50, 'Enemy HP', {
            fontFamily: 'Fredoka One',
            fontSize: '18px',
            color: '#ffffff',
            stroke: '#000000',
            strokeThickness: 2
        });
    }

    updateHealthBar(graphics, x, y, width, height, current, max, color) {
        graphics.clear();
        const fillWidth = Math.max(0, (current / max) * (width - 4));
        graphics.fillStyle(color, 1);
        graphics.fillRoundedRect(x + 2, y + 2, fillWidth, height - 4, 4);
    }

    createSpellBar() {
        // Spell bar at bottom of screen
        this.spellBarBg = this.add.graphics();
        this.spellBarBg.fillStyle(0x000000, 0.5);
        this.spellBarBg.fillRoundedRect(20, this.cameras.main.height - 80, 300, 60, 8);

        this.add.text(30, this.cameras.main.height - 75, 'Spells:', {
            fontFamily: 'Fredoka One',
            fontSize: '14px',
            color: '#ffffff'
        });

        this.spellSlots = [];
        for (let i = 0; i < 3; i++) {
            const slot = this.add.graphics();
            slot.fillStyle(0x444444, 1);
            slot.fillRoundedRect(100 + (i * 70), this.cameras.main.height - 65, 55, 40, 6);
            slot.lineStyle(2, 0x666666, 1);
            slot.strokeRoundedRect(100 + (i * 70), this.cameras.main.height - 65, 55, 40, 6);
            this.spellSlots.push(slot);
        }

        this.spellIcons = [];
        this.spellTexts = [];
    }

    createCoinDisplay() {
        // Coin display (top-center)
        this.coinBg = this.add.graphics();
        this.coinBg.fillStyle(0x000000, 0.5);
        this.coinBg.fillRoundedRect(this.cameras.main.centerX - 60, 10, 120, 35, 8);

        // Coin icon (circle)
        this.coinIcon = this.add.graphics();
        this.coinIcon.fillStyle(0xFFD700, 1);
        this.coinIcon.fillCircle(this.cameras.main.centerX - 40, 27, 12);
        this.coinIcon.lineStyle(2, 0xDAA520, 1);
        this.coinIcon.strokeCircle(this.cameras.main.centerX - 40, 27, 12);

        this.coinText = this.add.text(this.cameras.main.centerX + 10, 27, this.playerCoins.toString(), {
            fontFamily: 'Fredoka One',
            fontSize: '20px',
            color: '#FFD700',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);
    }

    openShop() {
        if (this.shopOpen) return;
        this.shopOpen = true;

        // Track if question was visible before opening shop
        this.questionWasVisible = this.questionVisible;

        // Hide question modal if it's showing
        if (this.questionVisible) {
            this.hideQuestion();
        }

        // Also hide the question icon while shop is open
        this.setQuestionIconVisible(false);

        // Create shop overlay
        this.shopOverlay = this.add.graphics();
        this.shopOverlay.fillStyle(0x000000, 0.7);
        this.shopOverlay.fillRect(0, 0, this.cameras.main.width, this.cameras.main.height);

        // Shop panel
        const panelX = this.cameras.main.centerX - 200;
        const panelY = this.cameras.main.centerY - 180;

        this.shopPanel = this.add.graphics();
        this.shopPanel.fillStyle(0xF5E6C8, 1);
        this.shopPanel.fillRoundedRect(panelX, panelY, 400, 360, 16);
        this.shopPanel.lineStyle(4, 0xDCC9A3, 1);
        this.shopPanel.strokeRoundedRect(panelX, panelY, 400, 360, 16);

        // Close button (X) in top-right corner of panel
        this.closeShopBtn = this.add.text(panelX + 375, panelY + 15, 'X', {
            fontFamily: 'Fredoka One',
            fontSize: '24px',
            color: '#666666'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });

        this.closeShopBtn.on('pointerover', () => this.closeShopBtn.setStyle({ color: '#DC143C' }));
        this.closeShopBtn.on('pointerout', () => this.closeShopBtn.setStyle({ color: '#666666' }));
        this.closeShopBtn.on('pointerdown', () => this.closeShop());

        // Shop title
        this.shopTitle = this.add.text(this.cameras.main.centerX, panelY + 30, 'Spell Shop', {
            fontFamily: 'Fredoka One',
            fontSize: '32px',
            color: '#3D3D3D'
        }).setOrigin(0.5);

        this.shopSubtitle = this.add.text(this.cameras.main.centerX, panelY + 60, 'Buy spells for this battle (max 3)', {
            fontFamily: 'Nunito',
            fontSize: '14px',
            color: '#666666'
        }).setOrigin(0.5);

        // Spell options
        this.shopSpellButtons = [];
        const spellKeys = ['heal', 'power', 'shield'];
        const spellY = panelY + 100;

        spellKeys.forEach((key, index) => {
            const spell = this.SPELLS[key];
            const btnY = spellY + (index * 70);

            // Spell button background
            const btn = this.add.graphics();
            btn.fillStyle(spell.color, 0.3);
            btn.fillRoundedRect(panelX + 20, btnY, 360, 55, 8);
            btn.lineStyle(2, spell.color, 1);
            btn.strokeRoundedRect(panelX + 20, btnY, 360, 55, 8);

            // Spell icon
            const icon = this.add.graphics();
            icon.fillStyle(spell.color, 1);
            icon.fillCircle(panelX + 50, btnY + 27, 18);

            // Spell name and cost
            const nameText = this.add.text(panelX + 80, btnY + 15, spell.name, {
                fontFamily: 'Fredoka One',
                fontSize: '18px',
                color: '#3D3D3D'
            });

            const costText = this.add.text(panelX + 80, btnY + 35, `Cost: ${spell.cost} coins`, {
                fontFamily: 'Nunito',
                fontSize: '14px',
                color: '#666666'
            });

            // Buy button - check if already purchased
            const alreadyOwned = this.purchasedSpells.includes(key);
            const buyBtn = this.add.text(panelX + 320, btnY + 27, alreadyOwned ? 'OWNED' : 'BUY', {
                fontFamily: 'Fredoka One',
                fontSize: '16px',
                color: '#ffffff',
                backgroundColor: alreadyOwned ? '#666666' : '#4EC5F1',
                padding: { x: 12, y: 6 }
            }).setOrigin(0.5);

            if (!alreadyOwned) {
                buyBtn.setInteractive({ useHandCursor: true });
                buyBtn.on('pointerover', () => buyBtn.setStyle({ backgroundColor: '#3BA8D8' }));
                buyBtn.on('pointerout', () => buyBtn.setStyle({ backgroundColor: '#4EC5F1' }));
                buyBtn.on('pointerdown', () => this.buySpell(key, buyBtn));
            }

            this.shopSpellButtons.push({ btn, icon, nameText, costText, buyBtn, key });
        });

        // Close button at bottom
        this.closeShopBtnBottom = this.add.text(this.cameras.main.centerX, panelY + 320, 'CLOSE', {
            fontFamily: 'Fredoka One',
            fontSize: '24px',
            color: '#ffffff',
            backgroundColor: '#666666',
            padding: { x: 30, y: 12 }
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });

        this.closeShopBtnBottom.on('pointerover', () => this.closeShopBtnBottom.setStyle({ backgroundColor: '#444444' }));
        this.closeShopBtnBottom.on('pointerout', () => this.closeShopBtnBottom.setStyle({ backgroundColor: '#666666' }));
        this.closeShopBtnBottom.on('pointerdown', () => this.closeShop());
    }

    closeShop() {
        if (!this.shopOpen) return;
        this.shopOpen = false;

        // Clean up shop UI
        this.shopOverlay.destroy();
        this.shopPanel.destroy();
        this.shopTitle.destroy();
        this.shopSubtitle.destroy();
        this.closeShopBtn.destroy();
        this.closeShopBtnBottom.destroy();
        this.shopSpellButtons.forEach(item => {
            item.btn.destroy();
            item.icon.destroy();
            item.nameText.destroy();
            item.costText.destroy();
            item.buyBtn.destroy();
        });

        // Restore question modal if it was visible before opening shop
        if (this.questionWasVisible && this.questionOverlay) {
            this.questionOverlay.setVisible(true);
            this.questionPanel.setVisible(true);
            this.questionText.setVisible(true);
            if (this.submitBtn) this.submitBtn.setVisible(true);
            if (this.questionCloseBtn) this.questionCloseBtn.setVisible(true);
            if (this.answerButtons) {
                this.answerButtons.forEach(btn => btn.setVisible(true));
            }
            this.questionVisible = true;
            this.setQuestionIconVisible(false);
        } else {
            // Question wasn't visible, show the question icon
            this.setQuestionIconVisible(true);
        }
    }

    buySpell(spellKey, buyBtn) {
        const spell = this.SPELLS[spellKey];

        // Check if already purchased
        if (this.purchasedSpells.includes(spellKey)) {
            this.showMessage('Already purchased!', '#FF6600');
            return;
        }

        // Check if max spells reached
        if (this.purchasedSpells.length >= 3) {
            this.showMessage('Max 3 spells!', '#FF6600');
            return;
        }

        // Check if enough coins
        if (this.playerCoins < spell.cost) {
            this.showMessage('Not enough coins!', '#DC143C');
            return;
        }

        // Purchase spell
        this.playerCoins -= spell.cost;
        this.purchasedSpells.push(spellKey);
        this.coinText.setText(this.playerCoins.toString());

        // Update button
        buyBtn.setText('OWNED');
        buyBtn.setStyle({ backgroundColor: '#666666' });
        buyBtn.removeInteractive();

        // Update spell bar
        this.updateSpellBar();

        this.showMessage(`Bought ${spell.name}!`, '#2E7D32');
    }

    updateSpellBar() {
        // Clear existing icons
        this.spellIcons.forEach(icon => icon.destroy());
        this.spellTexts.forEach(text => text.destroy());
        this.spellIcons = [];
        this.spellTexts = [];

        // Add purchased spells to bar
        this.purchasedSpells.forEach((spellKey, index) => {
            const spell = this.SPELLS[spellKey];
            const x = 100 + (index * 70);
            const y = this.cameras.main.height - 65;

            // Clear slot
            this.spellSlots[index].clear();
            this.spellSlots[index].fillStyle(spell.color, 0.8);
            this.spellSlots[index].fillRoundedRect(x, y, 55, 40, 6);
            this.spellSlots[index].lineStyle(2, spell.color, 1);
            this.spellSlots[index].strokeRoundedRect(x, y, 55, 40, 6);

            // Add spell initial
            const initial = spellKey === 'heal' ? 'H' : spellKey === 'power' ? 'P' : 'S';
            const text = this.add.text(x + 27, y + 20, initial, {
                fontFamily: 'Fredoka One',
                fontSize: '20px',
                color: '#ffffff'
            }).setOrigin(0.5);
            this.spellTexts.push(text);
        });

        // Make spells interactive
        this.makeSpellsInteractive();
    }

    showMessage(text, color) {
        const msg = this.add.text(this.cameras.main.centerX, this.cameras.main.centerY + 150, text, {
            fontFamily: 'Fredoka One',
            fontSize: '20px',
            color: color,
            stroke: '#000000',
            strokeThickness: 3
        }).setOrigin(0.5);

        this.tweens.add({
            targets: msg,
            alpha: 0,
            y: msg.y - 30,
            duration: 1000,
            onComplete: () => msg.destroy()
        });
    }

    makeSpellsInteractive() {
        // Clear existing hit areas
        if (this.spellHitAreas) {
            this.spellHitAreas.forEach(area => area.destroy());
        }
        this.spellHitAreas = [];

        // Add new hit areas for purchased spells
        this.purchasedSpells.forEach((spellKey, index) => {
            if (this.usedSpells.includes(spellKey)) return;

            const x = 100 + (index * 70);
            const y = this.cameras.main.height - 65;

            const hitArea = this.add.rectangle(x + 27, y + 20, 55, 40, 0x000000, 0)
                .setInteractive({ useHandCursor: true });

            hitArea.on('pointerdown', () => {
                if (this.battleState === 'battle' && !this.shopOpen && !this.usedSpells.includes(spellKey)) {
                    this.useSpell(spellKey, index);
                }
            });

            // Store reference
            if (!this.spellHitAreas) this.spellHitAreas = [];
            this.spellHitAreas.push(hitArea);
        });
    }

    useSpell(spellKey, slotIndex) {
        const spell = this.SPELLS[spellKey];
        this.usedSpells.push(spellKey);

        // Gray out used spell
        const x = 100 + (slotIndex * 70);
        const y = this.cameras.main.height - 65;
        this.spellSlots[slotIndex].clear();
        this.spellSlots[slotIndex].fillStyle(0x444444, 1);
        this.spellSlots[slotIndex].fillRoundedRect(x, y, 55, 40, 6);

        // Apply effect
        const centerY = this.cameras.main.centerY + 50;
        const playerX = 150;

        switch(spell.effect) {
            case 'heal':
                const healAmount = Math.min(spell.value, this.playerMaxHP - this.playerHP);
                this.playerHP += healAmount;
                this.updateHealthBar(this.playerHealthBar, 20, 70, 250, 30, this.playerHP, this.playerMaxHP, 0x4EC5F1);
                this.playerHealthText.setText(`${this.playerHP}/${this.playerMaxHP}`);
                this.showMessage(`+${healAmount} HP!`, '#2E7D32');
                this.flashCharacter(this.playerSprite, 0x00FF00, playerX, centerY - 60, 80, 120);
                // Show heal number
                this.showHealNumber(playerX + 40, centerY - 30, healAmount);
                break;

            case 'doubleDamage':
                this.hasPowerStrike = true;
                this.showMessage('Next attack: 2x damage!', '#FF6600');
                this.flashCharacter(this.playerSprite, 0xFF6600, playerX, centerY - 60, 80, 120);
                break;

            case 'blockAttack':
                this.hasShield = true;
                this.showMessage('Shield activated!', '#4169E1');
                this.flashCharacter(this.playerSprite, 0x4169E1, playerX, centerY - 60, 80, 120);
                // Show shield icon above player
                this.showShieldEffect(playerX + 40, centerY - 80);
                break;
        }
    }

    showHealNumber(x, y, amount) {
        const healText = this.add.text(x, y, `+${amount}`, {
            fontFamily: 'Fredoka One',
            fontSize: '32px',
            color: '#00FF00',
            stroke: '#006600',
            strokeThickness: 4
        }).setOrigin(0.5);

        this.tweens.add({
            targets: healText,
            y: y - 60,
            alpha: 0,
            duration: 1200,
            ease: 'Power2',
            onComplete: () => healText.destroy()
        });
    }

    showShieldEffect(x, y) {
        const shield = this.add.graphics();
        shield.fillStyle(0x4169E1, 0.6);
        shield.fillCircle(x, y + 60, 50);
        shield.lineStyle(4, 0x1E90FF, 1);
        shield.strokeCircle(x, y + 60, 50);

        this.tweens.add({
            targets: shield,
            alpha: 0.3,
            scale: 1.1,
            duration: 500,
            yoyo: true,
            repeat: 2,
            onComplete: () => shield.destroy()
        });
    }

    flashCharacter(target, color, x, y, width, height) {
        // Enhanced flash effect with multiple pulses
        const flash = this.add.graphics();
        flash.fillStyle(color, 0.7);
        flash.fillRect(x, y, width, height);

        // Pulse animation
        this.tweens.add({
            targets: flash,
            alpha: 0,
            duration: 200,
            yoyo: true,
            repeat: 2,
            onComplete: () => flash.destroy()
        });

        // Also tint the target sprite briefly if it has setTint
        if (target && target.setTint) {
            target.setTint(color);
            this.time.delayedCall(600, () => target.clearTint());
        }
    }

    showDamageNumber(x, y, damage, color) {
        const damageText = this.add.text(x, y, `-${damage}`, {
            fontFamily: 'Fredoka One',
            fontSize: '36px',
            color: color,
            stroke: '#000000',
            strokeThickness: 4
        }).setOrigin(0.5);

        this.tweens.add({
            targets: damageText,
            y: y - 80,
            alpha: 0,
            duration: 1500,
            ease: 'Power2',
            onComplete: () => damageText.destroy()
        });
    }

    shakeSprite(sprite, intensity = 5) {
        const originalX = sprite.x || 0;
        this.tweens.add({
            targets: sprite,
            x: originalX + intensity,
            duration: 50,
            yoyo: true,
            repeat: 5,
            onComplete: () => {
                sprite.x = originalX;
            }
        });
    }

    async showQuestion() {
        // For testing, use mock questions
        // Later, integrate with API: const response = await api.getQuestion(this.getDifficultyNumber());

        const mockQuestions = {
            easy: [
                { id: 1, question: 'What is a good place to keep your money safe?', options: ['Under your pillow', 'In a bank', 'In your pocket', 'On the ground'], correct: 1 },
                { id: 2, question: 'If you save $1 each day for a week, how much will you have?', options: ['$5', '$6', '$7', '$8'], correct: 2 },
                { id: 3, question: 'What does "saving" money mean?', options: ['Spending it all', 'Giving it away', 'Keeping it for later', 'Throwing it away'], correct: 2 }
            ],
            medium: [
                { id: 4, question: 'Which is a NEED, not a want?', options: ['Video games', 'Food', 'Toys', 'Candy'], correct: 1 },
                { id: 5, question: 'What is a budget?', options: ['A type of toy', 'A plan for spending money', 'A type of bank', 'A credit card'], correct: 1 },
                { id: 6, question: 'You have $10 and want a $15 toy. What should you do?', options: ['Steal it', 'Save more money', 'Break the toy', 'Cry'], correct: 1 }
            ],
            hard: [
                { id: 7, question: 'What is "interest" on a savings account?', options: ['A fee you pay', 'Extra money the bank gives you', 'A type of bank', 'A credit score'], correct: 1 },
                { id: 8, question: 'Why should you compare prices before buying?', options: ['It\'s fun', 'To save money', 'To waste time', 'To annoy stores'], correct: 1 },
                { id: 9, question: 'What is a scam?', options: ['A good deal', 'A trick to steal your money', 'A type of bank', 'A savings account'], correct: 1 }
            ]
        };

        const questions = mockQuestions[this.difficulty];
        this.currentQuestion = questions[Math.floor(Math.random() * questions.length)];
        this.selectedAnswer = null; // Track selected answer

        // Create question modal
        this.questionOverlay = this.add.graphics();
        this.questionOverlay.fillStyle(0x000000, 0.5);
        this.questionOverlay.fillRect(0, 0, this.cameras.main.width, this.cameras.main.height);

        const panelX = this.cameras.main.centerX - 250;
        const panelY = this.cameras.main.centerY - 170;

        this.questionPanel = this.add.graphics();
        this.questionPanel.fillStyle(0xF5E6C8, 1);
        this.questionPanel.fillRoundedRect(panelX, panelY, 500, 340, 16);
        this.questionPanel.lineStyle(4, 0xDCC9A3, 1);
        this.questionPanel.strokeRoundedRect(panelX, panelY, 500, 340, 16);

        this.questionText = this.add.text(this.cameras.main.centerX, panelY + 45, this.currentQuestion.question, {
            fontFamily: 'Nunito',
            fontSize: '18px',
            color: '#3D3D3D',
            wordWrap: { width: 450 },
            align: 'center'
        }).setOrigin(0.5);

        // Answer buttons
        this.answerButtons = [];
        const letters = ['A', 'B', 'C', 'D'];

        this.currentQuestion.options.forEach((option, index) => {
            const col = index % 2;
            const row = Math.floor(index / 2);
            const btnX = panelX + 30 + (col * 235);
            const btnY = panelY + 95 + (row * 65);

            const btn = this.add.text(btnX, btnY, `${letters[index]}. ${option}`, {
                fontFamily: 'Nunito',
                fontSize: '14px',
                color: '#3D3D3D',
                backgroundColor: '#FFFDF8',
                padding: { x: 15, y: 10 },
                fixedWidth: 210,
                wordWrap: { width: 180 }
            }).setInteractive({ useHandCursor: true });

            btn.on('pointerover', () => {
                if (this.selectedAnswer !== index) {
                    btn.setStyle({ backgroundColor: '#E8F4FD' });
                }
            });
            btn.on('pointerout', () => {
                if (this.selectedAnswer !== index) {
                    btn.setStyle({ backgroundColor: '#FFFDF8' });
                }
            });
            btn.on('pointerdown', () => this.selectAnswer(index));

            this.answerButtons.push(btn);
        });

        // Submit button (initially disabled)
        this.submitBtn = this.add.text(this.cameras.main.centerX, panelY + 295, 'SUBMIT', {
            fontFamily: 'Fredoka One',
            fontSize: '20px',
            color: '#ffffff',
            backgroundColor: '#999999',
            padding: { x: 40, y: 10 }
        }).setOrigin(0.5);

        // Submit button starts disabled until an answer is selected
        this.submitBtnEnabled = false;

        // Close button (X) in top-right corner of question panel
        this.questionCloseBtn = this.add.text(panelX + 475, panelY + 15, 'X', {
            fontFamily: 'Fredoka One',
            fontSize: '24px',
            color: '#666666'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });

        this.questionCloseBtn.on('pointerover', () => this.questionCloseBtn.setStyle({ color: '#DC143C' }));
        this.questionCloseBtn.on('pointerout', () => this.questionCloseBtn.setStyle({ color: '#666666' }));
        this.questionCloseBtn.on('pointerdown', () => this.hideQuestion());

        // Set question as visible
        this.questionVisible = true;
        this.setQuestionIconVisible(false);
    }

    selectAnswer(index) {
        // Deselect previous answer
        if (this.selectedAnswer !== null) {
            this.answerButtons[this.selectedAnswer].setStyle({ backgroundColor: '#FFFDF8', color: '#3D3D3D' });
        }

        // Select new answer
        this.selectedAnswer = index;
        this.answerButtons[index].setStyle({ backgroundColor: '#4EC5F1', color: '#ffffff' });

        // Enable submit button
        if (!this.submitBtnEnabled) {
            this.submitBtnEnabled = true;
            this.submitBtn.setStyle({ backgroundColor: '#2E7D32' });
            this.submitBtn.setInteractive({ useHandCursor: true });
            this.submitBtn.on('pointerover', () => this.submitBtn.setStyle({ backgroundColor: '#1B5E20' }));
            this.submitBtn.on('pointerout', () => this.submitBtn.setStyle({ backgroundColor: '#2E7D32' }));
            this.submitBtn.on('pointerdown', () => this.submitAnswer());
        }
    }

    hideQuestion() {
        // Hide question modal elements (don't destroy them)
        this.questionVisible = false;

        if (this.questionOverlay) this.questionOverlay.setVisible(false);
        if (this.questionPanel) this.questionPanel.setVisible(false);
        if (this.questionText) this.questionText.setVisible(false);
        if (this.submitBtn) this.submitBtn.setVisible(false);
        if (this.questionCloseBtn) this.questionCloseBtn.setVisible(false);
        if (this.answerButtons) {
            this.answerButtons.forEach(btn => btn.setVisible(false));
        }

        // Show the question icon so user can reopen
        this.setQuestionIconVisible(true);
    }

    showQuestionModal() {
        // Show question modal elements
        this.questionVisible = true;

        if (this.questionOverlay) this.questionOverlay.setVisible(true);
        if (this.questionPanel) this.questionPanel.setVisible(true);
        if (this.questionText) this.questionText.setVisible(true);
        if (this.submitBtn) this.submitBtn.setVisible(true);
        if (this.questionCloseBtn) this.questionCloseBtn.setVisible(true);
        if (this.answerButtons) {
            this.answerButtons.forEach(btn => btn.setVisible(true));
        }

        // Hide the question icon
        this.setQuestionIconVisible(false);
    }

    submitAnswer() {
        if (this.selectedAnswer === null) return;

        const isCorrect = this.selectedAnswer === this.currentQuestion.correct;

        // Disable all buttons
        this.answerButtons.forEach(btn => btn.removeInteractive());
        this.submitBtn.removeInteractive();

        // Show correct/wrong feedback
        this.answerButtons[this.currentQuestion.correct].setStyle({ backgroundColor: '#90EE90', color: '#3D3D3D' });
        if (!isCorrect) {
            this.answerButtons[this.selectedAnswer].setStyle({ backgroundColor: '#FFB6C1', color: '#3D3D3D' });
        }

        // Update submit button to show result
        this.submitBtn.setText(isCorrect ? 'CORRECT!' : 'WRONG!');
        this.submitBtn.setStyle({ backgroundColor: isCorrect ? '#2E7D32' : '#DC143C' });

        // Delay before processing result
        this.time.delayedCall(1200, () => {
            this.clearQuestionModal();

            if (isCorrect) {
                this.playerAttack();
            } else {
                this.enemyAttack();
            }
        });
    }

    clearQuestionModal() {
        if (this.questionOverlay) this.questionOverlay.destroy();
        if (this.questionPanel) this.questionPanel.destroy();
        if (this.questionText) this.questionText.destroy();
        if (this.answerButtons) {
            this.answerButtons.forEach(btn => btn.destroy());
        }
        if (this.submitBtn) {
            this.submitBtn.destroy();
        }
        if (this.questionCloseBtn) {
            this.questionCloseBtn.destroy();
        }
        this.questionOverlay = null;
        this.questionPanel = null;
        this.questionText = null;
        this.answerButtons = null;
        this.submitBtn = null;
        this.questionCloseBtn = null;
        this.selectedAnswer = null;
        this.submitBtnEnabled = false;
        this.questionVisible = false;
    }

    playerAttack() {
        let damage = this.PLAYER_DAMAGE;
        const isPowerStrike = this.hasPowerStrike;

        // Check for power strike
        if (isPowerStrike) {
            damage = 50;
            this.hasPowerStrike = false;
        }

        // Apply damage
        this.enemyHP = Math.max(0, this.enemyHP - damage);

        const centerY = this.cameras.main.centerY + 50;
        const enemyX = this.cameras.main.width - 230;

        // Step 1: Show "Correct!" message
        this.showMessage(isPowerStrike ? 'POWER STRIKE!' : 'Correct!', isPowerStrike ? '#FF6600' : '#2E7D32');

        // Step 2: Player jumps/moves toward enemy (after 300ms)
        this.time.delayedCall(300, () => {
            // Player lunge animation
            this.tweens.add({
                targets: this.playerSprite,
                x: 200,
                duration: 300,
                ease: 'Power2',
                yoyo: true,
                onYoyo: () => {
                    // Step 3: Impact! Flash and shake enemy
                    this.flashCharacter(this.enemySprite, 0xFF0000, enemyX, centerY - 70, 100, 140);
                    this.shakeSprite(this.enemySprite, 10);

                    // Show damage number floating up
                    this.showDamageNumber(enemyX + 50, centerY - 30, damage, '#FF0000');

                    // Screen shake for power strike
                    if (isPowerStrike) {
                        this.cameras.main.shake(200, 0.01);
                    }
                }
            });
        });

        // Step 4: Update health bar (after 800ms)
        this.time.delayedCall(800, () => {
            const enemyBarX = this.cameras.main.width - 270;
            const startHP = this.enemyHP + damage;
            let currentHP = startHP;

            // Animate health bar decreasing
            this.tweens.addCounter({
                from: startHP,
                to: this.enemyHP,
                duration: 500,
                onUpdate: (tween) => {
                    currentHP = Math.round(tween.getValue());
                    this.updateHealthBar(this.enemyHealthBar, enemyBarX, 70, 250, 30, currentHP, this.enemyMaxHP, 0xDC143C);
                    this.enemyHealthText.setText(`${currentHP}/${this.enemyMaxHP}`);
                }
            });
        });

        // Step 5: Check win condition and show next question (after 2000ms)
        this.time.delayedCall(2000, () => {
            if (this.enemyHP <= 0) {
                this.battleVictory();
            } else {
                this.showQuestion();
            }
        });
    }

    enemyAttack() {
        const centerY = this.cameras.main.centerY + 50;
        const playerX = 150;

        // Check for shield
        if (this.hasShield) {
            this.hasShield = false;
            this.showMessage('Wrong answer...', '#DC143C');

            // Enemy still lunges but shield blocks
            this.time.delayedCall(500, () => {
                this.tweens.add({
                    targets: this.enemySprite,
                    x: -150,
                    duration: 300,
                    ease: 'Power2',
                    yoyo: true,
                    onYoyo: () => {
                        // Shield block effect
                        this.showMessage('Shield blocked the attack!', '#4169E1');
                        const shieldFlash = this.add.graphics();
                        shieldFlash.fillStyle(0x4169E1, 0.8);
                        shieldFlash.fillCircle(playerX + 40, centerY, 80);
                        this.tweens.add({
                            targets: shieldFlash,
                            alpha: 0,
                            scale: 1.5,
                            duration: 500,
                            onComplete: () => shieldFlash.destroy()
                        });
                    }
                });
            });

            this.time.delayedCall(2000, () => this.showQuestion());
            return;
        }

        const damage = this.currentEnemy.attack;
        this.playerHP = Math.max(0, this.playerHP - damage);

        // Step 1: Show "Wrong!" message
        this.showMessage('Wrong answer...', '#DC143C');

        // Step 2: Enemy lunges toward player (after 500ms)
        this.time.delayedCall(500, () => {
            this.tweens.add({
                targets: this.enemySprite,
                x: -150,
                duration: 300,
                ease: 'Power2',
                yoyo: true,
                onYoyo: () => {
                    // Step 3: Impact! Flash and shake player
                    this.flashCharacter(this.playerSprite, 0xFF0000, playerX, centerY - 60, 80, 120);
                    this.shakeSprite(this.playerSprite, 10);

                    // Show damage number floating up
                    this.showDamageNumber(playerX + 40, centerY - 30, damage, '#FF0000');

                    // Camera shake
                    this.cameras.main.shake(150, 0.008);
                }
            });
        });

        // Step 4: Update health bar (after 1000ms)
        this.time.delayedCall(1000, () => {
            const startHP = this.playerHP + damage;
            let currentHP = startHP;

            // Animate health bar decreasing
            this.tweens.addCounter({
                from: startHP,
                to: this.playerHP,
                duration: 500,
                onUpdate: (tween) => {
                    currentHP = Math.round(tween.getValue());
                    this.updateHealthBar(this.playerHealthBar, 20, 70, 250, 30, currentHP, this.playerMaxHP, 0x4EC5F1);
                    this.playerHealthText.setText(`${currentHP}/${this.playerMaxHP}`);
                }
            });
        });

        // Step 5: Check lose condition and show next question (after 2000ms)
        this.time.delayedCall(2000, () => {
            if (this.playerHP <= 0) {
                this.battleDefeat();
            } else {
                this.showQuestion();
            }
        });
    }

    battleVictory() {
        this.battleState = 'ended';

        // Award coins
        const coinsWon = this.currentEnemy.coins;
        this.playerCoins += coinsWon;

        // Update global game data
        if (gameData.user) {
            gameData.user.wins = (gameData.user.wins || 0) + 1;
            gameData.user.coins = this.playerCoins;
        }

        // Show victory overlay
        this.showResultOverlay(true, coinsWon);
    }

    battleDefeat() {
        this.battleState = 'ended';

        // Show defeat overlay
        this.showResultOverlay(false, 0);
    }

    showResultOverlay(victory, coinsWon) {
        // Overlay
        const overlay = this.add.graphics();
        overlay.fillStyle(0x000000, 0.7);
        overlay.fillRect(0, 0, this.cameras.main.width, this.cameras.main.height);

        // Result panel
        const panelX = this.cameras.main.centerX - 175;
        const panelY = this.cameras.main.centerY - 120;

        const panel = this.add.graphics();
        panel.fillStyle(victory ? 0xF5E6C8 : 0x4a4a4a, 1);
        panel.fillRoundedRect(panelX, panelY, 350, 240, 16);
        panel.lineStyle(4, victory ? 0xFFD700 : 0x8B0000, 1);
        panel.strokeRoundedRect(panelX, panelY, 350, 240, 16);

        // Title
        const title = this.add.text(this.cameras.main.centerX, panelY + 40, victory ? 'VICTORY!' : 'DEFEAT', {
            fontFamily: 'Fredoka One',
            fontSize: '42px',
            color: victory ? '#2E7D32' : '#DC143C',
            stroke: '#000000',
            strokeThickness: 3
        }).setOrigin(0.5);

        // Message
        let message = victory
            ? `You defeated ${this.currentEnemy.name}!\n\n+${coinsWon} coins earned!`
            : `${this.currentEnemy.name} won...\n\nTry again!`;

        const msgText = this.add.text(this.cameras.main.centerX, panelY + 110, message, {
            fontFamily: 'Nunito',
            fontSize: '18px',
            color: victory ? '#3D3D3D' : '#ffffff',
            align: 'center'
        }).setOrigin(0.5);

        // Continue button
        const continueBtn = this.add.text(this.cameras.main.centerX, panelY + 190, 'CONTINUE', {
            fontFamily: 'Fredoka One',
            fontSize: '20px',
            color: '#ffffff',
            backgroundColor: victory ? '#4EC5F1' : '#666666',
            padding: { x: 30, y: 12 }
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });

        continueBtn.on('pointerover', () => continueBtn.setStyle({ backgroundColor: victory ? '#3BA8D8' : '#555555' }));
        continueBtn.on('pointerout', () => continueBtn.setStyle({ backgroundColor: victory ? '#4EC5F1' : '#666666' }));
        continueBtn.on('pointerdown', () => {
            // TODO: Return to MapScene
            // For now, return to MenuScene
            this.scene.start('MenuScene');
        });
    }

    getDifficultyNumber() {
        return this.difficulty === 'easy' ? 1 : this.difficulty === 'medium' ? 2 : 3;
    }
}
