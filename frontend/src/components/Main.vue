<template>
    <section>
        <nav class="pagination is-centered" role="navigation" aria-label="pagination">
            <ul class="pagination-list">
                <a class="pagination-link" @click="previousImage">Previous</a>
                <a class="pagination-link" @click="nextImage">Next</a>
            </ul>
        </nav>
        <div class="columns">
          <!-- positive -->
          <div class="column is-one-quarter">
            <VoteList
              type="Positive"
              :data="neighoursData"
              direction="column"
              v-on:updateVote="updateVoteForImage($event)"
            />
          </div>
          <!-- main middle -->
          <div class="column">
            <div class="columns">
              <div class="column is-half">
                <span v-if="selectedImageData">Main image:</span>
                 <img :src="selectedImageData"/>
              </div>
              <div class="column is-half">
                <ComparedImage
                  :image-name="closestNonVotedImage['filename']"
                  :distance="closestNonVotedImage['distance']"
                />
              </div>
            </div>
            <!-- not voted -->
              <VoteList
                type="Without"
                :data="neighoursData"
                direction='row'
                v-on:updateVote="updateVoteForImage($event)"
              />
          </div>
          <!-- negativ -->
          <div class="column is-one-quarter">
            <VoteList
              type="Negative"
              :data="neighoursData"
              direction='column'
              v-on:updateVote="updateVoteForImage($event)"
            />
          </div>
        </div>
    </section>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import backendUri from './config';
import ComparedImage from './ComparedImage.vue';
import VoteList from './VoteList.vue';

export default Vue.extend({
  name: 'Main.vue',
  components: {
    ComparedImage,
    VoteList,
  },
  data() {
    return {
      images: [],
      neighoursData: [],
      selectedImageIndex: 0,
      selectedImageData: null,
      closestNonVotedImage: null,
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
      this.neighoursData = null;
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
        .get(`${backendUri}/${this.$store.state.project}/neighbours/${selectedImageName}/${this.$store.state.user}`)
        .then((response) => response.data);
      this.selectedImageData = `${backendUri}/${this.$store.state.project}/${selectedImageName}`;
      this.findClosestNonVotedImage();
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
    findClosestNonVotedImage() {
      for (let i = 0; i < this.neighoursData.length; i += 1) {
        const { vote } = this.neighoursData[i];
        if (vote === '0') {
          this.closestNonVotedImage = this.neighoursData[i];
          break;
        }
      }
    },
    updateVoteForImage(event) {
      for (let i = 0; i < this.neighoursData.length; i += 1) {
        const { filename } = this.neighoursData[i];
        if (filename === event.filename) {
          this.neighoursData[i].vote = event.newVote;
          break;
        }
      }
    },
  },
});
</script>
