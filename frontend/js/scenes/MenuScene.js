class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
        this.isLoginMode = true;
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


        //Battle Backgrounds
        this.load.image('kingscourts_bg', 'assets/images/backgrounds/kingscourt_bg.png');

        //Player

        //Enemies 
    
        this.load.image("shopSprite", "assets/images/shop.png");
    // Optional: background, UI, sounds
    // this.load.image("mapBg", "assets/map-bg.png");
    // this.load.audio("correct", "assets/correct.mp3");
    }

    create() {
        // Create the sky background
        this.createBackground();

        // Create the login/register form
        this.createAuthForm();
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
        const title = this.isLoginMode ? 'Welcome back. Log in to play!' : 'Create your account!';
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
        const username = this.formElement.getChildByID('username').value;
        const password = this.formElement.getChildByID('password').value;
        const errorDiv = this.formElement.getChildByID('error-message');

        // Basic validation
        if (!username || !password) {
            errorDiv.textContent = 'Please fill in all fields';
            return;
        }

        if (password.length < 4) {
            errorDiv.textContent = 'Password must be at least 4 characters';
            return;
        }

        // Clear any previous errors
        errorDiv.textContent = '';

        if (this.isLoginMode) {
            this.login(username, password);
        } else {
            this.register(username, password);
        }
    }

    async login(username, password) {
        const errorDiv = this.formElement.getChildByID('error-message');
        const submitBtn = this.formElement.getChildByName('submit-btn');

        try {
            // TODO: Replace with actual API call
            // const response = await fetch('/api/login/', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ username, password })
            // });
            // const data = await response.json();

            // For now, simulate successful login
            console.log('Login attempt:', { username, password });

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 500));

            // Store user data
            gameData.user = {
                username: username,
                level: 1,
                wins: 0,
                coins: 50,
                max_hp: 100
            };
            gameData.isLoggedIn = true;

            // Show success and launch battle
            errorDiv.style.color = '#2E7D32';
            errorDiv.textContent = 'Login successful! Starting battle...';

            // Start BattleScene after short delay (for testing)
            setTimeout(() => {
                this.scene.start('MapScene');
                //this.scene.start('BattleScene', { difficulty: 'easy', area: 'Savings Village' });
            }, 1000);

        } catch (error) {
            errorDiv.textContent = 'Login failed. Please try again.';
            console.error('Login error:', error);
        }
    }

    async register(username, password) {
        const errorDiv = this.formElement.getChildByID('error-message');

        try {
            // TODO: Replace with actual API call
            // const response = await fetch('/api/register/', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ username, password })
            // });
            // const data = await response.json();

            // For now, simulate successful registration
            console.log('Register attempt:', { username, password });

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 500));

            // Show success and switch to login
            errorDiv.style.color = '#2E7D32';
            errorDiv.textContent = 'Account created! Please log in.';

            // Switch to login mode after short delay
            setTimeout(() => {
                this.isLoginMode = true;
                this.toggleMode();
            }, 1500);

        } catch (error) {
            errorDiv.textContent = 'Registration failed. Please try again.';
            console.error('Register error:', error);
        }
    }
}
