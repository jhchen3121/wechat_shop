import Vue from 'vue'
import Axios from 'axios'
import VueAxios from 'vue-axios'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import App from './App'
import router from './router'
import store from './store'
import api from './config/api'
// vue-quill-edit
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

// element-ui 跟 bootstrap css 有冲突
// import 'bootstrap/js/modal.js'
// import 'bootstrap/js/dropdown.js'
// import 'bootstrap/js/tooltip.js'
// // import 'bootstrap/dist/css/bootstrap.css'
// import 'font-awesome/css/font-awesome.css'
// import 'summernote'
// import 'summernote/dist/lang/summernote-zh-CN.js'
// import 'summernote/dist/summernote.css'

Vue.use(VueAxios, Axios);
Vue.use(ElementUI);

// add设置调试模式
Vue.config.devtools = true;
 // Vue.config.devtools = __ENV__.NODE_ENV !== 'production';

router.beforeEach((to, from, next) => {

	let token = sessionStorage.getItem('token') || '';

    //配置接口信息
    // Axios.defaults.baseURL = 'http://www.地址.com:8360/admin/';
    // Axios.defaults.baseURL = api.rootUrl;
    // 避免请求重复拼接
    Axios.defaults.baseURL = '';
    Axios.defaults.headers.common['x-session-token'] = token;

	if (!token && to.name !== 'login') {
		next({
			path: '/login',
			query: { redirect: to.fullPath }
		})
	} else {
		next()
	}
});

if (!process.env.IS_WEB) {
  Vue.use(require('vue-electron'))
}
Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app')
