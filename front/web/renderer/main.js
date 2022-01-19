import Vue from "vue";
import axios from "axios";

import App from './App.vue';
import router from './router';
import store from './store';
import ViewUI from 'view-design';
import 'view-design/dist/styles/iview.css';

if(!process.env.IS_WEB) Vue.use(require('vue-electron'));
Vue.http=Vue.prototype.$http=axios;
Vue.config.productionTip=false;
Vue.use(ViewUI);

new Vue({
    components:{App},
    router,
    store,
    template:'<App/>'
}).$mount('#app');