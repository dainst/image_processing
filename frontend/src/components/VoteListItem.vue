<style>

.arrows {
    display: inline-block;
}

.arrow_element {
    border-width: 5px;
    border-style: solid;
    display: inline-block;
}

.neg:hover {
    background-color: darkred;
}

.pos:hover {
    background-color: darkgreen;
}

.arrow {
  border: solid black;
  border-width: 0 3px 3px 0;
  display: inline-block;
  padding: 3px;
}

.right {
  transform: rotate(-45deg);
  -webkit-transform: rotate(-45deg);
}

.left {
  transform: rotate(135deg);
  -webkit-transform: rotate(135deg);
}

</style>

<template>
    <div>
        <img :src="imageUrl(this.name)" />
        <div class="arrows">
            <p
                v-if="vote !== '1'" class="arrow_element pos"
                v-on:click="changeVote('1')">
                <i class="arrow left"></i>
                pos
            </p>
            <p
                v-if="vote !== '-1'" class="arrow_element neg"
                v-on:click="changeVote('-1')">
                <i class="arrow right"></i>
                neg
            </p>
        </div>
    </div>
</template>

<script>
import Vue from 'vue';
import backendUri from './config';

export default Vue.extend({
  name: 'VoteListItem.vue',
  props: ['name', 'vote'],
  data() {
    return {

    };
  },
  methods: {
    changeVote(vote) {
      this.$emit('changeVote', {
        newVote: vote,
        filename: this.name,
      });
    },
    imageUrl(imageName) {
      return `${backendUri}/${this.$store.state.project}/${imageName}`;
    },
  },
});
</script>
