<template>
  <div id="app">
    <link
      rel="stylesheet"
      href="https://cdn.materialdesignicons.com/5.3.45/css/materialdesignicons.min.css"
    />
    <b-navbar>
      <template slot="end">
        <b-navbar-item>
          <ProjectSelection />
        </b-navbar-item>
        <b-navbar-item>
          <NameSelection />
        </b-navbar-item>
      </template>
      <!-- <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>-->
    </b-navbar>
    <!-- <router-view/> -->
    <section v-if="allSet">
      <Main />
    </section>
  </div>
</template>

<script>
import Vue from 'vue';
import Main from './Main.vue';
import NameSelection from './NameSelection.vue';
import ProjectSelection from './ProjectSelection.vue';

export default Vue.extend({
  name: 'App',
  components: {
    NameSelection,
    ProjectSelection,
    Main,
  },
  computed: {
    allSet() {
      return this.$store.state.user !== '' && this.$store.state.project !== '';
    },
  },
});
</script>
