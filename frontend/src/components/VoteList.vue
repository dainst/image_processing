<style scoped>
.outer_div {
  border-radius: 10px;
  border: 2px solid #7957d5;
  padding: 10px;
  width: 100%;
}

.item_container {
  display: flex;
  overflow: auto;
  width: 100%;
}

.ic_row {
  flex-direction: row;
}

.item_div {
  flex-wrap: wrap;
}

h1 {
  font-weight: bold;
  color: #7957d5;
}

.test {
  height: 30%;
  overflow: auto;
  display: flex;
}
.column_container {
  max-height: 1000px;
  overflow: auto;
}
</style>

<template>
  <div class="outer_div">
    <h1>{{ type }} votes</h1>
    <div v-if="direction === 'row'" class="item_container">
      <div v-for="item of this.data" :key="item" class="item_div">
        <VoteListItem
          v-if="checkRender(item.vote, item.filename)"
          v-bind:name="item.filename"
          v-on:changeVote="updateVote($event)"
          :vote="item.vote"
        />
      </div>
    </div>
    <div v-else-if="direction === 'column'" class="column_container">
      <div v-for="item of this.data" :key="item">
        <VoteListItem
          v-if="checkRender(item.vote)"
          v-bind:name="item.filename"
          v-on:changeVote="updateVote($event)"
          :vote="item.vote"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import VoteListItem from './VoteListItem.vue';

export default Vue.extend({
  name: 'VoteList.vue',
  components: {
    VoteListItem,
  },
  props: ['type', 'data', 'direction'],
  data() {
    return {};
  },
  methods: {
    checkRender(vote, filename) {
      let retValue;
      if (this.type === 'Positive') {
        if (vote === '1') retValue = true;
        else retValue = false;
      } else if (this.type === 'Negative') {
        if (vote === '-1') retValue = true;
        else retValue = false;
      } else if (this.type === 'Without') {
        if (
          vote === '0'
          && this.$parent.closestNonVotedImage.filename !== filename
        ) { retValue = true; } else retValue = false;
      }
      return retValue;
    },
    updateVote(event) {
      this.$emit('updateVote', event);
    },
  },
});
</script>
