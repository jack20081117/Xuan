'use strict';

process.env.NODE_ENV='production';

const {say}=require('cfonts');
const chalk=require('chalk');
const del=require('del');
const {spawn}=require('child_process');
const webpack=require('webpack');
const listr=require('listr');

const mainConfig=require('./webpack.main.config');
const rendererConfig=require('./webpack.renderer.config');
const webConfig=require('./webpack.web.config');

const doneLog=chalk.bgGreen.white(' DONE ')+' ';
const errorLog=chalk.bgRed.white(' ERROR ')+' ';
const okayLog=chalk.bgBlue.white(' OKAY ')+' ';

const isCI=process.env.CI||false;

function clean(){
    del.sync(['build/*'])
}