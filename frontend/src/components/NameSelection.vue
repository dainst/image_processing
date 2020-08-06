<template>
  <b-field>
    <b-input v-model="name" placeholder="Please enter your name" icon="account"></b-input>
    <p class="control">
      <button class="button is-primary" v-bind:disabled="isButtonDisabled" v-on:click="updateName">
        Ok
      </button>
    </p>
  </b-field>
</template>

<script>
import Vue from 'vue';

export default Vue.extend({
  name: 'NameSelection.vue',
  data() {
    return {
      name: this.$store.state.user,
    };
  },
  computed: {
    isButtonDisabled() {
      return (this.name === '' || this.name === this.$store.state.user);
    },
  },
  methods: {
    updateName() {
      this.$store.commit('setUser', this.name);
    },
  },
});
</script>
