import Phaser from "phaser";

export default class BattleScene extends Phaser.Scene{
  constructor(){
    super("BattleScene")
  }
  preload(){
    console.log("BattleScene preload running");
    this.load.image("BG_1_castle","assets/BattleBG_castle.png");
    this.load.image("Player","assets/Player.png");

  }

  create(){
    console.log("BattleScene create running");
    this.add.image(0,0,"BG_1_castle").setOrigin(0,0)
    this.add.image(300,550,"Player").setScale(0.6)

  }
  
  update(){}
}
