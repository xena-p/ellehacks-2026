let gameData = {
    user: null,
    isLoggedIn: false,
    _logoutRequested: false,
    _booting: true
};

const __originalScenePluginStart = Phaser.Scenes.ScenePlugin.prototype.start;
Phaser.Scenes.ScenePlugin.prototype.start = function (key, data) {
    if (key === 'MenuScene' && !gameData._logoutRequested && !gameData._booting) {
        // Prevent any unsolicited return to the menu after boot.
        // If something tries to send you back, route to MapScene instead.
        // (This avoids getting stuck in an auto-menu loop after battle.)
        return __originalScenePluginStart.call(this, 'MapScene');
    }
    if (key === 'MenuScene') {
        gameData._logoutRequested = false;
    }
    return __originalScenePluginStart.call(this, key, data);
};

const game = new Phaser.Game(config);
