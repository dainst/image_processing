<template>
  <section>
    <img v-bind:src="imageUrl" />
    Name: {{imageName}}
    Distance: {{distance}}
  </section>
</template>

<script>
import Vue from 'vue';
import backendUri from './config';

export default Vue.extend({
  name: 'ComparedImage.vue',
  props: ['imageName', 'distance'],
  data() {
    return {};
  },
  computed: {
    imageUrl() {
      return `${backendUri}/${this.$store.state.project}/${this.$props.imageName}`;
    },
  },
});
</script>
