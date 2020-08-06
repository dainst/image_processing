<template>
    <section>
        <b-dropdown aria-role="list">
            <button class="button is-primary" slot="trigger" slot-scope="{ active }">
                <span>{{buttonText}}</span>
                <b-icon :icon="active ? 'menu-up' : 'menu-down'"></b-icon>
            </button>
            <div v-for="project of this.projects" :key="project">
                <b-dropdown-item @click="selectProject(project)" aria-role="listitem">
                    {{project}}
                </b-dropdown-item>
            </div>
        </b-dropdown>
    </section>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import backendUri from './config';

export default Vue.extend({
  name: 'ProjectSelection',
  data() {
    return {
      projects: [],
    };
  },
  mounted() {
    axios
      .get(backendUri)
      .then((response) => this.setProjects(response.data));
  },
  computed: {
    buttonText() {
      if (this.$store.state.project !== '') {
        return this.$store.state.project;
      }
      return 'Select project';
    },
  },
  methods: {
    setProjects(projects) {
      this.projects = projects;
    },
    selectProject(project) {
      this.$store.commit('setProject', project);
    },
  },
});
</script>
