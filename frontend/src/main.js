import Buefy from 'buefy';
import 'buefy/dist/buefy.css';
import Vue from 'vue';
import Vuex from 'vuex';
import App from './components/App.vue';
import router from './router';

Vue.config.productionTip = false;
Vue.use(Vuex);
Vue.use(Buefy, {
  defaultIconPack: 'mdi',
  defaultContainerElement: '#content',
});

const store = new Vuex.Store({
  state: {
    user: '',
    project: '',
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    setProject(state, project) {
      state.project = project;
    },
  },
});

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app');
