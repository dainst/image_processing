<template>
    <section>
        <nav class="pagination is-centered" role="navigation" aria-label="pagination">
            <ul class="pagination-list">
                <a class="pagination-link" @click="previousImage">Previous</a>
                <a class="pagination-link" @click="nextImage">Next</a>
            </ul>
        </nav>
        <div class="columns">
            <div class="column">
                <span v-if="selectedImageData">Main image:</span>
                <img :src="selectedImageData"/>
            </div>
            <div class="column" v-if="neighoursData.length > 0">
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
    project() {
      this.loadImages();
    },
  },
  methods: {
    async loadImages() {
      this.images = [];
      this.neighoursData = [];
      if (this.$store.state.project === '') {
        return;
      }

      this.images = await axios
        .get(`${backendUri}/${this.$store.state.project}`)
        .then((response) => response.data);

      this.updateDisplayedImages();
    },
    async updateDisplayedImages() {
      const selectedImageName = this.images[this.selectedImageIndex];
      this.neighoursData = await axios
        .get(`${backendUri}/${this.$store.state.project}/neighbours/${selectedImageName}`)
        .then((response) => response.data);
      this.selectedImageData = `${backendUri}/${this.$store.state.project}/${selectedImageName}`;
    },
    previousImage() {
      this.selectedImageIndex -= 1;
      if (this.selectedImageIndex < 0) this.selectedImageIndex = 0;
      this.updateDisplayedImages();
    },
    nextImage() {
      this.selectedImageIndex += 1;
      if (this.selectedImageIndex >= this.images.length) {
        this.selectedImageIndex = this.images.length - 1;
      }
      this.updateDisplayedImages();
    },

  },
});
</script>
