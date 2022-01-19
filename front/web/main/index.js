import {app,BrowserWindow,globalShortcut} from 'electron';
import setting from 'electron-settings';
import localshortcut from 'electron-localshortcut';
import * as os from 'os';

if(process.env.NODE_ENV!=='development'){
    global.__static=require('path').join(__dirname,'/static').replace(/\\/g,'\\\\');
}

async function getConfig(){
    let config=await setting.get('config');
    console.log('config :>>',config);
    global.config=config
}

getConfig();

let mainWindow;
const winURL=process.env.NODE_ENV==='development'?`http://localhost:9080`:`file://${__dirname}/index.html`;

function createWindow(){
    mainWindow=new BrowserWindow({
        height:1080,
        useContentSize:true,
        width:1920,
        webPreferences:{
            nodeIntegration:true,
        }
    });

    mainWindow.loadURL(winURL);

    mainWindow.on('closed',()=>{
        mainWindow=null;
    });

    globalShortcut.register('alt+shift+x',function(){mainWindow.webContents.openDevTools()});
}

app.on('ready',createWindow);

app.on('window-all-closed',()=>{
    if(process.platform!=='darwin'){
        app.quit();
    }
});

app.on('activate',()=>{
    if (mainWindow===null){
      if(os.platform()==='darwin'){
        localshortcut.register(`command+v`,function(){
          mainWindow.webContents.paste();
        });
        localshortcut.register(`command+c`,function(){
          mainWindow.webContents.copy();
        });
        localshortcut.register(`command+x`,function(){
          mainWindow.webContents.cut();
        })
      }
      createWindow();
    }
  })