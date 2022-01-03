<template>
    <div>
        <Tooltip content="导入sgf文本或sgf文件棋谱">
            <Button type="info" shape="circle" @click="sgfModal=true;sgfText='';">导入棋谱</Button>
        </Tooltip>
        <RadioGroup v-model="hint" @on-change="stepControl()">
            <Tooltip content="绘制每次落子点">
                <Radio label="step">
                    <Icon type="ios-funnel"/>
                    <span>落子提醒</span>
                </Radio>
            </Tooltip>
            <Tooltip content="绘制每次落子的手数">
                <Radio label="currentStep">
                    <Icon type="md-hand"/>
                    <span>当前手数</span>
                </Radio>
            </Tooltip>
            <Tooltip content="绘制全部手数">
                <Radio label="hands">
                    <Icon type="ios-hand"/>
                    <span>全部手数</span>
                </Radio>
            </Tooltip>
            <Tooltip content="显示坐标">
                <Checkbox v-model="showXY" @on-change="changeShowXY()">显示坐标</Checkbox>
            </Tooltip>
        </RadioGroup>

        <Tooltip content="回退到棋局开始">
            <Button type="primary" shape="circle" @click="boardControl('begin')">{{ begin }}</Button>
        </Tooltip>
        <Tooltip content="回退5步">
            <Button type="primary" shape="circle" @click="boardControl('fiveback')">{{ fiveback }}</Button>
        </Tooltip>
        <Tooltip content="回退1步（悔棋）">
            <Button type="primary" shape="circle" @click="boardControl('back')">{{ back }}</Button>
        </Tooltip>
        <Tooltip content="前进1步">
            <Button type="primary" shape="circle" @click="boardControl('step')">{{ step }}</Button>
        </Tooltip>
        <Tooltip content="前进5步">
            <Button type="primary" shape="circle" @click="boardControl('fivestep')">{{ fivestep }}</Button>
        </Tooltip>
        <Tooltip content="前进到最近一步">
            <Button type="primary" shape="circle" @click="boardControl('end')">{{ end }}</Button>
        </Tooltip>
        <Tooltip content="将当前局面交由Xuan进行分析">
            <Button type="primary" shape="circle" @click="analyze()">引擎分析</Button>
        </Tooltip>
        <Tooltip content="编辑软件配置">
            <Button type="info" shape="circle" @click="setup()">修改配置</Button>
        </Tooltip>
        <Tooltip content="暂时废弃">
            <Button type="success" shape="circle" disabled @click="saveGoban()">保存对局信息</Button>
        </Tooltip>
        <Tooltip content="进行形式判断">
            <Button type="info" shape="circle" @click="boardAnalyze()">形式判断</Button>
        </Tooltip>
        <Tooltip content="胜负判断">
            <Button type="info" shape="circle" @click="checkWinner()">胜负判断</Button>
        </Tooltip>

        <Modal
            v-model="sgfModal"
            title="导入棋谱"
            @on-ok="ok"
            @on-cancel="cancel">
            <Tabs value="sgfText">
                <TabPane label="导入sgf文本" name="sgfText">
                    <Input v-model="sgfText" type="textarea" :rows="4" placeholder="在此处粘贴SGF"/>
                </TabPane>
                <TabPane label="导入sgf棋谱文件" name="sgfFile" disabled="">
                </TabPane>
            </Tabs>
        </Modal>
    </div>
</template>

<script>
import Bus from "emitvue";
import * as util from './util';

export default {
    data(){
        return {
            hint:"step",
            /*step:当前落子
             *currentStep:当前手数
             *hands:所有手数
             */
            begin:"|<",
            end:">|",
            step:">",
            back:"<",
            fivestep:">>",
            fiveback:"<<",
            sgfModal:false,
            sgfText:'',
            showXY:true
        }
    },
    methods:{
        stepControl(){
            Bus.$emit("stepControl",this.hint);
        },
        analyze(){
            Bus.$emit("analyze",null);
        },
        setup(){
            Bus.$emit("setup",null);
        },
        saveGoban(){
            Bus.$emit("saveGoban",null);
        },
        //局面分析
        boardAnalyze(){
            Bus.$emit("boardAnalyze",null);
        },
        boardControl(value){
            Bus.$emit("boardControl",value);
        },
        checkWinner(){
            Bus.$emit("checkWinner",null);
        },
        //点击ok导入棋谱
        ok(){
            if (this.sgfText===''){
                this.$Message.warning("检测到棋谱为空，取消导入");
                return;
            }
            let res=util.parseSgf(this.sgfText)
            Bus.$emit("addSgf",res);
            this.$Message.info('导入成功');
        },
        cancel(){
            this.$Message.info('取消导入');
        },
        changeShowXY(){
             Bus.$emit("changeShowXY",this.showXY);
        }
    },
    created(){
    }
};
</script>

<style>
</style>