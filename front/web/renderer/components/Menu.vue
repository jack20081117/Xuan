<template>
    <div></div>
</template>

<script>
import Bus from "emitvue";
import { Accelerator } from 'electron';
let remote=require("electron").remote;
let Menu=remote.Menu;

export default {
    data(){
        return {
            blackLocked:false,
            whiteLocked:false,
            switchLocked:true,
            lockStatus:0 //0:交替;1:下黑子;-1:下白子
        };
    },
    methods:{
        switchLock(type){
            console.log('type,lockStatus :>> ',type,this.lockStatus)
            switch(type){
                case null:
                    if(this.lockStatus===0) return;
                    else{
                        this.lockStatus=0;
                        this.blackLocked=false;
                        this.whiteLocked=false;
                        this.switchLocked=true;
                        Bus.$emit('switchLock',null);
                        this.$Message.info("切换为交替落子");
                    }
                    break;
                case true:
                    if(this.lockStatus===1) return;
                    else{
                        this.lockStatus=1;
                        this.blackLocked=true;
                        this.whiteLocked=false;
                        this.switchLocked=false;
                        Bus.$emit('switchLock',true);
                        this.$Message.info("切换为落黑子");
                    }
                    break;
                case false:
                    if(this.lockStatus===-1) return;
                    else{
                        this.lockStatus=-1;
                        this.blackLocked=false;
                        this.whiteLocked=true;
                        this.switchLocked=false;
                        Bus.$emit('switchLock',false);
                        this.$Message.info("切换为落白子")
                    }
                    break;
                default:
                    break;
            }
            if((this.switchLocked===false)&&(this.blackLocked===false)&&(this.whiteLocked===false))
                this.switchLocked=true;
            this.createMenu();
        },
        createMenu(){
            let template=[
                {
                    label:"菜单",
                    submenu:[
                        {
                            label:"新的一局",
                            accelerator:'shift+N',
                            click:()=>{
                                Bus.$emit("newGame");
                            }
                        }
                    ]
                },
                {
                    label:"工具",
                    submenu:[
                        {
                            label:"落子控制",
                            submenu:[
                                {
                                    label:"交替落子",
                                    type:"checkbox",
                                    click:()=>{
                                        this.switchLock(null);
                                    },
                                    checked:this.switchLocked,
                                    accelerator:'shift+1'
                                },
                                {
                                    label:"落黑子",
                                    type:"checkbox",
                                    click:()=>{
                                        this.switchLock(true);
                                    },
                                    checked:this.blackLocked,
                                    accelerator:'shift+2'
                                },
                                {
                                    label:"落白子",
                                    type:"checkbox",
                                    click:()=>{
                                        this.switchLock(false);
                                    },
                                    checked:this.whiteLocked,
                                    accelerator:'shift+3'
                                }
                            ]
                        },
                        {
                            label:"形式判断",
                            accelerator:'alt+shift+3',
                            click:()=>{
                                this.checkInfluence();
                            }
                        }
                    ]
                }
            ];
            var menu=Menu.buildFromTemplate(template);
            Menu.setApplicationMenu(menu);
        },
        checkInfluence(){
            console.log('11 :>> ',11);
        }
    },
    mounted(){
        this.createMenu();
    }
};
</script>

<style>
</style>