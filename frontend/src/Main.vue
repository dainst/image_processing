<template>
    <section>
        <div class="columns">
            <div class="column is-half">
                Main image
                <img :src="selectedImageData"/>
            </div>
            <div class="column is-half" v-if="neighoursData.length > 0">
                <ComparedImage
                    :image-name="neighoursData[0][0]"
                    :distance="neighoursData[0][1]"
                />
            </div>
        </div>
        <div class="columns">
            <div class="tile is-parent is-12">
                <div class="tile is-child" v-if="neighoursData.length > 0">
                    <ComparedImage
                        :image-name="neighoursData[1][0]"
                        :distance="neighoursData[1][1]"
                    />
                </div>
                <div class="tile is-child" v-if="neighoursData.length > 0">
                    <ComparedImage
                        :image-name="neighoursData[2][0]"
                        :distance="neighoursData[2][1]"
                    />
                </div>
                <div class="tile is-child" v-if="neighoursData.length > 0">
                    <ComparedImage
                        :image-name="neighoursData[2][0]"
                        :distance="neighoursData[2][1]"
                    />
                </div>
            </div>
        </div>
    </section>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import backendUri from './config';
import ComparedImage from './ComparedImage.vue';

export default Vue.extend({
  name: 'Main.vue',
  components: {
    ComparedImage,
  },
  data() {
    return {
      images: [],
      neighoursData: [],
      selectedImageIndex: 0,
      selectedImageData: null,
    };
  },
  mounted() {
    this.loadImages(this.$store.state.project);
  },
  computed: {
    project() {
      return this.$store.state.project;
    },
  },
  watch: {
    project(name) {
      this.loadImages(name);
    },
  },
  methods: {
    async loadImages(project) {
      this.images = [];
      this.neighoursData = [];
      if (project === '') {
        return;
      }

      this.images = await axios
        .get(`${backendUri}/${project}`)
        .then((response) => response.data);

      const selectedImageName = this.images[this.selectedImageIndex];
      this.neighoursData = await axios
        .get(`${backendUri}/${project}/neighbours/${selectedImageName}`)
        .then((response) => response.data);
      this.selectedImageData = `${backendUri}/${project}/${selectedImageName}`;
    },
  },
});
</script>

<style>
    .primaryImage {
        max-height: 500px;
    }
</style>
