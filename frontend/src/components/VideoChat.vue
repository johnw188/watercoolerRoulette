<template>
  <div>
    <span title="localVideo">
      <video alt="local" bind:this="{local}" ref="local" autoplay muted></video>
    </span>
    <span title="remoteVideo">
      <video alt="remote" bind:this="{remote}" ref="remote" autoplay></video>
    </span>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import ChatInteraction from '../lib/ChatInteraction';

export default class VideoChat extends Vue {
  $refs!: {
    local: HTMLMediaElement;
    remote: HTMLMediaElement;
  };

  public async connectUser() {
    return new ChatInteraction('NoOne').getRtcInitialized().then((rtc) => {
      rtc.getStreams().then((streams) => {
        this.$refs.local.srcObject = streams.local;
        this.$refs.remote.srcObject = streams.remote;
      });
    });
  }
}
</script>

<style scoped>
video {
  width: 45%;
  outline-width: 1px;
  outline-color: black;
  outline-style: solid;
  margin: 3px;
}
</style>
