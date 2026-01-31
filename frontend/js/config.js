// Phaser Game Configuration
const config = {
    type: Phaser.AUTO,
    width: 1480,
    height: 730,
    parent: 'game-container',
    backgroundColor: '#5BA3C0',
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    },
    dom: {
        createContainer: true
    },
    scene: [MenuScene, MapScene, BattleScene]
};
