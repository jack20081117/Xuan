<template>
    <div>
        <Modal
            v-model="modalSetup"
            title="Xuan配置中心"
            @on-ok="ok"
            @on-cancel="cancel">
            <p>引擎连接方式</p>
            <RadioGroup v-model="connectType">
                <Radio label="网络连接"></Radio>
                <Radio label="命令行" disabled></Radio>
            </RadioGroup>
            <Tabs value="connect">
                <TabPane label="网络连接" name="connect">
                    <p>IP地址</p>
                    <Input v-model="ip"/>
                    <p>端口</p>
                    <Input v-model="port"/>
                </TabPane>
                <TabPane label="命令行" name="command"></TabPane>
            </Tabs>
        </Modal>
    </div>
</template>

<script>
import settings from "electron-settings";
import bus from "emitvue";
import _ from "lodash";

export default {
    data(){
        return {
            modelSetup:false,
            connectType:"网络连接",
            ip:0,
            port:0,
            defaultSet:{
                ip:'127.0.0.1',
                port:7075
            },
            setting:null
        };
    },
    methods:{
        async getSet(){
            this.setting=await settings.get("setting");
            console.log("setting :>> ",this.setting);
            if(!this.setting||_.isEmpty(this.setting)){
                this.setting=this.defaultSet;
                await set.set("setting",this.setting);
            }
            try{
                this.setting=JSON.parse(this.setting);
            }catch(err){
                this.setting=this.defaultSet;
                await set.set("setting",this.setting);
            }
            this.ip=this.setting.ip;
            this.port=this.setting.port;
        },
        async ok(){
            this.setting.ip=this.ip;
            this.setting.port=this.port;
            await set.set("setting",JSON.stringify(this.setting));
            this.$Message.info("保存配置成功");
        },
        cancel(){
            this.$Message.info("取消保存配置");
        },
    },
    mounted(){//收到消息就弹窗
        bus.$on("setup",()=>{
            this.modelSetup=true;
        });
    },
    async created(){
        await this.getSet();
    }
};
</script>

<style>
</style>