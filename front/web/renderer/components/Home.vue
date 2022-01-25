<template>
    <div>
        <MyMenu></MyMenu>
        <canvas id="go" width="1920" @mousedown="prePlay" height="940"></canvas>
        <Modal
            v-model="modalBoardControl"
            title="检测到用户修改了棋谱"
            @on-ok="boardControlOK"
            @on-cancel="boardControlCancel">
            <p>是否从当前局面继续对局?</p>
        </Modal>
        <Modal
            v-model="modalCheckWinner"
            title="胜负判断"
            @on-ok="setWinnerModal"
            @on-cancel="setWinnerModal">
            <p>黑:{{ this.blackWin }}</p>
            <p>白:{{ this.whiteWin }}</p>
            <p>结果为:{{ this.text }}</p>
        </Modal>
        <MyTool></MyTool>
        <MySet></MySet>
    </div>
</template>

<script>
import _ from "lodash";
import MyMenu from "./Menu.vue";
import MyTool from "./Tool.vue";
import mySet from "./Setup.vue";
import tcp from "./Tcp.vue";
import Bus from "emitvue";
import settings from "electron-settings";
import influence from "@sabaki/influence";
import * as util from "./util.js";
import Go from "./go.js";
import * as constant from './constant.js';
import { systemPreferences } from 'electron';

let sound=document.body.appendChild(document.createElement("span"));
sound.play=function(){
    this.innerHTML="<embed src='play.wav' id='sound'/>";
    document.getElementById("sound").style.display='block';
    document.getElementById("sound").style.display='none';
}

export default {
    components:{
        MyMenu,
        MyTool,
        mySet
    },
    data(){
        return {
            config:null,
            event:null,
            showModal:false,//是否打开修改配置的窗口
            string:util.getEmptyString(),//目前棋盘上的棋串
            boardSize:19,
            robX:null,robY:null,//打劫位置
            siteX:19,siteY:19,//当前步位置
            step:"step",//落子样式
            black:"#000000",white:"#FFFFFF",//棋子颜色
            offsetX:290,offsetY:120,//棋盘偏移量
            isBlack:true,//当前是否为黑棋

            //canvas
            go:null,
            context:null,
            board:(util.getEmptyBoard()),//棋盘 0为空 1为黑棋 -1为白棋
            goban:[],//棋谱 格式:{x,y,color}
            currentNum:-1,//目前手数
            history:[],//历史信息 {board:[],string:[]}
            canvasData:null,
            //锁定落子
            lockedBlack:null,//null:交替;1:黑;-1:白
            modalBoardControl:false,
            showXY:true,
            x:null,y:null,
            modalCheckWinner:false,
            blackWin:0,whiteWin:0,
            text:''
        };
    },
    async created(){
        this.config=await settings.get("setting");
        try{
            JSON.parse(this.config);
            this.config=JSON.parse(this.config);
        }catch(err){
            console.log("this.config或许不是json");
        }
    },
    async mounted(){
        this.go=document.getElementById("go");
        this.context=this.go.getContext("2d");
        this.drawMap();
        this.drawStar();
        this.drawText();
        Bus.$on("newGame",()=>{
            console.log("START :>> ");
        });
        Bus.$on("switchLock",(value)=>{
            this.lockedBlack=value;
        });
        Bus.$on("stepControl",(value)=>{
            this.step=value;
            this.refresh();
            if(this.currentNum===-1){
                console.log("无需绘制落子");
                return;
            }
            let current=this.history[this.currentNum];
            console.log("stepControl current :>> ",current)
            this.switchDrawRadio(current.siteX,current.siteY);
        });
        Bus.$on("analyze",async()=>{
            let data={
                operator:"run",
                board:_.cloneDeep(this.board),
                color:this.isBlack?"black":"white",
                string:_.cloneDeep(this.string),
                goban:_.cloneDeep(this.goban)
            };
            console.log(`ip=${this.config.ip} port=${this.config.port}`);
            let result=await tcp.send(data,this.config.ip,this.config.port);
            console.log("result :>> ",result);
            if(!result){
                this.$Message.error("引擎传输数据格式错误!");
            }
            let probas=result.data;
            let num=Math.ceil(Math.random()*1000000)%9;
            let best=probas[num];
            let x=best.x,y=best.y;
            console.log("引擎选点 :>> ",x,y);
            this.play(x,y);
        });
        Bus.$on("saveGoban",async()=>{
            let data={
                operator:"saveGoban",
                goban:JSON.stringify(this.goban)
            };
            let result=await tcp.send(data,this.config.ip,this.config.port);
            console.log("saveGoban :>> ",result);
            if(!result){
                this.$Message.error("引擎传输数据格式错误!");
            }else{
                this.$Message.info(result.message);
            }
        });
        //判断形式
        Bus.$on("boardAnalyze",()=>{
            this.getInfluence();
        });

        //导入棋谱
        Bus.$on("addSgf",(value)=>{
            this.doSGF(value);
        });

        // 棋盘按钮控制
        Bus.$on('boardControl',(type)=>{
            this.doBoardControl(type)
        });
        Bus.$on('changeShowXY',(value)=>{
            this.showXY=value;
            this.refresh();
        });

        //判断胜负
        Bus.$on('checkWinner',()=>{
            this.checkWinner();
        });
    },
    methods:{
        newGame(){//初始化
            console.log("开始新的一局");
            this.board=util.getEmptyBoard();
            this.string=util.getEmptyString();
            this.robX=null;
            this.robY=null;
            this.isBlack=true;
            this.goban=[];
            this.currentNum=-1;
            this.history=[];
        },
        prePlay(event){
            this.event=event;
            if(this.currentNum===-1&&this.history.length===0){
                this.play();
                return;
            }
            if((this.currentNum!==this.history.length-1)&&(this.currentNum!==-1)&&(this.history.length!==0)){
                this.modalBoardControl=true;
            }else{
                this.play();
            }
        },
        play(out_x,out_y){
            let event=this.event;
            console.log("\n\n\n开始落子...")
            let backupString=_.cloneDeep(this.string);
            let backupBoard=_.cloneDeep(this.board);
            let x=out_x!==undefined?out_x:event.layerX;
            let y=out_y!==undefined?out_y:event.layerY;
            this.isBlack=(this.lockedBlack===null?this.isBlack:this.lockedBlack);
            //引擎选点和玩家选点
            if(out_x===undefined&&out_y===undefined){
                if((x<this.offsetX)||(x>this.offsetX+40*19)
                || (y<this.offsetY)||(y>this.offsetY+40*19)){
                    this.$Message.error("请在棋盘上选择正确的点");
                    return;
                }
                x-=this.offsetX;
                y-=this.offsetY;
                x=Math.round(x/40);
                y=Math.round(y/40);
            }
            if(this.board[x][y]!==0){
                this.$Message.error("无法在已有棋子的位置落子");
                return;
            }
            console.log("落子点为x=",x+1,",y=",y+1);
            this.board[x][y]=this.isBlack?1:-1;
            this.x=x;
            this.y=y;

            Go.combine(x,y,this.string,this.board,this.isBlack);
            let killRes=Go.kill(x,y,this.board[x][y]===1?-1:1,this.string,this.board);
            if(killRes.length>0){
                for(let i=0;i<killRes.length;i++){
                    let backup=Go.cleanString(killRes[i],this.string,this.board);
                    let killed=backup.killed;
                    this.string=backup.string;
                    this.board=backup.board;
                    if(killed.length===1){//杀死一个棋子的话可能是打劫,要判断
                        if(x===this.robX&&y===this.robY){
                            this.$Message.error("无法在打劫点落子");
                            this.string=backupString;
                            this.board=backupBoard;
                            return;
                        }else{//记录打劫点
                            this.robX=killed[0].x;
                            this.robY=killed[0].y;
                            console.log("记录打劫点 x=",this.robX,',y=',this.robY)
                        }
                    }else{
                        this.robX=null;
                        this.robY=null;
                    }
                }
                this.refresh();
            }else{
                let result=Go.checkKill(x,y,this.board[x][y]===1?1:-1,this.string,this.board);
                if(result!==false){
                    this.$Message.error("无法在导致自己死棋的位置落子!");
                    this.string=backupString;
                    this.board=backupBoard;
                    return;
                }
                this.robX=null;
                this.robY=null;
            }
            this.drawChess(x,y);
            this.siteX=x;
            this.siteY=y;
            this.goban.push({x,y,color:this.isBlack?-1:1});
            this.refresh();
            console.log("goban :>> ",this.goban);
            this.currentNum++;
            let historyPush={
                string:_.cloneDeep(this.string),
                board:_.cloneDeep(this.board),
                robX:this.robX,
                robY:this.robY,
                siteX:this.siteX,
                siteY:this.siteY
            }
            this.history.push(historyPush);
            this.switchDrawRadio(x,y);
        },
        refresh(){
            this.drawMap();
            this.drawStar();
            this.drawBoard();
            this.drawText();
            this.switchDrawRadio(this.x,this.y);
        },
        drawMap(){
            this.context.fillStyle="#FFE4C4";
            this.context.fillRect(0,0,1920,940);
            for(let i=0;i<19;i++){//画棋盘的纵横线
                this.context.beginPath();
                this.context.lineWidth=0.3;
                this.context.moveTo(40*i+this.offsetX,0+this.offsetY);
                this.context.lineTo(40*i+this.offsetX,40*18+this.offsetY);
                this.context.closePath();
                this.context.stroke();
            }
            for(let i=0;i<19;i++){//画棋盘的纵横线
                this.context.beginPath();
                this.context.lineWidth=0.3;
                this.context.moveTo(0+this.offsetX,40*i+this.offsetY);
                this.context.lineTo(40*18+this.offsetX,40*i+this.offsetY);
                this.context.closePath();
                this.context.stroke();
            }
        },
        drawSingleStar(x,y){
            this.context.beginPath();
            this.context.fillStyle=this.black;
            this.context.arc(x*40+this.offsetX,y*40+this.offsetY,3,0,2*Math.PI);
            this.context.stroke();
            this.context.closePath();
            this.context.fill();
        },
        drawStar(){
            this.drawSingleStar(3,3);
            this.drawSingleStar(3,15);
            this.drawSingleStar(15,3);
            this.drawSingleStar(15,15);
            this.drawSingleStar(9,9);
            this.drawSingleStar(3,9);
            this.drawSingleStar(9,3);
            this.drawSingleStar(9,15);
            this.drawSingleStar(15,9);
        },
        drawChess(x,y,black){
            let isBlack=this.board[x][y]===1;
            this.context.beginPath();
            if(isBlack===true){
                this.context.fillStyle=this.black;
                this.context.strokeStyle=this.black;
                if(black===undefined) this.isBlack=false;
            }else{
                this.context.fillStyle=this.white;
                this.context.strokeStyle=this.black;
                if(black===undefined) this.isBlack=true;
            }
            this.context.arc(x*40+this.offsetX,y*40+this.offsetY,17,0,2*Math.PI);
            this.context.stroke();
            this.context.closePath();
            this.context.fill();
            sound.play();
        },
        drawText(){
            if(!this.showXY) return;
            this.context.font="26px Arial bolder";
            this.context.fillStyle="black";
            for(let key in constant.drawTextSet){
                let textInfo=constant.drawTextSet[key];
                this.context.fillText(key,textInfo.x1-290,textInfo.y1);
                this.context.fillText(key,textInfo.x2-290,textInfo.y2);
            }
        },
        drawBoard(){
            //遍历 绘制所有的棋子
            for(let i=0; i<19;i++)
                for(let j=0;j<19;j++)
                    if(this.board[i][j]!==0){
                        let black=this.board[i][j]===1;
                        this.drawChess(i,j,black);
                    }
        },
        suicide(x,y){//把这步棋从棋盘上去掉
            let color=(this.board[x][y]===1?"black":"white");
            let subString=this.string[color];
            let num=subString[x][y];
            let arr=subString[num];
            for(let i=0;i<arr.length;i++){
                if(arr[i].x===x&&arr[i].y===y){
                    arr.splice(i,1);
                    break;
                }
            }
            this.board[x][y]=0;
            delete subString[x][y];
        },
        paintNum(){//给棋子标注棋串号
            for(let i=0;i<19;i++)
                for(let j=0;j<19;j++)
                    if(this.board[x][y]!==0){
                        let textColor=(this.board[i][j]===1?this.white:this.black);
                        let color=(this.board[i][j]===1?"black":"white");
                        let subString=this.string[color];
                        let num=subString[i][j];
                        this.context.fillStyle=textColor;
                        this.context.font="20px Arial";
                        this.context.fillText(num.toString(),i*40-10+this.offsetX,j*40+10+this.offsetY);
                    }
        },
        drawSingleStep(i,j,num){
            let offsetText=0;
            num=num||this.goban.length;
            if(num<10) offsetText=5;
            if(num>100) offsetText=-5;
            if(this.board[i][j]!==0){
                let textColor=(this.board[i][j]===1?this.white:this.black);
                this.context.fillStyle=textColor;
                this.context.font="20px Arial";
                this.context.fillText(num.toString(),i*40-10+this.offsetX+offsetText,j*40+10+this.offsetY);
            }
        },
        drawStep(){
            let needDraw={};//需要绘制的列表
            for(let i=0;i<this.goban.length;i++){
                let x=this.goban[i].x;
                let y=this.goban[i].y;
                if(this.board[x][y]!==0){//如果为空说明被吃了
                    if(!needDraw[x]) needDraw[x]={};
                    if(!needDraw[x][y]) needDraw[x][y]={num:i+1};
                    else if(needDraw[x][y].num<i+1) needDraw[x][y]={num:i+1};
                }
            }
            for(let x in needDraw)
                for(let y in needDraw[x]){
                    let info=needDraw[x][y];
                    this.drawSingleStep(x,y,info.num);
                }
        },
        drawCircle(x,y,radius,color){
            this.context.beginPath();
            this.context.fillStyle=color;
            this.context.arc(x*40+this.offsetX,y*40+this.offsetY,radius,0,2*Math.PI);
            this.context.closePath();
            this.context.fill();
        },
        switchDrawRadio(x,y){
            x=x||this.x;
            y=y||this.y;
            switch(this.step){
                case "step":
                    let textColor=(this.board[x][y]===1?this.white:this.black);
                    this.drawCircle(x,y,7,textColor);
                    break;
                case "currentStep":
                    this.drawSingleStep(x,y);
                    break;
                case "hands":
                    this.drawStep();
                    break;
                default:
                    break;
            }
        },
        getInfluence(){
            let result=influence.map(this.board);
            console.log("result :>> ",result)
            for(let i=0;i<19;i++)
                for(let j=0;j<19;j++){
                    let value=result[i][j];
                    if((value===0)||(value===1)||(value===-1)) continue;
                    value=parseFloat(value.toString().slice(0,4));
                    let color=(value>0?"#000000":"#FFFFFF");
                    if(value<0) value=-value;
                    value*=10;
                    this.drawCircle(i,j,value,color);
                }
        },
        sgfLogic(x,y,color){
            this.isBlack=(color==="black");
            this.board[x][y]=this.isBlack?1:-1;
            Go.combine(x,y,this.string,this.board,this.isBlack);
            let killRes=Go.kill(x,y,this.board[x][y]===1?-1:1,this.string,this.board);
            if(killRes.length>0)
                for(let i=0;i<killRes.length;i++)
                    Go.cleanString(killRes[i],this.string,this.board);
        },
        doSGF(sgfData){
            console.log("sgf :>> ",sgfData);
            this.newGame();
            for(let i=0;i<sgfData.length;i++){
                let {x,y,color}=sgfData[i];
                x--;y--;
                this.goban.push({x,y,color:(color==='black'?1:-1)});
                console.log(`目前是第${i}手,x:${x},y:${y},color:${color}`);
                this.sgfLogic(x,y,color);
                let historyPush={
                    string:_.cloneDeep(this.string),
                    board:_.cloneDeep(this.board),
                    robX:this.robX,
                    robY:this.robY,
                    siteX:this.siteX,
                    siteY:this.siteY
                }
                this.history.push(historyPush);
                this.currentNum++;
            }
            console.log("string :>> ",this.string);
            console.log("board :>> ",this.board);
            console.log("goban :>> ",this.goban);
            console.log("currentNum :>> ",this.currentNum);
            this.refresh();
        },
        doBoardControl(type){
            console.log('type :>> ',type);
            switch(type){
                case "begin"://回退到棋局开始
                    if(this.currentNum===-1){
                        this.$Message.warning("已经到最开始的位置");
                        return;
                    }
                    this.currentNum=-1;
                    break;
                case "fiveback"://回退5步
                    if(this.currentNum===-1){
                        this.$Message.warning("已经到最开始的位置");
                        return;
                    }
                    this.currentNum-=5;
                    break;
                case "back"://回退1步(悔棋)
                    if(this.currentNum===-1){
                        this.$Message.warning("已经到最开始的位置");
                        return;
                    }
                    this.currentNum--;
                    break;
                case "step"://前进1步
                    if(this.currentNum===this.history.length-1){
                        this.$Message.warning("已经到最末尾的位置");
                        return;
                    }
                    this.currentNum++;
                    break;
                case "fivestep"://前进5步
                    if(this.currentNum===this.history.length-1){
                        this.$Message.warning("已经到最末尾的位置");
                        return;
                    }
                    this.currentNum+=5;
                    break;
                case "end"://前进到最近一步
                    if(this.currentNum===this.history.length-1){
                        this.$Message.warning("已经到最末尾的位置");
                        return;
                    }
                    this.currentNum=this.history.length-1;
                    break;
            }
            this.currentNum=Math.max(this.currentNum,-1);
            this.currentNum=Math.min(this.currentNum,this.history.length-1);
            console.log("currentNum :>> ",this.currentNum);
            this.updateBoardData();
            console.log("string :>> ",this.string);
            console.log("board :>> ",this.board);
            this.refresh();
            if(this.currentNum===-1) return;
            this.switchDrawRadio(this.siteX,this.siteY);
        },
        updateBoardData(){
            console.log("history[currentNum]",this.history[this.currentNum]);
            if(this.currentNum===-1){
                this.board=util.getEmptyBoard();
                this.string=util.getEmptyString();
                this.robX=null;
                this.robY=null;
                this.siteX=null;
                this.siteY=null;
            }else{
                console.log("history :>> ",this.history);
                this.string=this.history[this.currentNum].string;
                this.board=this.history[this.currentNum].board;
                this.robX=this.history[this.currentNum].robX;
                this.robY=this.history[this.currentNum].robY;
                this.siteX=this.history[this.currentNum].siteX;
                this.siteY=this.history[this.currentNum].siteY;
            }
        },
        boardControlOk(){
            //截断历史
            if (this.currentNum!==-1) {
                this.history=this.history.slice(0,this.currentNum)
                this.currentNum--;
            }else this.history=[];
            this.play();
            this.$Message.success('已修改历史棋谱');
        },
        boardControlCancel(){
            this.$Message.info('取消修改棋谱');
        },
        checkWinner(){
            let res=influence.areaMap(this.board);
            console.log("res :>> ,res");
            let black=0,white=0;
            for(let i=0;i<19;i++)
                for(let j=0;j<19;j++){
                    if(res[i][j]===1) black++;
                    if(res[i][j]===-1) white++;
                }
            let text=(black>white+6.5)?"黑胜":"白胜";
            console.log("black :>> ",black);
            console.log("white :>> ",white);
            this.blackWin=black;
            this.whiteWin=white;
            this.text=text;
            this.modalCheckWinner=true;
            console.log("modalCheckWinner :>> ",this.modalCheckWinner);
        },
        setWinnerModal(){
            this.modalCheckWinner=!this.modalCheckWinner;
        }
    }
};
</script>