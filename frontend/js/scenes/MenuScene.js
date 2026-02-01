class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
        this.isLoginMode = true;
        this.sparkles = [];
    }

    preload() {
        // Load assets needed for the menu
        this.load.image('sky-bg', 'assets/images/backgrounds/pixel-sky-background.png');

        //Map Background
        this.load.image("map", "assets/images/map/map.png");

        //Clouds for Map
        this.load.image("cloud1Sprite", "assets/images/cloud1.png");
        this.load.image("cloud2Sprite", "assets/images/cloud2.png");

        // Level icons / buttons
        this.load.image("level1Sprite", "assets/images/level1.png");
        this.load.image("level2Sprite", "assets/images/level2.png");
        this.load.image("level3Sprite", "assets/images/level3.png");
        this.load.image("level4Sprite", "assets/images/level4.png");
        this.load.image("level5Sprite", "assets/images/level5.png");

        //Heart Icons for Map Shop
        this.load.image("healthSmall", "assets/images/smallHp.png");
        this.load.image("healthMedium", "assets/images/medHp.png");
        this.load.image("healthLarge", "assets/images/largeHp.png");
        //Battle Backgrounds
        this.load.image('kingscourts_bg', 'assets/images/backgrounds/kingscourt_bg.png');
        this.load.image('frostpeak_bg', 'assets/images/backgrounds/FrostPeak_bg.jpg');
        this.load.image('cloudspire_bg', 'assets/images/backgrounds/Cloudspire_bg.png');
        this.load.image('ashbound_bg', 'assets/images/backgrounds/Ashbound_bg.png');
        this.load.image('havenfall_bg', 'assets/images/backgrounds/Havenfall_bg.png');


        //Battle labels
        this.load.image('kingscourts_label', "assets/images/level1.png");
        this.load.image("frostpeak_label", "assets/images/level2.png");
        this.load.image("cloudspire_label", "assets/images/level3.png");
        this.load.image("ashbound_label", "assets/images/level4.png");
        this.load.image("havenfall_label", "assets/images/level5.png");

        //Other labels
        this.load.image('hplabel',"assets/images/labels/labelbox.png");

        // Battle screen icons
        this.load.image('question_logo', "assets/images/icons/question_logo.png");
        this.load.image('shop_logo', "assets/images/icons/shop_logo.png");

        //Player & Pet
        this.load.image('player', 'assets/images/player/player.png');
        this.load.image('pet', 'assets/images/player/pet_cat.png');

        //Enemies
        this.load.image('kingscourt_enemy', 'assets/images/enemies/enemy_kingscourt.png');
        this.load.image('frostpeak_enemy', 'assets/images/enemies/enemy_FrostPeak.png');
        this.load.image('cloudspire_enemy', 'assets/images/enemies/enemy_Cloudspire.png');
        this.load.image('ashbound_enemy', 'assets/images/enemies/enemy_Ashbound.png');
        this.load.image('havenfall_enemy', 'assets/images/enemies/enemy_Havenfall.png');

        this.load.image("shopSprite", "assets/images/shop.png");

        // Logo/Favicon
        this.load.image('logo', 'assets/images/favicon.png');

    // Optional: background, UI, sounds
    // this.load.image("mapBg", "assets/map-bg.png");
    // this.load.audio("correct", "assets/correct.mp3");
    }

    create() {
        // Create the sky background
        this.createBackground();

        // Add logo at top left
        this.logo = this.add.image(300, 80, 'logo')
            .setOrigin(0.5)
            .setScale(0.15)
            .setDepth(100);

        // Create the animated game title
        this.createGameTitle();

        // Create the piggy bank mascot
        this.createMascot();

        // Create the login/register form
        this.createAuthForm();

        // Start sparkle effects
        this.startSparkleEffects();

        // Play entrance animations
        this.playEntranceAnimations();
    }

    // ============ SPARKLE SYSTEM ============
    createSparkle(x, y, color = 0xFFD700) {
        const sparkle = this.add.graphics();
        const size = Phaser.Math.Between(3, 6);

        // Draw a small diamond/star shape
        sparkle.fillStyle(color, 1);
        sparkle.beginPath();
        sparkle.moveTo(x, y - size);
        sparkle.lineTo(x + size * 0.5, y);
        sparkle.lineTo(x, y + size);
        sparkle.lineTo(x - size * 0.5, y);
        sparkle.closePath();
        sparkle.fillPath();

        // Add a white center for extra sparkle
        sparkle.fillStyle(0xFFFFFF, 0.8);
        sparkle.fillCircle(x, y, size * 0.3);

        sparkle.setAlpha(0);
        sparkle.setScale(0);
        sparkle.setDepth(100);

        // Animate the sparkle
        this.tweens.add({
            targets: sparkle,
            alpha: 1,
            scale: 1,
            duration: 200,
            ease: 'Back.easeOut',
            onComplete: () => {
                this.tweens.add({
                    targets: sparkle,
                    alpha: 0,
                    scale: 0.5,
                    duration: 300,
                    delay: 100,
                    ease: 'Power2',
                    onComplete: () => sparkle.destroy()
                });
            }
        });

        return sparkle;
    }

    startSparkleEffects() {
        // Sparkles around the title
        this.time.addEvent({
            delay: 300,
            callback: () => {
                if (this.gameTitle) {
                    const offsetX = Phaser.Math.Between(-150, 150);
                    const offsetY = Phaser.Math.Between(-30, 30);
                    this.createSparkle(
                        this.cameras.main.centerX + offsetX,
                        80 + offsetY,
                        Phaser.Math.RND.pick([0xFFD700, 0xFFFFFF, 0xFFA500])
                    );
                }
            },
            loop: true
        });

        // Sparkles from piggy bank coin slot
        this.time.addEvent({
            delay: 800,
            callback: () => {
                if (this.mascotContainer) {
                    for (let i = 0; i < 3; i++) {
                        this.time.delayedCall(i * 100, () => {
                            const offsetX = Phaser.Math.Between(-10, 10);
                            const offsetY = Phaser.Math.Between(-20, -5);
                            this.createSparkle(
                                this.mascotContainer.x + offsetX,
                                this.mascotContainer.y - 40 + offsetY,
                                0xFFD700
                            );
                        });
                    }
                }
            },
            loop: true
        });
    }

    // ============ GAME TITLE ============
    createGameTitle() {
        const centerX = this.cameras.main.centerX;

        // Create title container for animations
        this.titleContainer = this.add.container(centerX, -100);
        this.titleContainer.setDepth(50);

        // Main title text
        this.gameTitle = this.add.text(0, 0, '{PROJECT NAME!!!!}', {
            fontFamily: 'Fredoka One',
            fontSize: '64px',
            color: '#FFD700',
            stroke: '#8B4513',
            strokeThickness: 8
        }).setOrigin(0.5);

        // Subtitle
        this.gameSubtitle = this.add.text(0, 45, '{NEW PHRASE GOES HERE!!!!}]', {
            fontFamily: 'Nunito',
            fontSize: '18px',
            color: '#FFFFFF',
            stroke: '#000000',
            strokeThickness: 3
        }).setOrigin(0.5);

        // Add coin decorations on sides of title
        const leftCoin = this.createTitleCoin(-180, -5);
        const rightCoin = this.createTitleCoin(180, -5);

        this.titleContainer.add([this.gameTitle, this.gameSubtitle, leftCoin, rightCoin]);

        // Continuous gentle bounce animation
        this.tweens.add({
            targets: this.gameTitle,
            scaleX: 1.05,
            scaleY: 1.05,
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }

    createTitleCoin(x, y) {
        const coin = this.add.graphics();
        const size = 25;

        coin.fillStyle(0xFFD700, 1);
        coin.fillCircle(x, y, size);
        coin.lineStyle(3, 0xDAA520, 1);
        coin.strokeCircle(x, y, size);
        coin.fillStyle(0xFFFF99, 0.5);
        coin.fillCircle(x - 8, y - 8, 8);

        // Spin animation
        this.tweens.add({
            targets: coin,
            scaleX: 0.3,
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        return coin;
    }

    // ============ PIGGY BANK MASCOT ============
    createMascot() {
        const centerX = this.cameras.main.centerX;
        const centerY = this.cameras.main.centerY;

        // Position mascot to the left of the card
        const mascotX = centerX - 280;
        const mascotY = centerY + 20;

        this.mascotContainer = this.add.container(mascotX - 200, mascotY); // Start off-screen
        this.mascotContainer.setDepth(40);

        const mascot = this.add.graphics();

        // Main body (pink oval)
        mascot.fillStyle(0xFFB6C1, 1);
        mascot.fillEllipse(0, 0, 90, 70);

        // Body outline
        mascot.lineStyle(3, 0xFF69B4, 1);
        mascot.strokeEllipse(0, 0, 90, 70);

        // Snout
        mascot.fillStyle(0xFFC0CB, 1);
        mascot.fillEllipse(50, 5, 30, 25);
        mascot.lineStyle(2, 0xFF69B4, 1);
        mascot.strokeEllipse(50, 5, 30, 25);

        // Nostrils
        mascot.fillStyle(0xFF69B4, 1);
        mascot.fillCircle(45, 3, 4);
        mascot.fillCircle(55, 3, 4);

        // Ears
        mascot.fillStyle(0xFFB6C1, 1);
        mascot.beginPath();
        mascot.moveTo(-25, -30);
        mascot.lineTo(-35, -55);
        mascot.lineTo(-10, -35);
        mascot.closePath();
        mascot.fillPath();
        mascot.strokePath();

        mascot.beginPath();
        mascot.moveTo(5, -30);
        mascot.lineTo(15, -55);
        mascot.lineTo(25, -35);
        mascot.closePath();
        mascot.fillPath();
        mascot.strokePath();

        // Inner ears
        mascot.fillStyle(0xFFC0CB, 1);
        mascot.beginPath();
        mascot.moveTo(-22, -32);
        mascot.lineTo(-30, -48);
        mascot.lineTo(-13, -36);
        mascot.closePath();
        mascot.fillPath();

        mascot.beginPath();
        mascot.moveTo(8, -32);
        mascot.lineTo(15, -48);
        mascot.lineTo(22, -36);
        mascot.closePath();
        mascot.fillPath();

        // Coin slot on top
        mascot.fillStyle(0x333333, 1);
        mascot.fillRoundedRect(-20, -38, 40, 6, 3);

        // Legs
        mascot.fillStyle(0xFFB6C1, 1);
        mascot.fillRoundedRect(-35, 25, 18, 25, 5);
        mascot.fillRoundedRect(-10, 25, 18, 25, 5);
        mascot.fillRoundedRect(15, 25, 18, 25, 5);
        mascot.fillRoundedRect(40, 20, 15, 20, 5);

        // Curly tail
        mascot.lineStyle(4, 0xFF69B4, 1);
        mascot.beginPath();
        mascot.arc(-50, 0, 15, 0, Math.PI * 1.5, false);
        mascot.strokePath();

        this.mascotContainer.add(mascot);

        // Eyes (separate for blinking)
        this.leftEye = this.add.graphics();
        this.leftEye.fillStyle(0x000000, 1);
        this.leftEye.fillCircle(10, -10, 6);
        this.leftEye.fillStyle(0xFFFFFF, 1);
        this.leftEye.fillCircle(12, -12, 2);

        this.rightEye = this.add.graphics();
        this.rightEye.fillStyle(0x000000, 1);
        this.rightEye.fillCircle(30, -10, 6);
        this.rightEye.fillStyle(0xFFFFFF, 1);
        this.rightEye.fillCircle(32, -12, 2);

        this.mascotContainer.add([this.leftEye, this.rightEye]);

        // Blinking animation
        this.time.addEvent({
            delay: 3000,
            callback: () => this.mascotBlink(),
            loop: true
        });

        // Idle wobble animation
        this.tweens.add({
            targets: this.mascotContainer,
            angle: 3,
            duration: 800,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Gentle bounce
        this.tweens.add({
            targets: this.mascotContainer,
            y: mascotY - 5,
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut',
            delay: 500
        });
    }

    mascotBlink() {
        // Quick blink animation
        this.tweens.add({
            targets: [this.leftEye, this.rightEye],
            scaleY: 0.1,
            duration: 100,
            yoyo: true,
            ease: 'Power2'
        });
    }

    // ============ ENTRANCE ANIMATIONS ============
    playEntranceAnimations() {
        // Title drops from top
        this.tweens.add({
            targets: this.titleContainer,
            y: 80,
            duration: 800,
            ease: 'Bounce.easeOut',
            delay: 200
        });

        // Mascot slides in from left
        const centerX = this.cameras.main.centerX;
        const mascotTargetX = centerX - 280;

        this.tweens.add({
            targets: this.mascotContainer,
            x: mascotTargetX,
            duration: 600,
            ease: 'Back.easeOut',
            delay: 400
        });

        // Parchment card and form fade in (handled by existing elements)
        // The card is already created, but we can add a subtle effect
        if (this.formElement) {
            this.formElement.setAlpha(0);
            this.tweens.add({
                targets: this.formElement,
                alpha: 1,
                duration: 500,
                delay: 600
            });
        }
    }

    createBackground() {
        // Add the pixel sky background image
        const bg = this.add.image(0, 0, 'sky-bg');
        bg.setOrigin(0, 0);

        // Scale to fit the game dimensions
        bg.setDisplaySize(this.cameras.main.width, this.cameras.main.height);
    }

    createAuthForm() {
        const centerX = this.cameras.main.centerX;
        const centerY = this.cameras.main.centerY;

        // Create the parchment card background
        this.createParchmentCard(centerX, centerY);

        // Create the HTML form using Phaser DOM element
        const formHTML = this.createFormHTML();

        this.formElement = this.add.dom(centerX, centerY).createFromHTML(formHTML);

        // Add event listeners
        this.setupFormListeners();
    }

    createParchmentCard(x, y) {
        const cardWidth = 380;
        const cardHeight = 360;

        // Create card shadow
        const shadow = this.add.graphics();
        shadow.fillStyle(0x000000, 0.15);
        shadow.fillRoundedRect(x - cardWidth/2 + 8, y - cardHeight/2 + 8, cardWidth, cardHeight, 16);

        // Create main card
        const card = this.add.graphics();

        // Parchment background color
        card.fillStyle(0xF5E6C8, 1);
        card.fillRoundedRect(x - cardWidth/2, y - cardHeight/2, cardWidth, cardHeight, 16);

        // Add subtle border
        card.lineStyle(3, 0xDCC9A3, 1);
        card.strokeRoundedRect(x - cardWidth/2, y - cardHeight/2, cardWidth, cardHeight, 16);

        // Add corner decorations (folded corners effect)
        this.addCornerFolds(card, x, y, cardWidth, cardHeight);
    }

    addCornerFolds(graphics, x, y, width, height) {
        const foldSize = 20;
        const halfW = width / 2;
        const halfH = height / 2;

        // Top-right fold
        graphics.fillStyle(0xE8D4B0, 1);
        graphics.beginPath();
        graphics.moveTo(x + halfW - foldSize, y - halfH);
        graphics.lineTo(x + halfW, y - halfH);
        graphics.lineTo(x + halfW, y - halfH + foldSize);
        graphics.closePath();
        graphics.fillPath();

        // Bottom-left fold
        graphics.beginPath();
        graphics.moveTo(x - halfW, y + halfH - foldSize);
        graphics.lineTo(x - halfW, y + halfH);
        graphics.lineTo(x - halfW + foldSize, y + halfH);
        graphics.closePath();
        graphics.fillPath();
    }

    createFormHTML() {
        const title = this.isLoginMode ? 'Welcome back! Log in to play!' : 'Create your account!';
        const buttonText = this.isLoginMode ? 'Log In' : 'Sign Up';
        const switchText = this.isLoginMode
            ? "Don't have an account? <a href='#' id='switch-mode'>Sign up</a>"
            : "Already have an account? <a href='#' id='switch-mode'>Log in</a>";

        return `
            <div class="auth-form">
                <h1 class="auth-title">${title}</h1>

                <form id="auth-form">
                    <div class="input-group">
                        <input type="text" id="username" name="username" placeholder="Username" required>
                    </div>

                    <div class="input-group">
                        <input type="password" id="password" name="password" placeholder="Password" required>
                    </div>

                    <button type="submit" class="submit-btn">${buttonText}</button>
                </form>

                <div class="switch-mode">
                    ${switchText}
                </div>

                <div id="error-message" class="error-message"></div>
            </div>
        `;
    }

    setupFormListeners() {
        const form = this.formElement.getChildByID('auth-form');
        const switchLink = this.formElement.getChildByID('switch-mode');

        // Form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        // Switch between login and register
        switchLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMode();
        });
    }

    toggleMode() {
        this.isLoginMode = !this.isLoginMode;

        // Remove old form and create new one
        this.formElement.destroy();

        const centerX = this.cameras.main.centerX;
        const centerY = this.cameras.main.centerY;

        const formHTML = this.createFormHTML();
        this.formElement = this.add.dom(centerX, centerY).createFromHTML(formHTML);
        this.setupFormListeners();
    }

    handleSubmit() {
        const username = this.formElement.getChildByID('username').value.trim();
        const password = this.formElement.getChildByID('password').value;
        const errorDiv = this.formElement.getChildByID('error-message');

        // Reset error styling
        errorDiv.style.color = '#DC143C';

        // Basic validation
        if (!username || !password) {
            errorDiv.textContent = 'Please fill in all fields';
            return;
        }

        if (username.length < 3) {
            errorDiv.textContent = 'Username must be at least 3 characters';
            return;
        }

        if (password.length < 4) {
            errorDiv.textContent = 'Password must be at least 4 characters';
            return;
        }

        // Clear any previous errors
        errorDiv.textContent = '';

        // Both login and signup work the same way locally - no backend required
        this.startGame(username);
    }

    startGame(username) {
        const errorDiv = this.formElement.getChildByID('error-message');

        // Store a simple token for API calls (can be any string for local mode)
        localStorage.setItem('authToken', 'local-user-token');

        // Store user data
        gameData.user = {
            username: username,
            level: 1,
            wins: 0,
            coins: 50,
            max_hp: 100
        };
        gameData.isLoggedIn = true;

        // Show success message
        const message = this.isLoginMode ? 'Login successful!' : 'Account created!';
        errorDiv.style.color = '#2E7D32';
        errorDiv.textContent = `${message} Starting game...`;

        // Start MapScene after short delay
        setTimeout(() => {
            this.scene.start('MapScene');
        }, 1000);
    }
}
