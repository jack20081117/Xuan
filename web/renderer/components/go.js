import * as util from './util';
import _ from "lodash";

export default new class{
    getFourDirect(x,y){
        let up={
            x,
            y:y+1
        };
        let down={
            x,
            y:y-1
        };
        let left={
            x:x-1,
            y
        };
        let right={
            x:x+1,
            y
        };
        return {up,down,left,right};
    }

    getSrcString(directs){
        for(let i=0;i<directs.length;i++){
            let s=directs[i];
            if(s>0) return s;
        }
    }

    getStringInfo(x,y,string,board,isBlack){
        //越界 刚才的点在边界
        if(x<0||x>18||y<0||y>18) return -1;
        //目前是黑在下 但这个点返回的是空或者白
        if(board[x][y]!==(isBlack?1:-1)) return false;
        let subString=null;
        subString=(isBlack?string.black:string.white);
        if(subString[x]&&subString[x][y]) return subString[x][y];
        else return true;
    }

    combineCurrentString(x,y,src,isBlack,string,board,directs){
        console.log("combineCurrentString:x,y,src :>> ",x,y,src);
        let subString=null;
        console.log("combineCurrentString string->",string);
        subString=(isBlack?string.black:string.white);
        if(!subString[x]) subString[x]={};
        subString[x][y]=src;
        subString[src].push({x,y});
        for(let i=0;i<directs.length;i++){
            let s=directs[i];
            if(s>0&&su!==src){
                subString[src]=subString[src].concat(subString[s]);
                for(let key in subString) if(key<19)
                    for(let subKey in subString[key])
                        if(subString[key][subKey]===s)
                            subString[key][subKey]=src;
                delete subString[s];
            }
        }
        return string;
    }

    combine(x,y,string,board,isBlack){
        console.log("开始combine");
        let {up,down,left,right}=this.getFourDirect(x,y);
        let su=this.getStringInfo(up.x,up.y,string,board,isBlack);
        let sd=this.getStringInfo(down.x,down.y,string,board,isBlack);
        let sl=this.getStringInfo(left.x,left.y,string,board,isBlack);
        let sr=this.getStringInfo(right.x,right.y,string,board,isBlack);
        if((su===false || su===-1)
        && (sd===false || sd===-1)
        && (sl===false || sl===-1)
        && (sr===false || sr===-1)){
            let stringNum=string.num;
            let subString=(isBlack?string.black:string.white);
            if(!subString[x]) subString[x]={};
            if(!subString[stringNum]) subString[stringNum]=[];
            subString[x][y]=stringNum;
            subString[stringNum].push({x,y});
            string.num++;
        }else{
            let src=this.getSrcString([su,sd,sl,sr])
            console.log("基准棋串为 :>> ",src);
            string=this.combineCurrentString(x,y,src,isBlack,string,board,[su,sd,sl,sr]);
        }
        return string;
    }

    kill(x,y,flag,string,board){
        let {up,down,left,right}=this.getFourDirect(x,y);
        let killed=[];
        directs=[up,down,left,right];
        for(let i=0;i<directs.length;i++){
            let s=directs[i];
            if(s.x>=0&&s.x<19&&s.y>=0&&s.y<19)
                if(board[s.x][s.y]===flag){
                    let res=this.checkKill(s.x,s.y,flag,string,board);
                    if(res!==false) killed.push(res);
                }
        }
        return killed;
    }

    checkKill(x,y,flag,string,board){
        let color=(flag===1?'black':'white');
        let subString=string[color];
        let num=subString[x][y];
        let arr=subString[num];
        console.log("判断这个棋串 num,arr :>> ",num,arr);
        for(let i=0;i<arr.length;i++){
            let x=arr[i].x;
            let y=arr[i].y;
            let {up,down,left,right}=this.getFourDirect(x,y);
            directs=[up,down,left,right];
            for(let i=0;i<directs.length;i++){
                let s=directs[i];
                if(s.x>=0&&s.x<19&&s.y>=0&&s.y<19)
                    if(board[s.x][s.y]===0) return false;
            }
        }
        return num;
    }

    cleanString(num,string,board){
        let color=(string.black[num]?'black':'white');
        console.log("要杀死的棋串为 :>> ",num);
        let subString=string[color];
        let killed=[];
        let arr=subString[num];
        console.log("arr :>> ",arr);
        if(!arr){//避免重复杀棋导致错误
            console.log("num 已被杀死 :>> ");
            return {killed,string,board};
        }
        for(let i=0;i<arr.length;i++){
            let x=arr[i].x;
            let y=arr[i].y;
            delete subString[x][y];
            if(_.isEmpty(subString[x])) delete subString[x];
            board[x][y]=0;
            killed.push({x,y});
        }
        delete subString[num];
        return {killed,string,board};
    }
};