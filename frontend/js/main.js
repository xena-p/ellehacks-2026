// Initialize the Phaser Game
const game = new Phaser.Game(config);

// Global game data (will be populated after login)
let gameData = {
    user: null,
    isLoggedIn: false
};
