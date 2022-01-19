'use strict';

process.env.BABEL_ENV='renderer';

const path=require('path');
const {dependencies}=require('../../package.json');
const webpack=require('webpack');

const MinifyPlugin=require('babel-minify-webpack-plugin');
const CopyWebpackPlugin=require('copy-webpack-plugin');
const MiniCssExtractPlugin=require('mini-css-extract-plugin');
const HTMLWebpackPlugin=require('html-webpack-plugin');
const {VueLoaderPlugin}=require('vue-loader');

let whiteListedModules=['vue'];

let rendererConfig={
    devtool:'#cheap-module-eval-source-map',
    entry:{
        renderer:path.join(__dirname,'../web/renderer/main.js')
    },
    externals:[
        ...Object.keys(dependencies||{}).filter(d=>!whiteListedModules.includes(d))
    ],
    module:{
        rules:[
            {
                test:/\.scss$/,
                use:['vue-style-loader','css-loader','sass-loader']
            },
            {
                test:/\.sass$/,
                use:['vue-style-loader','css-loader','sass-loader?indentedSyntax']
            },
            {
                test:/\.less$/,
                use:['vue-style-loader','css-loader','less-loader'],
            },
            {
                test:/\.css$/,
                use:['vue-style-loader','css-loader']
            },
            {
                test:/\.html$/,
                use:'vue-html-loader'
            },
            {
                test:/\.js$/,
                use:'babel-loader',
                exclude:/node_modules/
            },
            {
                test:/\.node$/,
                use:'node-loader'
            },
            {
                test:/\.vue$/,
                use:{
                    loader:'vue-loader',
                    options:{
                        extractCSS:process.env.NODE_ENV==='production',
                        loaders:{
                            sass:'vue-style-loader!css-loader!sass-loader?indentedSyntax=1',
                            scss:'vue-style-loader!css-loader!sass-loader',
                            less:'vue-style-loader!css-loader!less-loader'
                        }
                    }
                }
            },
            {
                test:/\.(png|jpe?g|gif|svg)(\?.*)?$/,//图片格式
                use:{
                    loader:'url-loader',
                    query:{
                        limit:10000,
                        name:'imgs/[name]--[folder].[ext]'
                    }
                }
            },
            {
                test:/\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,//音频,视频文件形式
                loader:'url-loader',
                options:{
                    limit:10000,
                    name:'media/[name]--[folder].[ext]'
                }
            },
            {
                test:/\.(woff2?|eot|ttf|otf)(\?.*)?$/,
                use:{
                    loader:'url-loader',
                    query:{
                        limit:10000,
                        name:'fonts/[name]--[folder].[ext]'
                    }
                }
            }
        ]
    },
    node:{
        __dirname:process.env.NODE_ENV!=='production',
        __filename:process.env.NODE_ENV!=='production'
    },
    output:{
        filename:'[name].js',
        libraryTarget:'commonjs2',
        path:path.join(__dirname,'../dist/electron')
    },
    plugins:[
        new VueLoaderPlugin(),
        new MiniCssExtractPlugin({filename:'styles.css'}),
        new HTMLWebpackPlugin({
            filename:'index.html',
            template:path.resolve(__dirname,'../web/index.ejs'),
            templateParameters(compilation,assets,options){
                return {
                    compilation:compilation,
                    webpack:compilation.getStats().toJson(),
                    webpackConfig:compilation.options,
                    htmlWebpackPlugin:{
                        files:assets,
                        options:options
                    },
                    process
                };
            },
            minify:{
                collapseWhitespace:true,
                removeAttributeQuotes:true,
                removeComments:true
            },
            nodeModules:((process.env.NODE_ENV!=='production')?path.resolve(__dirname,'../node_modules'):false)
        }),
        new webpack.NoEmitOnErrorsPlugin()
    ],
    resolve:{
        alias:{
            '@':path.join(__dirname,'../web/renderer'),
            'vue$':'vue/dist/vue.esm.js'
        },
        extensions:['.js','vue','.json','.css','.node']
    },
    target:'electron-renderer'
};

if(process.env.NODE_ENV!=='production')
    rendererConfig.plugins.push(
        new webpack.HotModuleReplacementPlugin(),
        new webpack.DefinePlugin({
        '__static':`"${path.join(__dirname,'../static').replace(/\\/g,'\\\\')}"`
        }
    ));

if(process.env.NODE_ENV==='production'){
    rendererConfig.devtool='';
    rendererConfig.plugins.push(
        new MinifyPlugin(),
        new CopyWebpackPlugin([{
            from:path.join(__dirname,'../static'),
            to:path.join(__dirname,'../dist/electron/static'),
            ignore:['.*']
        }]),
        new webpack.DefinePlugin({
            'process.env.NODE_ENV':'"production"'
        }),
        new webpack.LoaderOptionsPlugin({
            minimize:true
        })
    );
}

module.exports=rendererConfig;