<template>
</template>

<script>
import net from "net";
import { resolve } from 'url';

export default {
    //发送数据
    async send(json,ip,port){
        console.log("send data...waiting,json->",json);
        return new Promise((resolve,reject)=>{
            let client=new net.Socket();
            client.connect({
                host:ip,
                port:port
            });

            //客户端与服务器建立连接触发
            client.on('connect',()=>{
                client.write(JSON.stringify(json));
            });

            //客户端接收数据触发
            client.on('data',(data)=>{
                client.end();
                resolve(this.safeJSONParse(data.toString()));
            });

            //客户端错误触发
            client.on('error',(error)=>{
                reject(error);
            });
        });
    },
    safeJSONParse(data){
        try{
            return JSON.parse(data);
        }catch(err){
            console.log("data :>> ",data);
            return null;
        }
    }
};
</script>