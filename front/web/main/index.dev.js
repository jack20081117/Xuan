// Install `electron-debug` with `devtron`
require('electron-debug')({showDevTools:true});

require('electron').app.on('ready',()=>{
    let installExtension=require('electron-devtools-installer');
    installExtension.default(installExtension.VUEJS_DEVTOOLS).then(()=>{}).catch(err=>console.log('Unable to install `vue-devtools`: \n',err));
});

require('./index')