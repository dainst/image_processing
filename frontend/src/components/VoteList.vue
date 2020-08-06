<style scoped>
.outer_div {
  border-radius: 15px;
  border: 4px solid darkgreen;
}

</style>

<template>
    <section class="outer_div">
        <h1>{{ type }} votes</h1>
        <div v-if="direction === 'row'">
          <div style="overflow: auto;">
            <div class="columns">
              <div v-for="item of this.data" :key="item" class="column is-one-quarter">
                <VoteListItem
                  v-if="checkRender(item.vote)"
                  v-bind:name="item.filename"
                  v-on:changeVote="updateVote($event)"
                  :vote="item.vote"
                />
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="direction === 'column'">
          <div v-for="item of this.data" :key="item">
            <VoteListItem
              v-if="checkRender(item.vote)"
              v-bind:name="item.filename"
              v-on:changeVote="updateVote($event)"
              :vote="item.vote"
            />
          </div>
        </div>
    </section>
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
    checkRender(vote) {
      let retValue;
      if (this.type === 'Positive') {
        if (vote === '1') retValue = true;
        else retValue = false;
      } else if (this.type === 'Negative') {
        if (vote === '-1') retValue = true;
        else retValue = false;
      } else if (this.type === 'Without') {
        if (vote === '0') retValue = true;
        else retValue = false;
      }
      return retValue;
    },
    updateVote(event) {
      this.$emit('updateVote', event);
    },
  },
});
</script>
