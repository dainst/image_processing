<style scoped>
.outer_div {
  border-radius: 10px;
  border: 2px solid #7957d5;
  margin-top: 15px;
}
</style>
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
      <div class="column is-half">
        <div class="columns outer_div">
          <div class="column is-half">
            <span v-if="selectedImageData">
              <img :src="selectedImageData" />
              <strong>Main image:</strong>
              {{images[this.selectedImageIndex]}}
            </span>
          </div>
          <div class="column is-half">
            <VoteListItem
              :name="closestNonVotedImage['filename']"
              :vote="closestNonVotedImage['vote']"
              v-on:changeVote="updateVoteForClosestImage($event)"
            />
            <!--   <ComparedImage
              :image-name="closestNonVotedImage['filename']"
              :distance="closestNonVotedImage['distance']"
            />-->
          </div>
        </div>
        <!-- not voted -->
        <VoteList
          type="Without"
          :data="neighoursData"
          direction="row"
          v-on:updateVote="updateVoteForImage($event)"
        />
      </div>
      <!-- negative -->
      <div class="column is-one-quarter">
        <VoteList
          type="Negative"
          :data="neighoursData"
          direction="column"
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
// import ComparedImage from './ComparedImage.vue';
import VoteListItem from './VoteListItem.vue';
import VoteList from './VoteList.vue';

export default Vue.extend({
  name: 'Main.vue',
  components: {
    VoteListItem,
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
    name() {
      return this.$store.state.user;
    },
  },
  watch: {
    project() {
      this.loadImages(this.$store.state.project);
    },
    name() {
      this.loadImages(this.$store.state.project);
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
    updateVoteForClosestImage(event) {
      this.updateVoteForImage(event);
      this.findClosestNonVotedImage();
    },
    updateVoteForImage(event) {
      for (let i = 0; i < this.neighoursData.length; i += 1) {
        const { filename } = this.neighoursData[i];
        if (filename === event.filename) {
          this.neighoursData[i].vote = event.newVote;
          // send post request to server
          axios({
            method: 'post',
            url: `${backendUri}/${this.$store.state.project}/neighbours/${this.images[this.selectedImageIndex]}/vote`,
            data: {
              user: this.$store.state.user,
              vote: event.newVote,
              neighbour_image: filename,
            },
          })
            .then((response) => {
              console.log(response.data);
            })
            .catch((response) => {
              // handle error
              console.log(response);
            });
          break;
        }
      }
    },
  },
});
</script>
